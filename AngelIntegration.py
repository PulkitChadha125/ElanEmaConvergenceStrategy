import datetime

import pandas as pd
import requests
from SmartApi import SmartConnect #or from SmartApi.smartConnect import SmartConnect
import pyotp
from logzero import logger
import pandas_ta as ta

apikey="qCKtcpLM"
secret="bd933d00-6d62-4d9a-8da7-b05ad6ceb401"
USERNAME="E12404"
PASSWORD="sAMSUNGS6"
totp_string="IPALPKAOF47W3T7LLWQMKLHAKU"
pin = "9626"
smartApi=None


def login(api_key,username,pwd,totp_string):
    global smartApi
    api_key = api_key
    username = username
    pwd = pwd
    smartApi = SmartConnect(api_key)
    try:
        token =totp_string
        totp = pyotp.TOTP(token).now()
    except Exception as e:
        logger.error("Invalid Token: The provided token is not valid.")
        raise e

    correlation_id = "abcde"
    data = smartApi.generateSession(username, pwd, totp)

    if data['status'] == False:
        logger.error(data)

    else:
        authToken = data['data']['jwtToken']

        refreshToken = data['data']['refreshToken']
        feedToken = smartApi.getfeedToken()

        res = smartApi.getProfile(refreshToken)
        smartApi.generateToken(refreshToken)
        res = res['data']['exchanges']
        print(smartApi.getProfile(refreshToken))



def symbolmpping():
    url="https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
    d=requests.get(url).json()
    tokendf=pd.DataFrame.from_dict(d)
    tokendf['expiry']=pd.to_datetime(tokendf['expiry'])
    tokendf=tokendf.astype({'strike':float})
    tokendf.to_csv("Instrument.csv")

def get_historical_data(symbol,token,timeframe,ema1,ema2,ema3,ema4):
    global smartApi
    try:
        historicParam = {
            "exchange": "NFO",
            "symboltoken": token,
            "interval": "ONE_MINUTE",
            "fromdate": "2024-02-08 09:00",
            "todate": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        }
        res= smartApi.getCandleData(historicParam)
        df = pd.DataFrame(res['data'], columns=['date', 'open', 'high', 'low', 'close', 'flag'])
        df['date'] = pd.to_datetime(df['date'])
        df['EMA1']=ta.ema(df['close'],ema1)
        df['EMA2']=ta.ema(df['close'],ema2)
        df['EMA3']=ta.ema(df['close'],ema3)
        df['EMA4']=ta.ema(df['close'],ema4)
        df['smalemadifference']=df['EMA1']-df['EMA2']
        df['longemadifference']=df['EMA3']-df['EMA4']
        df.to_csv(f"{symbol}.csv")

        return df.tail(3)

    except Exception as e:
        logger.exception(f"Historic Api failed: {e}")

def buy(symbol,token,quantity,exchange):
    try:
        orderparams = {
            "variety": "NORMAL",
            "tradingsymbol": symbol,
            "symboltoken": token,
            "transactiontype": "BUY",
            "exchange": exchange,
            "ordertype": "MARKET",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": "0",
            "squareoff": "0",
            "stoploss": "0",
            "quantity": quantity
        }
        # Method 1: Place an order and return the order ID
        orderid = smartApi.placeOrder(orderparams)
        logger.info(f"PlaceOrder : {orderid}")
        # Method 2: Place an order and return the full response
        response = smartApi.placeOrderFullResponse(orderparams)
        logger.info(f"PlaceOrder : {response}")
    except Exception as e:
        logger.exception(f"Order placement failed: {e}")

def sell(symbol,token,quantity,exchange):
    try:
        orderparams = {
            "variety": "NORMAL",
            "tradingsymbol": symbol,
            "symboltoken": token,
            "transactiontype": "SELL",
            "exchange": exchange,
            "ordertype": "MARKET",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": "0",
            "squareoff": "0",
            "stoploss": "0",
            "quantity": quantity
        }
        # Method 1: Place an order and return the order ID
        orderid = smartApi.placeOrder(orderparams)
        logger.info(f"PlaceOrder : {orderid}")
        # Method 2: Place an order and return the full response
        response = smartApi.placeOrderFullResponse(orderparams)
        logger.info(f"PlaceOrder : {response}")
    except Exception as e:
        logger.exception(f"Order placement failed: {e}")

def SHORT(symbol,token,quantity,exchange):
    try:
        orderparams = {
            "variety": "NORMAL",
            "tradingsymbol": symbol,
            "symboltoken": token,
            "transactiontype": "SHORT",
            "exchange": exchange,
            "ordertype": "MARKET",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": "0",
            "squareoff": "0",
            "stoploss": "0",
            "quantity": quantity
        }
        # Method 1: Place an order and return the order ID
        orderid = smartApi.placeOrder(orderparams)
        logger.info(f"PlaceOrder : {orderid}")
        # Method 2: Place an order and return the full response
        response = smartApi.placeOrderFullResponse(orderparams)
        logger.info(f"PlaceOrder : {response}")
    except Exception as e:
        logger.exception(f"Order placement failed: {e}")

def cover(symbol,token,quantity,exchange):
    try:
        orderparams = {
            "variety": "NORMAL",
            "tradingsymbol": symbol,
            "symboltoken": token,
            "transactiontype": "COVER",
            "exchange": exchange,
            "ordertype": "MARKET",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": "0",
            "squareoff": "0",
            "stoploss": "0",
            "quantity": quantity
        }
        # Method 1: Place an order and return the order ID
        orderid = smartApi.placeOrder(orderparams)
        logger.info(f"PlaceOrder : {orderid}")
        # Method 2: Place an order and return the full response
        response = smartApi.placeOrderFullResponse(orderparams)
        logger.info(f"PlaceOrder : {response}")
    except Exception as e:
        logger.exception(f"Order placement failed: {e}")