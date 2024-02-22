import signal
import requests
from time import sleep
import pandas as pd
import numpy as np
from re import findall # needed to parse news

global df_news
global tick
global rf
global Alpha_B
global Gamma_B
global Theta_B
global Target_tick
global Target_price
global news_tick

API_KEY = {'X-API-Key': 'MCKGCURR'}  # API key from RIT Client
shutdown = False  

# class that passes error message, ends the program
class ApiException(Exception):
    pass

# code that lets us shut down if CTRL C is pressed
def signal_handler(signum, frame):
    global shutdown
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    shutdown = True

# Gets the current tick
def get_tick(session):
    global tick

    resp = session.get('http://localhost:9999/v1/case')
    if resp.ok:
        tick = resp.json()['tick']
        return tick
    
    raise ApiException('fail - cant get tick')

# sends a market order to API
def sendMarketOrder(session, ticker, quantity, direction):
    # Sends a market order for a specific ticker
    mkt_order_params = {'ticker': ticker,
                        'type': 'MARKET',
                        'quantity': quantity,
                        'action': direction}
    resp = session.post('http://localhost:9999/v1/orders', params=mkt_order_params)
    if resp.ok:
        return
    elif resp.status_code == 429:
        wait_time = resp.json()['wait']
        sleep(wait_time)
        session.post('http://localhost:9999/v1/orders', params=mkt_order_params)
    else:
        print(resp.json())
    return

# Sends a limit order to API
def sendLimitOrder(session, ticker, quantity, direction, price):
    mkt_order_params = {'ticker': ticker,
                        'type': "LIMIT",
                        'quantity': quantity,
                        'action': direction,
                        'price': price}
    resp = session.post('http://localhost:9999/v1/orders', params=mkt_order_params)
    if resp.ok:
        return resp.json()['order_id']
    elif resp.status_code == 429:
        wait_time = resp.json()['wait']
        sleep(wait_time)
        return sendLimitOrder(session, ticker, quantity, direction, price)
    else:
        print(resp.json())
    return

# Orders transactions by max trade size
def sendMaxOrders(session, ticker, quantity, direction, max):
    pos_new = []
    quantity = int(quantity)
    if abs(quantity) > max:
        q = abs(quantity) // max
        for j in range(q):
            position = max * np.sign(quantity)
            pos_new.append(position)

        r = quantity - max * q * np.sign(quantity)
        if r != 0:
            pos_new.append(r)
    else:
        pos_new.append(quantity)
    
    while len(pos_new) != 0:
        ST_pos = pos_new[0]
        sendMarketOrder(session, ticker, ST_pos, direction)
        pos_new.pop(0)

        if len(pos_new) == 0:
            break
    return

# Parses all news items and extracts numbers/sentiment
def get_news(session):
    global df_news

    # queries the all news
    df = session.get(f"http://localhost:9999/v1/news").json()
    df = pd.DataFrame(df)

    # Checks to send back old news df if no new news
    if len(df_news) == len(df):
        return
    
    # Target Tick
    df['filter'] = df['headline'].apply(lambda x: 1 if "Private Information" in x else " ")
    df['Target_tick'] = np.where(df['filter'] == 1, df['body'], None)
    df['Target_tick'] = df['Target_tick'].apply(lambda x: findall('\d+', x) if x != None else [" "])
    df['Target_tick'] = df['Target_tick'].str[0]
    df['Target_tick'] = df['Target_tick'].apply(lambda x: int(x) if x != " " else np.nan)

    # Target Price
    df['filter'] = df['headline'].apply(lambda x: 1 if "Private Information" in x else " ")
    df['Target_price'] = np.where(df['filter'] == 1, df['body'], None)
    df['Target_price'] = df['Target_price'].apply(lambda x: x.replace(",", "") if x != None else x)
    df['Target_price'] = df['Target_price'].apply(lambda x: findall('\d+\.\d+', x) if x != None else [np.nan])
    df['Target_price'] = df['Target_price'].str[0]
    df['Target_price'] = df['Target_price'].apply(lambda x: float(x))

    # Starting rf information
    df['filter'] = df['body'].apply(lambda x: x if "bond" in x.lower() else None)
    df['rf'] = df['filter'].apply(lambda x: findall('\d+(\.\d+)?%', x) if x != None else [np.nan])
    df['rf'] = df['rf'].str[0]
    df['rf'] = df['rf'].apply(lambda x: np.nan if type(x) == float else float(x.strip('%')) / 100)

    # Starting Alpha beta
    df['Beta_helper'] = df['filter'].apply(lambda x: findall('\d+\.\d+', x) if x != None else [np.nan,np.nan,np.nan,np.nan])
    df['B_Alpha'] = df['Beta_helper'].str[1]
    df['B_Alpha'] = df['B_Alpha'].apply(lambda x: float(x))
    df['B_Gamma'] = df['Beta_helper'].str[2]
    df['B_Gamma'] = df['B_Gamma'].apply(lambda x: float(x))
    df['B_Theta'] = df['Beta_helper'].str[3]
    df['B_Theta'] = df['B_Theta'].apply(lambda x: float(x))

    df.drop(columns=['period', 'news_id', 'headline', 'body', 'ticker', 'filter', 'Beta_helper'], inplace=True)

    get_latest_news_parse(df)

    df_news = df

    return

