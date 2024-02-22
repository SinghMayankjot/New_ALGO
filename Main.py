# import Helper_function
import multiprocessing
from ritc import Case, Order, RIT, Security
import Helper_function
from OrderManager import OrderManager
import time
from multiprocessing import Event

shared_position_limit = multiprocessing.Value('i', 25000)

def worker_function(worker_id, rit, condition, condition2):
    orderManager = OrderManager()
    rit = RIT("JIC5LMDR")
    securities_ls = rit.get_securities()
    orders = 0
    current_security = securities_ls[worker_id]["ticker"]
    while rit.get_case().status == Case.Status.ACTIVE:
        security = rit.get_securities(ticker=current_security)[0]
        position = rit.get_securities()[0]["position"]
            
        max_trade_size = 25000
        book = rit.get_securities_book(ticker=current_security)
        # print(book)

        #  
        print(position, max_trade_size)
        my_bids = calculate_order_quantity('Ninja', 'bids',book)
        my_asks = calculate_order_quantity('Ninja', 'asks',book)
        print("my_bids: ",my_bids, " my_asks: ", my_asks)
        if my_bids < 22000 and my_asks > -22000 and -25000 < position < 25000:
            with condition:
                condition.wait()
                print("I'm here", current_security)
                buyPrice = orderManager.getLimitPrice(current_security, "BUY")
                sellPrice = orderManager.getLimitPrice(current_security, "SELL")
                # sentiment = orderManager.determineMarketSentiment ("RITC")
                # print (sentiment)
                # if sellPrice - buyPrice > 0.05 and 0.90 < sentiment < 1.1:
                #     orderManager.sendLimitOrder ("RITC", 3000, "BUY", buyPrice + 0.01)
                #     orderManager.sendLimitOrder ("RITC", 3000, "SELL", buyPrice + 0.01)
                # elif sentiment > 1.5:
                #     orderManager.sendLimitOrder ("RITC", 3000, "BUY", buyPrice + 0.01)
                # elif sentiment < 0.75:
                #     orderManager.sendLimitOrder ("RITC", 3000, "SELL", buyPrice + 0.01)

                centerPrice = (buyPrice + sellPrice) / 2
                try:
                    orderManager.sendLimitOrder(
                        current_security, 3000, "BUY", centerPrice - 0.03
                    )
                    orderManager.sendLimitOrder(
                        current_security, 3000, "SELL", centerPrice + 0.03
                    )
                    print("Made an Order")
                except:
                    print("No worries")
        # marketMakeRITCWithArb(current_security, orderManager, rit, current_security)
        # marketMakeRITCWithSpread(current_security, orderManager, rit, current_security)
    # MIN_SPREAD = 0.07
    # make_market(rit, current_security, MIN_SPREAD)
def notification(rit ,condition,condition2):
    while rit.get_case().status == Case.Status.ACTIVE:  
        with condition:
            position = rit.get_securities()[0]['position']
            print("Position is:", position)
            book = rit.get_securities_book(ticker='ALGO')
            my_bids = calculate_order_quantity('Ninja', 'bids',book)
            my_asks = calculate_order_quantity('Ninja', 'asks',book)
            if my_bids < 25000 and my_asks > -25000:
                # Notify the condition to proceed
                condition.notify()
                #print("Notified condition")                

def main():
    condition = multiprocessing.Condition()
    condition2 = multiprocessing.Condition()
    rit = RIT("JIC5LMDR")
    securities_ls = rit.get_securities()
    print(securities_ls)
    print(rit.get_securities_book(ticker=securities_ls[0]['ticker'], limit=1))
    num_processes = len(securities_ls)  # Number of processes to create
    # Create a list of processes
    processes = []
    for i in range(num_processes):
        process = multiprocessing.Process(target=worker_function, args=(i, rit, condition,condition2))
        processes.append(process)
    
    # Start all the processes
    for process in processes:
        process.start()
    notification(rit, condition,condition2)
    # Wait for all processes to finish
    for process in processes:
        process.join()
    

def marketMakeRITCWithArb(current_security, orderManager, rit, ticker):
    security = rit.get_securities(ticker=ticker)[0]
    position = (
        rit.get_securities()[0]["position"]
        + rit.get_securities()[1]["position"]
        + rit.get_securities()[2]["position"]
    )
    max_trade_size = 25000
    book = rit.get_securities_book(ticker=ticker, limit=1)

    if (
        position
        == (
            rit.get_securities()[0]["position"]
            + rit.get_securities()[1]["position"]
            + rit.get_securities()[2]["position"]
        )
        >= 25000
    ):
        return
    if -25000 < position < 25000:
        buyPrice = orderManager.getLimitPrice(current_security, "BUY")
        sellPrice = orderManager.getLimitPrice(current_security, "SELL")
        # sentiment = orderManager.determineMarketSentiment ("RITC")
        # print (sentiment)
        # if sellPrice - buyPrice > 0.05 and 0.90 < sentiment < 1.1:
        #     orderManager.sendLimitOrder ("RITC", 3000, "BUY", buyPrice + 0.01)
        #     orderManager.sendLimitOrder ("RITC", 3000, "SELL", buyPrice + 0.01)
        # elif sentiment > 1.5:
        #     orderManager.sendLimitOrder ("RITC", 3000, "BUY", buyPrice + 0.01)
        # elif sentiment < 0.75:
        #     orderManager.sendLimitOrder ("RITC", 3000, "SELL", buyPrice + 0.01)

        centerPrice = (buyPrice + sellPrice) / 2
        orderManager.sendLimitOrder(current_security, 3000, "BUY", centerPrice - 0.05)
        orderManager.sendLimitOrder(current_security, 3000, "SELL", centerPrice + 0.05)
        print("Made an Order")
        
