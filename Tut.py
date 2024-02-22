import signal
import requests
import time
import sys

class ApiException(Exception):
    pass

def signal_handler(signum, frame):
    global shutdown
    signal.signal(signal.SIGINT,signal.SIG_DFL)
    shutdown = True
    
API_KEY = {'X-API-Key':'3PAFQ3IA'}
shutdown = False

SPEEDBUMP = 0.1
MAX_VOLUME = 5000
MAX_ORDERS = 5
SPREAD = 0.05

def get_tick(session):
    resp = session.get('http://localhost:9999/v1/case')
    if resp.ok:
        case = resp.json()
        return case['tick']
    raise ApiException('Authorization error. Please check API key.')


def ticker_bid_ask(session, ticker):
    payload = {'ticker': ticker}
    resp = session.get('http://localhost:9999/v1/securities/book', params = payload)
    if resp.ok:
        book = resp.json()
        return book['bids'][0]['price'], book['asks'][0]['price']
    raise ApiException('Authorization error. Please check API key.')

def open_sells(session):
    resp = session.get('http://localhost:9999/v1/orders?status=OPEN')
    if resp.ok:
        open_sells_volume = 0 # total combined volumes of all open calls
        ids = []              # all open sell ids 
        prices = []           # all open sell prices
        order_volumes = []    # all open sell volumes
        volumes_filled = []   # volume filled for each open sell order
        
        open_orders = resp.json()
        for order in open_orders:
            if order['action'] == 'SELL':
                volumes_filled.append(order['quantity_filled'])
                order_volumes.append(order['quantity'])
                open_sells_volume = open_sells_volume + order['quantity']
                prices.append(order['price'])
                ids.append(order['order_id'])
    return volumes_filled, open_sells_volume, ids, prices, order_volumes

def open_buys(session):
    resp = session.get('http://localhost:9999/v1/orders?status=OPEN')
    if resp.ok:
        open_buys_volume = 0 # total combined volumes of all open calls
        ids = []              # all open buy ids 
        prices = []           # all open buy prices
        order_volumes = []    # all open buy volumes
        volumes_filled = []   # volume filled for each open buy order
        
        open_orders = resp.json()
        for order in open_orders:
            if order['action'] == 'BUY':
                volumes_filled.append(order['quantity_filled'])
                order_volumes.append(order['quantity'])
                open_buys_volume = open_buys_volume + order['quantity']
                prices.append(order['price'])
                ids.append(order['order_id'])
    return volumes_filled, open_buys_volume, ids, prices, order_volumes             

def buy_sell(session, sell_price, buy_price):
    for i in range(MAX_ORDERS):
        session.post('http://localhost:9999/v1/orders', params = {'ticker':'CNR', 'type':'LIMIT', 'quantity': MAX_VOLUME,'price': sell_price, 'action': 'SELL'})
        session.post('http://localhost:9999/v1/orders', params = {'ticker':'CNR', 'type':'LIMIT', 'quantity': MAX_VOLUME,'price': sell_price, 'action': 'BUY'})


def re_order(session, number_of_orders, ids, volumes_filled, volumes, price, action):
    for i in range(number_of_orders):
        id = ids[i]
        volume = volumes[i]
        volume_filled = volumes_filled[i]
        if volume_filled != 0 :
            volume = MAX_VOLUME - volume_filled
            
        deleted = session.delete('http://localhost:9999/v1/orders/{}'.format(id))
        if deleted.ok:
            session.post('http://localhost:9999/v1/orders', params = {'ticker':'CNR', 'type':'LIMIT', 'quantity': volume,'price': price, 'action': action})

            
def main():
    buy_ids = []
    buy_prices = []
    buy_volumes = []
    volume_filled_buys = []
    open_buys_volume = 0
    
    sell_ids = []
    sell_prices = []
    sell_volumes = []
    volume_filled_sells = []
    open_sells_volume = 0
    
    single_side_filled = False
    single_side_transaction_time = 0
    
    with requests.Session() as s:
        s.headers.update(API_KEY)
        tick = get_tick(s)
        
        while tick > 5 and tick < 295 and not shutdown:
            volume_filled_sells, open_sells_volume, sell_ids, sell_prices, sell_volumes = open_sells(s)
            volume_filled_buys, open_buys_volume, buy_ids, buy_prices, buy_volumes = open_buys(s)
            bid_price, ask_price = ticker_bid_ask(s,'CNR')
            
            if(open_sells_volume == 0 and open_buys_volume == 0):
                single_side_filled = False
                bid_ask_spread = ask_price - bid_price
                sell_price = ask_price
                buy_price = bid_price
                
                if(bid_ask_spread >= SPREAD):
                    buy_sell(s, sell_price, buy_price)
                    time.sleep(SPEEDBUMP)
            else:
                if (not single_side_filled and (open_buys_volume == 0 or open_sells_volume == 0)):
                    single_side_filled = True
                    single_side_transaction_time = tick
                    
                if(open_sells_volume == 0):
                    if(buy_price == bid_price):
                        continue
                    
                    elif(tick -single_side_transaction_time >=3):
                        next_buy_price = bid_price + 0.01
                        potential_profit = sell_price - next_buy_price - 0.02
                        
                        if(potential_profit >= 0.1 or tick - single_side_transaction_time >=6):
                            action = 'BUY'
                            number_of_orders = len(buy_ids)
                            buy_price = bid_price + 0.1
                            price = buy_price
                            ids = buy_ids
                            volumes = buy_volumes
                            volumes_filled = volume_filled_buys
                            
                            re_order(s, number_of_orders, ids, volumes_filled, volumes, price, action)
                            time.sleep(SPEEDBUMP)
                            
                elif(open_buys_volume == 0):
                    if(sell_price == ask_price):
                        continue
                    
                    elif(tick - single_side_transaction_time >= 3):
                        next_sell_price = ask_price - 0.01
                        potential_profit = next_sell_price - buy_price - 0.02
                        
                        if(potential_profit >= 0.01 or tick - single_side_transaction_time >=6):
                            action = 'SELL'
                            number_of_orders = len(sell_ids)
                            sell_price = ask_price - 0.01
                            price = sell_price
                            ids = sell_ids
                            volumes = sell_volumes
                            volumes_filled = volume_filled_sells
                            
                            re_order(s, number_of_orders, ids, volumes_filled, volumes, price, action)
                            time.sleep(SPEEDBUMP)            
                                    
            tick = get_tick(s)
            
if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    main()
                                        