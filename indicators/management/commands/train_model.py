import torch
import torch.nn as nn
import optuna
from django.conf import settings
from core.command import BaseCommand


# -----------------------------------------------------------------------------
# Synthetic data generator (replace with real stock data loading later)
# -----------------------------------------------------------------------------

def get_stock_data(n_samples=500, n_features=5):
    """
    Generate dummy stock data: X is 5 past closing prices, y is next-day price.
    Returns an 80/20 train/validation split.
    """
    torch.manual_seed(42)
    X = torch.randn(n_samples, n_features)
    weights = torch.tensor([0.5, 0.3, 0.1, -0.2, 0.4])
    y = (X @ weights + torch.randn(n_samples) * 0.1).unsqueeze(1)

    split_idx = int(n_samples * 0.8)
    X_train, X_val = X[:split_idx], X[split_idx:]
    y_train, y_val = y[:split_idx], y[split_idx:]
    return X_train, y_train, X_val, y_val


INPUT_DIM = 5   # number of features (past days of closing prices)
N_EPOCHS = 50   # training epochs


class Command(BaseCommand):

    help = 'Train a PyTorch model, optionally with Optuna hyperparameter optimization'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '-t', '--threads',
            type=int,
            default=None,
            required=False,
            help='Limit the number of PyTorch CPU threads'
        )
        parser.add_argument(
            '-o', '--optimize',
            action='store_true',
            default=False,
            help='Run Optuna hyperparameter optimization instead of a single training pass'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(f'==> {self.help}'))
        self.processMonitorStart('train_model', options)

        # --- Thread configuration ---
        if options['threads'] is not None:
            torch.set_num_threads(options['threads'])
            torch.set_num_interop_threads(options['threads'])
            self.stdout.write(self.style.WARNING(f'--> PyTorch threads set to {options["threads"]}'))

        # --- Load data (with train/validation split) ---
        self.X_train, self.y_train, self.X_val, self.y_val = get_stock_data()
        self.stdout.write(
            f'--> Loaded data: train X{list(self.X_train.shape)} y{list(self.y_train.shape)}, '
            f'val X{list(self.X_val.shape)} y{list(self.y_val.shape)}'
        )

        if options['optimize']:
            self.runOptimization()
        else:
            self.runTraining()

        self.stdout.write(self.style.SUCCESS('==> Done'))
        self.processMonitorFinish()

    # -------------------------------------------------------------------------
    # Shared training helper
    # -------------------------------------------------------------------------

    def trainModel(self, model, lr=1e-3, verbose=False):
        """Train a model and return the validation loss."""
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)
        loss_fn = nn.MSELoss()

        model.train()
        for epoch in range(N_EPOCHS):
            optimizer.zero_grad()
            output = model(self.X_train)
            loss = loss_fn(output, self.y_train)
            loss.backward()
            optimizer.step()

            if verbose and (epoch + 1) % 10 == 0:
                self.stdout.write(f'    Epoch {epoch + 1}/{N_EPOCHS}  loss: {loss.item():.6f}')

        model.eval()
        with torch.no_grad():
            val_loss = loss_fn(model(self.X_val), self.y_val).item()
        return val_loss

    # -------------------------------------------------------------------------
    # Optuna Optimization
    # -------------------------------------------------------------------------

    def runOptimization(self):
        self.stdout.write(self.style.WARNING('--> Starting Optuna hyperparameter optimization'))

        # Ensure the optuna schema exists in PostgreSQL
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute('CREATE SCHEMA IF NOT EXISTS optuna')

        storage = optuna.storages.RDBStorage(
            url=settings.OPTUNA_STORAGE,
            engine_kwargs={'connect_args': {'options': '-csearch_path=optuna'}}
        )

        sampler = optuna.samplers.TPESampler(
            multivariate=True,
            constant_liar=True
        )

        study = optuna.create_study(
            study_name='spm_model_study',
            storage=storage,
            sampler=sampler,
            direction='minimize',
            load_if_exists=True
        )

        study.optimize(self.objective, n_trials=50)

        self.stdout.write(self.style.SUCCESS(f'--> Best trial value : {study.best_trial.value}'))
        self.stdout.write(self.style.SUCCESS(f'--> Best params      : {study.best_trial.params}'))

    def objective(self, trial):
        """Optuna objective — builds and trains a dynamic nn.Sequential model."""

        # --- Hyperparameter suggestions ---
        n_layers = trial.suggest_int('n_layers', 1, 5)
        learning_rate = trial.suggest_float('learning_rate', 1e-5, 1e-2, log=True)

        # --- Build dynamic nn.Sequential ---
        layers = []
        in_features = INPUT_DIM
        for i in range(n_layers):
            out_features = trial.suggest_int(f'layer_{i}_units', 16, 128)
            layers.append(nn.Linear(in_features, out_features))
            layers.append(nn.ReLU())
            in_features = out_features
        layers.append(nn.Linear(in_features, 1))
        model = nn.Sequential(*layers)

        return self.trainModel(model, lr=learning_rate)

    # -------------------------------------------------------------------------
    # Standard single-pass training
    # -------------------------------------------------------------------------

    def runTraining(self):
        self.stdout.write(self.style.WARNING('--> Starting standard training pass'))

        model = nn.Sequential(
            nn.Linear(INPUT_DIM, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )

        val_loss = self.trainModel(model, lr=1e-3, verbose=True)
        self.stdout.write(self.style.SUCCESS(f'--> Training complete (val loss: {val_loss:.6f})'))
