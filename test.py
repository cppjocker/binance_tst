from binance.spot import Spot
from binance.error import  ClientError

import creds

import pandas as pd
import numpy as np

pd.set_option('display.max_columns', 100)

def make_orders(trade_params, verbose=1):
    if trade_params["volume"] <= 0:
        raise Exception("Invalid total volume")

    if trade_params["number"] <= 0:
        raise Exception("Invalid trade orders number")

    if trade_params["priceMin"] <= 0:
        raise Exception("Invalid min price")

    if trade_params["priceMax"] <= 0:
        raise Exception("Invalid max price")

    if trade_params["amountDif"] <= 0:
        raise Exception("Invalid volume diff")

    average_volume = trade_params["volume"] / trade_params["number"]

    if trade_params["amountDif"] > average_volume:
        raise Exception("Too big volume diff")

    if trade_params["volume"] < trade_params["number"]:
        raise Exception("Too many number of orders or too small volume")


    side = trade_params["side"]
    symbol = "BTCUSDT"


    try:
        client = Spot(api_key=creds.api_key,
                        api_secret=creds.api_secret,
                        base_url="https://testnet.binance.vision")

        if verbose:
            info = client.exchange_info()

            sis = info['symbols']
            for si in sis:
                if si['symbol'] == symbol:
                    print(si)

        for i in range( trade_params["number"]):
            print(i)

            if verbose:
                print(client.time())
                order = client.get_orders (symbol)
                print(order)
                balance = client.account()
                print(balance)

            data_exchange_price = client.ticker_price(symbol=symbol)
            exchange_price = data_exchange_price['price']
            print(exchange_price)


            quantity_dollar = np.random.uniform(average_volume - trade_params["amountDif"], average_volume + trade_params["amountDif"], 1)[0]
            print("USDT volume:", quantity_dollar)

            quantity = quantity_dollar / float(exchange_price)
            quantity = float(round(quantity, 6)) #step is 0.000001
            print("BTC volume:", quantity)

            price = np.random.uniform(trade_params["priceMin"], trade_params["priceMax"], 1)[0]
            price = float(round(price, 2)) #step is 0.01
            print("Price:", price)

            order_res = client.new_order(
                symbol=symbol,
                side=side,
                type="LIMIT",
                quantity=quantity,
                price=price,
                timeInForce='GTC')

            if verbose:
                print(order_res)

                balance = client.account()
                print(balance)

                df = pd.DataFrame(client.get_orders(symbol=symbol))
                print(df.loc[:, ['orderId', 'clientOrderId', 'price', 'origQty', 'type', 'executedQty', 'side', 'status'] ] )


    except ClientError as e:
       print(e)
       return


def get_USDT_account(client):
    balance = client.account()
    balances = balance['balances']

    for b in balances:
        if b['asset'] == 'USDT':
            return float(b['free'])



def simple_test():
    client = Spot(api_key=creds.api_key,
                  api_secret=creds.api_secret,
                  base_url="https://testnet.binance.vision")


    account_1 = get_USDT_account(client)

    trade_params = {"volume": 200.0, "number": 10, "amountDif": 0.00001, "side": "SELL", "priceMin": 25000.0, "priceMax": 26000.0}
    make_orders(trade_params, verbose=0)

    account_2 = get_USDT_account(client)

    if (account_1 + 190 > account_2) or (account_1 + 210 < account_2):
        raise Exception("incorrect volume")


    trade_params = {"volume": 200.0, "number": 10, "amountDif": 0.00001, "side": "BUY", "priceMin": 35000.0, "priceMax": 36000.0}
    make_orders(trade_params, verbose=0)

    account_3 = get_USDT_account(client)

    if np.abs(account_3 - account_1) > 10:
        raise Exception("incorrect volume")


if __name__ == "__main__":
    #symbol is BTCUSDT
    simple_test()

    trade_params = {"volume": 100.0, "number": 5, "amountDif": 1.0, "side": "SELL", "priceMin": 25000.0, "priceMax": 26000.0}
    make_orders(trade_params, verbose=0)
