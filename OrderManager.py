from __future__ import division

import requests
import time


class OrderManager:
    API_KEY = {"X-API-key": "JIC5LMDR"}
    MY_TRADER_ID = "Ninja"
    ORDER_ID = "order_id"
    TRADER_ID = "trader_id"
    PRICE = "price"
    QUANTITY = "quantity"
    ORDER_QUANTITY_FILLED = "quantity_filled"
    CURRENT_POSITION = "position"
    TENDER_ID = "tender_id"

    def getSession(self):
        with requests.Session() as s:
            s.headers.update(self.API_KEY)
        return s

    def sendMarketOrder(self, ticker, order_type, quantity, direction):
        session = self.getSession()
        mkt_order_params = {
            "ticker": ticker,
            "type": order_type,
            "quantity": quantity,
            "action": direction,
        }
        response = session.post(
            "http://localhost:9999/v1/orders", params=mkt_order_params
        )
        order = response.json()
        return order["order_id"]

    def sendLimitOrder(self, ticker, quantity, direction, price):
        session = self.getSession()
        mkt_order_params = {
            "ticker": ticker,
            "type": "LIMIT",
            "quantity": quantity,
            "action": direction,
            "price": price,
        }
        response = session.post(
            "http://localhost:9999/v1/orders", params=mkt_order_params
        )
        order = response.json()
        return order["order_id"]

    def retrieveOrderBook(self, ticker, length):
        session = self.getSession()
        response = session.get(
            "http://localhost:9999/v1/securities/book?ticker="
            + ticker
            + "&limit="
            + str(length)
        )
        return response.json()

    def retrieveOrderBookSmall(self, ticker):
        session = self.getSession()
        response = session.get(
            "http://localhost:9999/v1/securities/book?ticker=" + ticker + "&limit=5"
        )
        return response.json()

    def getLimitPrice(self, ticker, orderType):
        orderBook = self.retrieveOrderBookSmall(ticker)
        if orderType == "BUY":
            return orderBook["bids"][0][self.PRICE]
        else:
            return orderBook["asks"][0][self.PRICE]

    def getTotalPosition(self, ticker):
        session = self.getSession()
        response = session.get("http://localhost:9999/v1/securities?ticker=" + ticker)
        content = response.json()
        return content[0][self.CURRENT_POSITION]

    def closePosition(self, ticker):
        position = self.getTotalPosition(ticker)
        self.sendMarketOrderUnderVolumeConstraint(position, ticker)

    def sendMarketOrderUnderVolumeConstraint(self, quantity, ticker):
        if quantity > 10000:
            quantity = 10000
        elif quantity < -10000:
            quantity = -10000
        self.sendMarketOrder(ticker, "MARKET", quantity, "SELL")
        # if quantity >= 10000:
        #     self.sendMarketOrder (ticker, "MARKET", orderQuantity, "SELL")
        # elif quantity > 0:
        #     self.sendMarketOrder (ticker, "MARKET", quantity, "SELL")
        # elif quantity <= -10000:
        #     self.sendMarketOrder (ticker, "MARKET", 10000, "BUY")
        # else:
        #     self.sendMarketOrder (ticker, "MARKET", abs (quantity), "BUY")

    def getQuantityForOrder(self, quantity):
        if quantity >= 10000:
            return 10000
        elif quantity <= -10000:
            return -10000
        else:
            return quantity

    def getActiveTender(self):
        session = self.getSession()
        response = session.get("http://localhost:9999/v1/tenders")
        return response.json()

    def acceptTender(self, tenderId):
        session = self.getSession()
        response = session.post("http://localhost:9999/v1/tenders/" + str(tenderId))
        return response.json()

    def debateTender(self):
        tender = self.getActiveTender()
        if len(tender) <= 0:
            return None
        tenderId = tender[0][self.TENDER_ID]
        tenderAction = tender[0]["action"]
        orderBook = self.retrieveOrderBook("RITC", 75)
        sentiment = self.determineMarketSentiment("RITC")
        arbitrage = 0.12
        if tenderAction == "BUY":
            tenderPrice = tender[0][self.PRICE]
            price = self.getLimitPrice("RITC", "BUY")
            if price - tenderPrice > arbitrage and (
                sentiment > 1 or len(orderBook["bids"]) > 35
            ):
                self.acceptTender(tenderId)
                return (
                    tender[0][self.QUANTITY],
                    tender[0][self.PRICE],
                    tender[0]["action"],
                )
        else:
            tenderPrice = tender[0][self.PRICE]
            price = self.getLimitPrice("RITC", "SELL")
            if tenderPrice - price > arbitrage and (
                sentiment < 1 or len(orderBook["asks"]) > 35
            ):
                self.acceptTender(tenderId)
                return (
                    tender[0][self.QUANTITY],
                    tender[0][self.PRICE],
                    tender[0]["action"],
                )
        return None

    def placeAggressiveExitTenderLimitOrders(self, ticker, quantity, price, action):
        # If changing to use price, use +0.10 instead of -0.01
        delta = 0.07
        limitSellPrice = self.getLimitPrice(ticker, "SELL")
        limitBuyPrice = self.getLimitPrice(ticker, "BUY")
        sentiment = self.determineMarketSentiment("RITC")
        while quantity > 0:
            orderQuantity = self.getQuantityForOrder(quantity)
            if action == "BUY":
                self.sendLimitOrder(
                    ticker, orderQuantity, "SELL", max(price, limitSellPrice) + delta
                )
            else:
                self.sendLimitOrder(
                    ticker, orderQuantity, "BUY", min(price, limitBuyPrice) - delta
                )
            quantity -= orderQuantity
            if sentiment > 1.5 or sentiment < 0.75:
                delta += 0.02
            else:
                delta += 0.01

    def placeConservativeExitTenderLimitOrders(self, ticker, quantity, price, action):
        # If changing to use price, use +0.10 instead of -0.01
        delta = 0.00
        limitSellPrice = self.getLimitPrice(ticker, "SELL")
        limitBuyPrice = self.getLimitPrice(ticker, "BUY")
        while quantity > 0:
            orderQuantity = self.getQuantityForOrder(quantity)
            if action == "BUY":
                self.sendLimitOrder(ticker, orderQuantity, "SELL", price + 0.10)
            else:
                self.sendLimitOrder(ticker, orderQuantity, "BUY", price - 0.10)
            quantity -= orderQuantity

    def cancelOrder(self, orderId):
        session = self.getSession()
        response = session.delete("http://localhost:9999/v1/orders/" + str(orderId))
        return response.json()

    def killAllOrders(self, ticker):
        orderBook = self.retrieveOrderBook(ticker, 30)
        for order in orderBook["bids"]:
            if order[self.TRADER_ID] == self.MY_TRADER_ID:
                orderId = order[self.ORDER_ID]
                self.cancelOrder(orderId)
        for order in orderBook["asks"]:
            if order[self.TRADER_ID] == self.MY_TRADER_ID:
                orderId = order[self.ORDER_ID]
                self.cancelOrder(orderId)

    def determineMarketSentiment(self, ticker):
        orderBook = self.retrieveOrderBook(ticker, 50)
        bidVolume = 0
        askVolume = 0
        for order in orderBook["bids"]:
            if order[self.TRADER_ID] != self.MY_TRADER_ID:
                bidVolume += order[self.QUANTITY] - order[self.ORDER_QUANTITY_FILLED]
        for order in orderBook["asks"]:
            if order[self.TRADER_ID] != self.MY_TRADER_ID:
                askVolume += order[self.QUANTITY] - order[self.ORDER_QUANTITY_FILLED]
        if askVolume == 0:
            return 1
        else:
            return bidVolume / askVolume
