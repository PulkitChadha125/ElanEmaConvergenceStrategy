import time
import traceback
import pandas as pd
import AngelIntegration
from datetime import datetime, timedelta


def write_to_order_logs(message):
    with open('OrderLog.txt', 'a') as file:  # Open the file in append mode
        file.write(message + '\n')


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
                "entryprice":None,
                "slvalue":None,
                "tpvalue": None,
                'tslstart': None,
                'BUY':False,
                'sell': False,
                'S':False,
                'T':False
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
    if not row.empty:
        token = row.iloc[0]['token']
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
                data= AngelIntegration.get_historical_data(symbol=params['Symbol'],token=token,timeframe=params['TimeFrame'],
                                                           ema1=params['EMA1'],ema2=params['EMA2'],
                                                           ema3=params['EMA3'],ema4=params['EMA4'])
                # smalemadifference,longemadifference
                smalemadifference_current = data.iloc[-2]['smalemadifference']
                smalemadifference_previous = data.iloc[-3]['smalemadifference']
                longemadifference_current = data.iloc[-2]['longemadifference']
                longemadifference_previous = data.iloc[-3]['longemadifference']
                ltp=  data.iloc[-1]['close']

                # buy
                if smalemadifference_current>0 and longemadifference_current <0 and params['BUY'] ==False:
                    if params['sell'] == True:
                        AngelIntegration.cover(symbol=symbol, token=token, quantity=params['lotsize'], exchange="NFO")
                    params['BUY']=True
                    params['sell']=False
                    params['S'] = True
                    params['T'] = True
                    params['slvalue'] = ltp-params['Stoploss']
                    params['tpvalue'] = ltp+params['Target']
                    if params['USETSL'] ==True:
                        params['tslstart'] = ltp+params['Tsl']

                    AngelIntegration.buy(symbol=symbol,token= token,quantity=params['lotsize'],exchange="NFO")
                    orderlog=f"{timestamp} Buy order executed @ {symbol} , @ {ltp}, sl={params['slvalue']},tp={params['tpvalue']}, tsl start={params['tslstart']}"
                    write_to_order_logs(orderlog)
                    print(orderlog)


                # sell
                if smalemadifference_current<0 and longemadifference_current >0 and params['sell'] ==False:
                    if params['BUY'] == True:
                        AngelIntegration.sell(symbol=symbol, token=token, quantity=params['lotsize'], exchange="NFO")

                    params['BUY'] = False
                    params['sell'] = True
                    params['S'] = True
                    params['T'] = True
                    params['slvalue'] = ltp + params['Stoploss']
                    params['tpvalue'] = ltp - params['Target']
                    if params['USETSL'] == True:
                        params['tslstart'] = ltp - params['Tsl']

                    AngelIntegration.SHORT(symbol=symbol, token=token, quantity=params['lotsize'], exchange="NFO")
                    orderlog = f"{timestamp} Short order executed @ {symbol} , @ {ltp}, sl={params['slvalue']},tp={params['tpvalue']}, tsl start={params['tslstart']}"
                    write_to_order_logs(orderlog)
                    print(orderlog)

                # sl and tp

                if params['BUY']==True:
                    if ltp>=params['tpvalue'] and params['tpvalue']>0:
                        params['BUY']=False
                        AngelIntegration.sell(symbol=symbol, token=token, quantity=params['lotsize'], exchange="NFO")
                        orderlog = f"{timestamp} Buy exit  @ {symbol} target executed @ {ltp}"
                        write_to_order_logs(orderlog)
                        print(orderlog)

                    if ltp<=params['slvalue'] and params['slvalue']>0:
                        params['BUY']=False
                        AngelIntegration.sell(symbol=symbol, token=token, quantity=params['lotsize'], exchange="NFO")
                        orderlog = f"{timestamp} Buy exit  @ {symbol} stoploss executed @ {ltp}"
                        write_to_order_logs(orderlog)
                        print(orderlog)

                    if ltp >=params['tslstart'] and params['tslstart']>0 and params['USETSL']==True:
                        params['slvalue']=params['slvalue']+params['Tsl']
                        orderlog = f"{timestamp} TSL level hit buy = {params['tslstart']} new sl = {params['slvalue']} "
                        write_to_order_logs(orderlog)
                        print(orderlog)
                        params['tslstart']=params['tslstart']+params['Tsl']


                if params['sell'] == True:
                    if ltp <= params['tpvalue'] and params['tpvalue'] > 0:
                        params['sell'] = False
                        AngelIntegration.cover(symbol=symbol, token=token, quantity=params['lotsize'], exchange="NFO")
                        orderlog = f"{timestamp} Short exit  @ {symbol} target executed @ {ltp}"
                        write_to_order_logs(orderlog)
                        print(orderlog)

                    if ltp >= params['slvalue'] and params['slvalue'] > 0:
                        params['sell'] = False
                        AngelIntegration.cover(symbol=symbol, token=token, quantity=params['lotsize'], exchange="NFO")
                        orderlog = f"{timestamp} Short exit  @ {symbol} stoploss executed @ {ltp}"
                        write_to_order_logs(orderlog)
                        print(orderlog)

                    if ltp <=params['tslstart'] and params['tslstart']>0 and params['USETSL']==True:
                        params['slvalue']=params['slvalue']-params['Tsl']
                        orderlog = f"{timestamp} TSL level hit sell = {params['tslstart']} new sl = {params['slvalue']} "
                        write_to_order_logs(orderlog)
                        print(orderlog)
                        params['tslstart']=params['tslstart']-params['Tsl']

                # buyexit
                if longemadifference_current>0 and params['BUY']==True:
                    params['BUY']=False
                    params['slvalue']=0
                    params['tpvalue']=0
                    params['tslstart'] = 0
                    AngelIntegration.sell(symbol=symbol, token=token, quantity=params['lotsize'], exchange="NFO")
                    orderlog = f"{timestamp} Buy exit  @ {symbol} long ema turnd positive: {longemadifference_current}"
                    write_to_order_logs(orderlog)
                    print(orderlog)
                # sell exit
                if longemadifference_current > 0 and params['sell'] == True:
                    params['sell'] = False
                    params['slvalue'] = 0
                    params['tpvalue'] = 0
                    params['tslstart']=0
                    AngelIntegration.cover(symbol=symbol, token=token, quantity=params['lotsize'], exchange="NFO")
                    orderlog = f"{timestamp} Short exit  @ {symbol} long ema turnd negative: {longemadifference_current}"
                    write_to_order_logs(orderlog)
                    print(orderlog)


    except Exception as e:
        print("Error happened in Main strategy loop: ", str(e))
        traceback.print_exc()



while True:
    main_strategy()
    time.sleep(1)

