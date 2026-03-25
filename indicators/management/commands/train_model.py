import torch
import torch.nn as nn
import optuna
from django.conf import settings
from core.command import BaseCommand


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

        # --- Data loading (placeholder) ---
        # TODO: Load your tensors here, e.g.:
        # X_train, y_train = self.loadData()

        if options['optimize']:
            self.runOptimization()
        else:
            self.runTraining()

        self.stdout.write(self.style.SUCCESS('==> Done'))
        self.processMonitorFinish()

    # -------------------------------------------------------------------------
    # Optuna Optimization
    # -------------------------------------------------------------------------

    def runOptimization(self):
        self.stdout.write(self.style.WARNING('--> Starting Optuna hyperparameter optimization'))

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

        # --- Architecture suggestions ---
        n_layers     = trial.suggest_int('n_layers', 1, 5)
        learning_rate = trial.suggest_float('learning_rate', 1e-5, 1e-2, log=True)
        optimizer_name = trial.suggest_categorical('optimizer', ['Adam', 'RMSprop'])

        # --- Build dynamic nn.Sequential ---
        # TODO: replace in_features with your actual input dimension
        in_features = 64  # placeholder

        layers = []
        for i in range(n_layers):
            out_features = trial.suggest_int(f'layer_{i}_out_features', 16, 256)
            layers.append(nn.Linear(in_features, out_features))
            layers.append(nn.ReLU())
            in_features = out_features

        # TODO: replace final output size (1) with your target dimension
        layers.append(nn.Linear(in_features, 1))
        model = nn.Sequential(*layers)

        # --- Optimizer ---
        optimizer_cls = getattr(torch.optim, optimizer_name)
        optimizer = optimizer_cls(model.parameters(), lr=learning_rate)

        # --- Training loop (placeholder) ---
        # TODO: replace with your DataLoader and real loss function
        # for epoch in range(n_epochs):
        #     optimizer.zero_grad()
        #     output = model(X_train)
        #     loss = loss_fn(output, y_train)
        #     loss.backward()
        #     optimizer.step()

        # TODO: return your actual validation loss
        val_loss = float('inf')  # placeholder
        return val_loss

    # -------------------------------------------------------------------------
    # Standard single-pass training
    # -------------------------------------------------------------------------

    def runTraining(self):
        self.stdout.write(self.style.WARNING('--> Starting standard training pass'))

        # TODO: replace in_features and architecture with your final design
        in_features = 64  # placeholder
        model = nn.Sequential(
            nn.Linear(in_features, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )

        optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

        # TODO: replace with your DataLoader and real loss function
        # for epoch in range(n_epochs):
        #     optimizer.zero_grad()
        #     output = model(X_train)
        #     loss = loss_fn(output, y_train)
        #     loss.backward()
        #     optimizer.step()
        #     self.stdout.write(f'Epoch {epoch} loss: {loss.item():.6f}')

        self.stdout.write(self.style.SUCCESS('--> Training complete'))