def calculate_order_quantity(trader_id, order_side,order_book):
    # Use map and sum to calculate the total order quantity without loops
    total_quantity = sum(map(lambda order: order['quantity'], filter(lambda order: order['trader_id'] == trader_id, order_book[order_side]))) - sum(map(lambda order: order['quantity_filled'], filter(lambda order: order['trader_id'] == trader_id, order_book[order_side])))

    return total_quantity

def marketMakeRITCWithSpread(current_security, orderManager, rit, ticker):
    security = rit.get_securities(ticker=ticker)[0]
    position = (
        rit.get_securities()[0]["position"]
        + rit.get_securities()[1]["position"]
        + rit.get_securities()[2]["position"]
    )
    max_trade_size = 25000
    book = rit.get_securities_book(ticker=ticker, limit=1)

    if (
        position
        == (
            rit.get_securities()[0]["position"]
            + rit.get_securities()[1]["position"]
            + rit.get_securities()[2]["position"]
        )
        >= 25000
    ):
        return
    if -25000 < position < 25000:
        buyPrice = orderManager.getLimitPrice(current_security, "BUY")
        sellPrice = orderManager.getLimitPrice(current_security, "SELL")
        sentiment = orderManager.determineMarketSentiment(current_security)
        if sellPrice - buyPrice > 0.05 and 0.90 < sentiment < 1.1:
            orderManager.sendLimitOrder(current_security, 3000, "BUY", buyPrice + 0.01)
            orderManager.sendLimitOrder(current_security, 3000, "SELL", buyPrice + 0.01)
        elif sentiment > 1.5:
            orderManager.sendLimitOrder(current_security, 3000, "BUY", buyPrice + 0.01)
        elif sentiment < 0.75:
            orderManager.sendLimitOrder(current_security, 3000, "SELL", buyPrice + 0.01)
        print("Made an Order")


def make_market(rit, ticker, MIN_SPREAD):
    while rit.get_case().status == Case.Status.ACTIVE:
        security = rit.get_securities(ticker=ticker)[0]
        position = (
            rit.get_securities()[0]["position"]
            + rit.get_securities()[1]["position"]
            + rit.get_securities()[2]["position"]
        )
        max_trade_size = 1000
        book = rit.get_securities_book(ticker=ticker, limit=1)

        if not book.bids or not book.asks:
            continue
        if (
            position
            == (
                rit.get_securities()[0]["position"]
                + rit.get_securities()[1]["position"]
                + rit.get_securities()[2]["position"]
            )
            >= 25000
        ):
            exit
        bid = book.bids[0].price
        ask = book.asks[0].price
        spread = ask - bid

        if spread < MIN_SPREAD:
            continue

        bid_quantity = min(max_trade_size, max_trade_size - position)
        ask_quantity = min(max_trade_size, max_trade_size + position)
        print(bid_quantity, "    ", ask_quantity)
        time.sleep(5)
        if bid_quantity > 0:
            rit.post_commands_cancel(
                query=f"Ticker='{ticker}' AND Price<{bid} AND Volume>0",
            )

            try:
                rit.post_orders(
                    True,
                    ticker=ticker,
                    type=Order.Type.LIMIT,
                    quantity=bid_quantity,
                    action=Order.Action.BUY,
                    price=bid,
                )
            except HTTPError as error:
                print(format_exc())
                print(error.response.json())
        else:
            rit.post_commands_cancel(query=f"Ticker='{ticker}' AND Volume>0")

        if ask_quantity > 0:
            rit.post_commands_cancel(
                query=f"Ticker='{ticker}' AND Price>{ask} AND Volume<0",
            )

            try:
                rit.post_orders(
                    True,
                    ticker=ticker,
                    type=Order.Type.LIMIT,
                    quantity=ask_quantity,
                    action=Order.Action.SELL,
                    price=ask,
                )
            except HTTPError as error:
                print(format_exc())
                print(error.response.json())
        else:
            rit.post_commands_cancel(query=f"Ticker='{ticker}' AND Volume<0")


if __name__ == "__main__":
    main()