# Updates global variables
def get_latest_news_parse(df_news):
    global rf
    global Alpha_B
    global Gamma_B
    global Theta_B
    global Target_tick
    global Target_price
    global news_tick
 
    rf_col = df_news['rf']
    i = rf_col.first_valid_index()
    rf = float(rf_col.loc[i])

    B_Alpha_col = df_news['B_Alpha']
    i = B_Alpha_col.first_valid_index()
    Alpha_B = float(B_Alpha_col.loc[i])

    B_Gamma_col = df_news['B_Gamma']
    i = B_Gamma_col.first_valid_index()
    Gamma_B = float(B_Gamma_col.loc[i])

    B_Theta_col = df_news['B_Theta']
    i = B_Theta_col.first_valid_index()
    Theta_B = float(B_Theta_col.loc[i])

    news_tick = df_news.loc[0, 'tick']

    Target_tick_col = df_news['Target_tick']
    i = Target_tick_col.first_valid_index()
    if i != None:
        Target_tick = float(Target_tick_col.loc[i])
    else:
        Target_tick = 0

    Target_price_col = df_news['Target_price']
    i = Target_price_col.first_valid_index()
    if i != None:
        Target_price = float(Target_price_col.loc[i])
    else:
        Target_price = 0
    
    
    return

# Gets the last prices for all securities
def get_last_prices(session):
    resp = session.get('http://localhost:9999/v1/securities/history?ticker=ALPHA&limit=2')
    if resp.ok:
        resp = resp.json()[1]
        Alpha_last = resp['close']
        tick = resp['tick']
    resp = session.get('http://localhost:9999/v1/securities/history?ticker=RITM&limit=2')
    if resp.ok:
        Ritm_last = resp.json()[1]['close']
    resp = session.get('http://localhost:9999/v1/securities/history?ticker=GAMMA&limit=2')
    if resp.ok:
        Gamma_last = resp.json()[1]['close']
    resp = session.get('http://localhost:9999/v1/securities/history?ticker=THETA&limit=2')
    if resp.ok:
        Theta_last = resp.json()[1]['close']
    return tick, Ritm_last, Alpha_last, Gamma_last, Theta_last

# Gets the max ticker given CAPM dollar values
def get_max_capm_ticker(Capm_A, Capm_G, Capm_T):
    Capm_list = [Capm_A, Capm_G, Capm_T]

    max_val = max(Capm_list, key=abs)
    max_id = Capm_list.index(max_val)

    if max_id == 0:
        max_ticker = "ALPHA"
    elif max_id == 1:
        max_ticker = "GAMMA"
    elif max_id == 2:
        max_ticker = "THETA"

    return max_ticker, max_val, max_id

# Gets the minimum ticker given CAPM dollar values:
def get_min_capm_ticker(Capm_A, Capm_G, Capm_T, max_val):
    Capm_list = [Capm_A, Capm_G, Capm_T]
    diff_list = [x - max_val for x in Capm_list]

    min_val = max(diff_list, key=abs)
    min_id = diff_list.index(min_val)

    if min_id == 0:
        min_ticker = "ALPHA"
    elif min_id == 1:
        min_ticker = "GAMMA"
    elif min_id == 2:
        min_ticker = "THETA"

    return min_ticker#, min_val

