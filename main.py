import time
import traceback

import pandas as pd
import AngelIntegration
from datetime import datetime, timedelta

def delete_file_contents(file_name):
    try:
        # Open the file in write mode, which truncates it (deletes contents)
        with open(file_name, 'w') as file:
            file.truncate(0)
        print(f"Contents of {file_name} have been deleted.")
    except FileNotFoundError:
        print(f"File {file_name} not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

result_dict={}
def get_user_settings():
    global result_dict
    try:
        csv_path = 'TradeSettings.csv'
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        result_dict = {}
        # Symbol,EMA1,EMA2,EMA3,EMA4,lotsize,Stoploss,Target,Tsl
        for index, row in df.iterrows():
            # Create a nested dictionary for each symbol
            symbol_dict = {
                'Symbol': row['Symbol'],
                'TimeFrame':row['TimeFrame'],
                'EMA1': row['EMA1'],
                'EMA2': row['EMA2'],
                'EMA3': row['EMA3'],
                'EMA4': float(row['EMA4']),
                "lotsize": float(row['lotsize']),
                "Stoploss": float(row['Stoploss']),
                "Target": float(row['Target']),
                "Tsl": float(row['Tsl']),
            }
            result_dict[row['Symbol']] = symbol_dict
        print("result_dict: ", result_dict)
    except Exception as e:
        print("Error happened in fetching symbol", str(e))

def get_api_credentials():
    credentials = {}
    delete_file_contents("OrderLogs.txt")
    try:
        df = pd.read_csv('Credentials.csv')
        for index, row in df.iterrows():
            title = row['Title']
            value = row['Value']
            credentials[title] = value
    except pd.errors.EmptyDataError:
        print("The CSV file is empty or has no data.")
    except FileNotFoundError:
        print("The CSV file was not found.")
    except Exception as e:
        print("An error occurred while reading the CSV file:", str(e))

    return credentials

get_user_settings()
credentials_dict = get_api_credentials()
api_key=credentials_dict.get('apikey')
username=credentials_dict.get('USERNAME')
pwd=credentials_dict.get('pin')
totp_string=credentials_dict.get('totp_string')
AngelIntegration.login(api_key=api_key,username=username,pwd=pwd,totp_string=totp_string)

def get_token(symbol):
    df= pd.read_csv("Instrument.csv")
    row = df.loc[df['symbol'] == symbol]

    # If the row is not empty, return the corresponding token value
    if not row.empty:
        token = row.iloc[0]['token']  # Assuming 'token' is the column containing the token values
        return token



def main_strategy():
    global result_dict

    try:
        for symbol, params in result_dict.items():
            symbol_value = params['Symbol']
            timestamp = datetime.now()
            timestamp = timestamp.strftime("%d/%m/%Y %H:%M:%S")
            if isinstance(symbol_value, str):
                token=get_token(symbol=params['Symbol'])
                print("token",token)
                data= AngelIntegration.get_historical_data(symbol=params['Symbol'],token=token,timeframe=params['TimeFrame'],
                                                           ema1=params['EMA1'],ema2=params['EMA2'],
                                                           ema3=params['EMA3'],ema4=params['EMA4'])

                EMA1_current = data.iloc[-2]['EMA1']
                EMA1_previous = data.iloc[-3]['EMA1']

                print(data)






    except Exception as e:
        print("Error happened in Main strategy loop: ", str(e))
        traceback.print_exc()



while True:
    main_strategy()
    time.sleep(1)

