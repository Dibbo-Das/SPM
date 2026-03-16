# SPM: NVIDIA Stock Price Prediction

This repository contains the data pipeline and machine learning architecture for predicting NVIDIA (NVDA) stock prices. The project is built on a Django foundation to utilize its powerful management commands and database routing, while relying on custom psycopg (v3) utilities for high-performance PostgreSQL batch insertions.

## Local Environment Setup

To get this project running on your local machine, follow these exact steps:

### 1. Clone & Install Dependencies
Ensure you have your Python virtual environment activated, then install the required packages:
```
pip install -r requirements.txt
```

### 2. Database Setup
Ensure you have PostgreSQL installed and running on your local machine.
Create a new local database named SPM. You can do this via DBeaver, pgAdmin, or the psql CLI:
```sql
CREATE DATABASE "SPM";
```

### 3. Local Credentials (Crucial Step)
**DO NOT edit the main `spm/settings.py` file with your database password.**
Instead, create a hidden local file that Git will ignore.
1. Create a new file at `spm/settings_local.py`.
2. Add your personal database credentials to it:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'SPM',
        'USER': 'your_local_postgres_username',
        'PASSWORD': 'your_local_postgres_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'pool': True,
        },
    }
}
```

### 4. Running the Pipeline
Once your database is set up and Paul has finished the extraction logic, you can pull the latest stock data into your local database by running our custom management command:
```
python manage.py yfinance_prices
```

## Architecture Overview
* `core/`: Contains foundational utilities like `DbExtra` for standardized database interactions.
* `importer/`: Contains the API wrappers (`yfinance_api.py`) and Django management commands to pull and store data.
* `notebooks/`: Dedicated workspace for Mustafa's ML model training and Jupyter notebooks.
* `spm/`: The core Django configuration folder.