# Gets the current trader position
def get_pos(session):
    # queries API for tickers of positions and last traded price by ticker
    df = session.get(f"http://localhost:9999/v1/securities").json()
    df = pd.DataFrame(df)
    df = df[['ticker', 'position', 'last']]
    return df

# Closes positions
def closeAll(session, df_pos):
    df_pos = df_pos[(df_pos['position'] != 0.0)]
    if df_pos.empty:
        return
    
    pos = df_pos['position'].to_list()
    tickers = df_pos['ticker'].to_list()
    pos_new = []
    ticker_new = []
    i = 0
    for item in pos:
        item = int(item)
        if abs(item) > 10000:
            q = abs(item) // 10000
            for j in range(q):
                position = 10000 * np.sign(item)
                pos_new.append(position)
                ticker_new.append(tickers[i])

            r = item - 10000 * q * np.sign(item)
            if r != 0:
                pos_new.append(r)
                ticker_new.append(tickers[i])
        else:
            pos_new.append(item)
            ticker_new.append(tickers[i])
        i += 1

    pos_new, ticker_new = zip(*sorted(zip(pos_new, ticker_new)))

    pos_new = list(pos_new)
    ticker_new = list(ticker_new)

    for h in range(len(pos_new)):
        sendMarketOrder(session, ticker_new[i], pos_new[i], "SELL")

    return

# Calculate Beta and Capm
def calculate_beta(df, Ritm_last, Alpha_last, Gamma_last, Theta_last):
    E_r = (Target_price - Ritm_last) / Ritm_last - rf
    Beta_A = df['Alpha_pct'].cov(df['Ritm_pct']) / df['Ritm_pct'].var()
    Beta_G = df['Gamma_pct'].cov(df['Ritm_pct']) / df['Ritm_pct'].var()
    Beta_T = df['Theta_pct'].cov(df['Ritm_pct']) / df['Ritm_pct'].var()

    Capm_A = (rf + Beta_A * E_r) * Alpha_last
    Capm_G = (rf + Beta_G * E_r) * Gamma_last
    Capm_T = (rf + Beta_T * E_r) * Theta_last

    Target_A = Capm_A + Alpha_last
    Target_G = Capm_G + Gamma_last
    Target_T = Capm_T + Theta_last

    Target_prices = [Target_A, Target_G, Target_T]
    max_ticker, max_val, target_index = get_max_capm_ticker(Capm_A, Capm_G, Capm_T)
    target_max_price = Target_prices[target_index]

    min_ticker = get_min_capm_ticker(Capm_A, Capm_G, Capm_T, max_val)

    return max_ticker, target_max_price, max_val, min_ticker

