import pandas as pd
from sqlalchemy import create_engine, text
import getpass

def verifyDbContent():
    
    dbName = "SPM_stock_db"
    dbUser = getpass.getuser()
    dbHost = "localhost"
    dbPort = "5432"
    
    connectionString = f"postgresql+psycopg://{dbUser}@{dbHost}:{dbPort}/{dbName}"
    
    try:
        engine = create_engine(connectionString)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT COUNT(*) FROM stock_prices"))
            count = result.scalar()
            print(f"Total rows in 'stock_prices': {count}")
            
            print("\nFirst 5 rows:")
            df = pd.read_sql("SELECT * FROM stock_prices LIMIT 5", connection)
            print(df)
            
    except Exception as e:
        print(f"Verification failed: {e}")

if __name__ == "__main__":
    verifyDbContent()
