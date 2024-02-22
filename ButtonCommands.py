from __future__ import division

from OrderManager import OrderManager

orderManager = OrderManager()


def marketBuyRITC():
    price = orderManager.getLimitPrice ("RITC", "SELL")
    orderManager.sendLimitOrder ("RITC", 5000, "BUY", price + 0.01)


def marketSellRITC():
    price = orderManager.getLimitPrice ("RITC", "BUY")
    orderManager.sendLimitOrder ("RITC", 5000, "SELL", price - 0.01)


def limitBuyRITC():
    # get the current highest bid and beat it by 1 cent
    price = orderManager.getLimitPrice ("RITC", "BUY")
    orderManager.sendLimitOrder ("RITC", 5000, "BUY", price + 0.01)


def limitSellRITC():
    # get the current highest bid and beat it by 1 cent
    price = orderManager.getLimitPrice ("RITC", "SELL")
    orderManager.sendLimitOrder ("RITC", 5000, "SELL", price - 0.01)


def closeRITC():
    orderManager.closePosition ("RITC")


def killAllRITCOrders():
    orderManager.killAllOrders ("RITC")


def marketMakeRITCWithArb():
    buyPrice = orderManager.getLimitPrice ("AC", "BUY")
    sellPrice = orderManager.getLimitPrice ("AC", "SELL")
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
    orderManager.sendLimitOrder ("RITC", 3000, "AC", centerPrice - 0.05)
    orderManager.sendLimitOrder ("RITC", 3000, "AC", centerPrice + 0.05)


def marketMakeRITCWithSpread():
    buyPrice = orderManager.getLimitPrice ("RITC", "BUY")
    sellPrice = orderManager.getLimitPrice ("RITC", "SELL")
    sentiment = orderManager.determineMarketSentiment("RITC")
    print (sentiment)
    if sellPrice - buyPrice > 0.05 and 0.90 < sentiment < 1.1:
        orderManager.sendLimitOrder("RITC", 3000, "BUY", buyPrice + 0.01)
        orderManager.sendLimitOrder("RITC", 3000, "SELL", buyPrice + 0.01)
    elif sentiment > 1.5:
        orderManager.sendLimitOrder("RITC", 3000, "BUY", buyPrice + 0.01)
    elif sentiment < 0.75:
        orderManager.sendLimitOrder("RITC", 3000, "SELL", buyPrice + 0.01)


def marketBuyBULL():
    price = orderManager.getLimitPrice ("BULL", "SELL")
    orderManager.sendLimitOrder ("BULL", 3000, "BUY", price + 0.01)


def marketSellBULL ():
    price = orderManager.getLimitPrice("BULL", "BUY")
    orderManager.sendLimitOrder("BULL", 3000, "SELL", price - 0.01)


def limitBuyBULL():
    # get the current highest bid and beat it by 1 cent
    price = orderManager.getLimitPrice("BULL", "BUY")
    orderManager.sendLimitOrder("BULL", 3000, "BUY", price + 0.01)


def limitSellBULL():
    # get the current highest bid and beat it by 1 cent
    price = orderManager.getLimitPrice ("BULL", "SELL")
    orderManager.sendLimitOrder ("BULL", 3000, "SELL", price - 0.01)


def closeBULL():
    orderManager.closePosition ("BULL")


def killAllBULLOrders():
    orderManager.killAllOrders ("BULL")


def marketBuyBEAR():
    price = orderManager.getLimitPrice ("BEAR", "SELL")
    orderManager.sendLimitOrder ("BEAR", 3000, "BUY", price + 0.01)


def marketSellBEAR ():
    price = orderManager.getLimitPrice ("BEAR", "BUY")
    orderManager.sendLimitOrder ("BEAR", 3000, "SELL", price - 0.01)


def limitBuyBEAR ():
    # get the current highest bid and beat it by 1 cent
    price = orderManager.getLimitPrice ("BEAR", "BUY")
    orderManager.sendLimitOrder ("BEAR", 3000, "BUY", price + 0.01)


def limitSellBEAR ():
    # get the current highest bid and beat it by 1 cent
    price = orderManager.getLimitPrice ("BEAR", "SELL")
    orderManager.sendLimitOrder ("BEAR", 3000, "SELL", price - 0.01)


def closeBEAR ():
    orderManager.closePosition ("BEAR")


def killAllBEAROrders ():
    orderManager.killAllOrders ("BEAR")


def closeUSD ():
    orderManager.closePosition ("USD")


def buyUSD ():
    orderManager.sendMarketOrder ("USD", "MARKET", 1000000, "BUY")


def sellUSD ():
    orderManager.sendMarketOrder ("USD", "MARKET", 1000000, "SELL")
