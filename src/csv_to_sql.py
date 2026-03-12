import pandas as pd
from sqlalchemy import create_engine
import getpass
import os

def loadDataToDb():
    
    dbName = "SPM_stock_db"
    dbUser = getpass.getuser()
    dbHost = "localhost"
    dbPort = "5432"
    
    connectionString = f"postgresql+psycopg://{dbUser}@{dbHost}:{dbPort}/{dbName}"
    
    try:
        engine = create_engine(connectionString)
        print(f"Connecting to database: {dbName} as user: {dbUser}")
        
        csvFile = "data/raw/spy_data.csv"
        if not os.path.exists(csvFile):
            print(f"Error: File {csvFile} not found.")
            return

        df = pd.read_csv(csvFile)
        
        tableName = "stock_prices"
        df.to_sql(tableName, engine, if_exists='replace', index=False)
        
        print(f"Successfully uploaded {len(df)} rows to {dbName}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    loadDataToDb()
