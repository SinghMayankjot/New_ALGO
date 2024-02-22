import threading
import time

from GuiManager import *


class ConsiderTenderThread (threading.Thread):
    def __init__ (self):
        threading.Thread.__init__ (self)
        self.running = True
        self.stopFlag = False

    def run (self):
        while self.running:
            if self.stopFlag:
                exit (1)
            tenderQuantityAndPrice = orderManager.debateTender ()
            if tenderQuantityAndPrice is not None:
                # if tenderQuantityAndPrice [2] == "BUY":
                #     price = orderManager.getLimitPrice ("RITC", "SELL")
                # else:
                #     price = orderManager.getLimitPrice ("RITC", "BUY")
                orderManager.placeAggressiveExitTenderLimitOrders ("RITC", tenderQuantityAndPrice [0], tenderQuantityAndPrice [1],
                                                                   tenderQuantityAndPrice [2])
            time.sleep (1)

    def stopThread (self):
        self.stopFlag = True


class DetermineTrendThread (threading.Thread):
    def __init__ (self, ticker):
        threading.Thread.__init__ (self)
        self.running = True
        self.stopFlag = False
        self.ticker = ticker
        self.sentiment = tkinter.StringVar()
        self.BULLSentimentFlag = tkinter.Button (tradingGUI, textvariable=self.sentiment, command=marketBuyBULL, height=3,
                                            width=15)
        self.BULLSentimentFlag.grid (row=4, column=2)

    def run (self):
        while self.running:
            if self.stopFlag:
                exit (1)
            self.sentiment = orderManager.determineMarketSentiment (self.ticker)
            self.BULLSentimentFlag.set(str(self.sentiment))
            time.sleep (1)

    def stopThread (self):
        self.stopFlag = True


# BULLSentimentThread = DetermineTrendThread ("BULL")
# BULLSentimentThread.start ()

createRITCButtons ()
createBULLButtons ()
createBEARButtons ()
createUSDButton ()

tenderDebateThread = ConsiderTenderThread ()
tenderDebateThread.start ()

tradingGUI.mainloop ()
tenderDebateThread.stopThread ()
# BULLSentimentThread.stopThread()