def main():
    global tick
    global df_news
    global orders

    # Opening session
    session = requests.Session()
    session.headers.update(API_KEY)

    # Initializing variables needed throughout loop
    tick = get_tick(session)
    df_news = pd.DataFrame()
    orders = []
    SENT_ORDERS = False
    df = pd.DataFrame(columns = ['tick', 'Ritm_L', 'Alpha_L', 'Gamma_L', 'Theta_L'])
    L_tick, Ritm_last, Alpha_last, Gamma_last, Theta_last = get_last_prices(session)
    df.loc[0] = {'tick':L_tick, 'Ritm_L':Ritm_last, 'Alpha_L':Alpha_last, 'Gamma_L':Gamma_last, 'Theta_L':Theta_last}

    while tick < 599 and not shutdown:
        # print(f"tick:{tick}, Sent_orders:{SENT_ORDERS}")
        tick = get_tick(session)
        get_news(session)

        L_tick, Ritm_last, Alpha_last, Gamma_last, Theta_last = get_last_prices(session)
        if df['tick'].iloc[-1] != L_tick:
            df.loc[len(df)] = {'tick':L_tick, 'Ritm_L':Ritm_last, 'Alpha_L':Alpha_last, 'Gamma_L':Gamma_last, 'Theta_L':Theta_last}
            df['Ritm_pct'] = df['Ritm_L'].pct_change()
            df['Alpha_pct'] = df['Alpha_L'].pct_change()
            df['Gamma_pct'] = df['Gamma_L'].pct_change()
            df['Theta_pct'] = df['Theta_L'].pct_change()
            inplace_var = False
            if len(df) >= 30:
                inplace_var = True
            df.drop([0], inplace=inplace_var)
            df.reset_index(inplace=True, drop=True)

        if (tick > (Target_tick + 5)):
            SENT_ORDERS = False
            Ritm_max = Ritm_last
            Ritm_min = Ritm_last
            # Checking for closeout
            df_pos = get_pos(session)
            df_pos = df_pos[(df_pos['position'] != 0.0)]
            if len(df_pos) == 0:
                continue
            else:
                session.post("http://localhost:9999/v1/commands/cancel?all=1")
                for row in df_pos.iterrows():
                    ticker = row[1]['ticker']
                    quantity = row[1]['position']
                    sendMaxOrders(session, ticker, quantity, "SELL", 10000)
                sleep(0.5)

        if (tick <= Target_tick) and SENT_ORDERS == False:
            max_ticker, target_max_price, max_val, min_ticker = calculate_beta(df, Ritm_last, Alpha_last, Gamma_last, Theta_last)
            print(f"Max Ticker: {max_ticker}, Max_Val: {max_val}")
            if abs(max_val) > 1:

                for a in range(6):
                    sendMarketOrder(session, max_ticker, 10000 * np.sign(max_val), "BUY")
                    id = sendLimitOrder(session, max_ticker, 10000 * np.sign(max_val), "SELL", target_max_price)
                    orders.append(id)
                    # sendMarketOrder(session, min_ticker, 10000 * np.sign(max_val), "SELL")
                # sendMarketOrder(session, min_ticker, 10000 * np.sign(max_val), "SELL")
                SENT_ORDERS = True

        elif (tick <= Target_tick):
            max_ticker, target_max_price, max_val, min_ticker = calculate_beta(df, Ritm_last, Alpha_last, Gamma_last, Theta_last)
            if abs(max_val) > 1:
                # sendMarketOrder(session, min_ticker, 5000 * np.sign(max_val), "SELL")
                sendMarketOrder(session, max_ticker, 5000 * np.sign(max_val), "BUY")
                id = sendLimitOrder(session, max_ticker, 5000 * np.sign(max_val), "SELL", target_max_price)
                orders.append(id)
                sleep(0.1)
            
        if tick <= (Target_tick + 5):
            E_r = (Target_price - Ritm_last) / Ritm_last - rf
            Beta_A = df['Alpha_pct'].cov(df['Ritm_pct']) / df['Ritm_pct'].var()
            Beta_G = df['Gamma_pct'].cov(df['Ritm_pct']) / df['Ritm_pct'].var()
            Beta_T = df['Theta_pct'].cov(df['Ritm_pct']) / df['Ritm_pct'].var()

            Capm_A = (rf + Beta_A * E_r) * Alpha_last
            Capm_G = (rf + Beta_G * E_r) * Gamma_last
            Capm_T = (rf + Beta_T * E_r) * Theta_last

            Target_A = Capm_A + Alpha_last
            Target_G = Capm_G + Gamma_last
            Target_T = Capm_T + Theta_last
            new_orders = []
            for id in orders:
                resp = session.get(f"http://localhost:9999/v1/orders/{id}")
                if resp.ok:
                    resp = resp.json()
                    if resp['quantity_filled'] == 0.0:
                        ticker = resp['ticker']
                        action = resp['action']
                        quantity = resp['quantity']
                        if ticker == "ALPHA":
                            price = Target_A
                        elif ticker == "GAMMA":
                            price = Target_G
                        else:
                            price = Target_T
                        new_id = sendLimitOrder(session, ticker, quantity, action, price)
                        new_orders.append(new_id)
                        session.delete(f"http://localhost:9999/v1/orders/{id}")

            orders = new_orders

        tick = get_tick(session)

if __name__ == '__main__':
    main()