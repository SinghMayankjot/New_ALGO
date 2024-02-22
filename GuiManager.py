import tkinter
from tkinter.ttk import Label

from ButtonCommands import *

tradingGUI = tkinter.Tk ()


def createRITCButtons ():
    marketBuyRITCButton = tkinter.Button (tradingGUI, text="Market Buy RITC", command=marketBuyRITC, height=3, width=15)
    marketBuyRITCButton.grid (row=0, column=0)
    marketSellRITCButton = tkinter.Button (tradingGUI, text="Market Sell RITC", command=marketSellRITC, height=3,
                                           width=15)
    marketSellRITCButton.grid (row=0, column=1)
    limitBuyRITCButton = tkinter.Button (tradingGUI, text="Limit Buy RITC", command=limitBuyRITC, height=3, width=15)
    limitBuyRITCButton.grid (row=1, column=0)
    limitSellRITCButton = tkinter.Button (tradingGUI, text="Limit Sell RITC", command=limitSellRITC, height=3, width=15)
    limitSellRITCButton.grid (row=1, column=1)
    closeRITCButton = tkinter.Button (tradingGUI, text="Close RITC", command=closeRITC, height=3, width=15)
    closeRITCButton.grid (row=2, column=0)
    killRITCOrdersButton = tkinter.Button (tradingGUI, text="Kill RITC Order", command=killAllRITCOrders, height=3,
                                           width=15)
    killRITCOrdersButton.grid (row=2, column=1)
    marketMakeRITCButtonArb = tkinter.Button (tradingGUI, text="MM RITC Spread",
                                              command=marketMakeRITCWithSpread, height=3,
                                              width=15)
    marketMakeRITCButtonArb.grid (row=3, column=0, pady=(0, 20))
    marketMakeRITCButtonSpread = tkinter.Button (tradingGUI, text="MM RITC Arb",
                                                 command=marketMakeRITCWithArb, height=3,
                                                 width=15)
    marketMakeRITCButtonSpread.grid (row=3, column=1, pady=(0, 20))


def createBULLButtons ():
    marketBuyBULLButton = tkinter.Button (tradingGUI, text="Market Buy BULL", command=marketBuyBULL, height=3, width=15)
    marketBuyBULLButton.grid (row=4, column=0)
    marketSellBULLButton = tkinter.Button (tradingGUI, text="Market Sell BULL", command=marketSellBULL, height=3,
                                           width=15)
    marketSellBULLButton.grid (row=4, column=1)
    limitBuyBULLButton = tkinter.Button (tradingGUI, text="Limit Buy BULL", command=limitBuyBULL, height=3, width=15)
    limitBuyBULLButton.grid (row=5, column=0)
    limitSellBULLButton = tkinter.Button (tradingGUI, text="Limit Sell BULL", command=limitSellBULL, height=3, width=15)
    limitSellBULLButton.grid (row=5, column=1)
    closeBULLButton = tkinter.Button (tradingGUI, text="Close BULL", command=closeBULL, height=3, width=15)
    closeBULLButton.grid (row=6, column=0, pady=(0, 20))
    killBULLOrdersButton = tkinter.Button (tradingGUI, text="Kill BULL Order", command=killAllBULLOrders, height=3,
                                           width=15)
    killBULLOrdersButton.grid (row=6, column=1, pady=(0, 20))


def createBEARButtons ():
     marketBuyBEARButton = tkinter.Button (tradingGUI, text="Market Buy BEAR", command=marketBuyBEAR, height=3, width=15)
#     marketBuyBEARButton.grid (row=7, column=0)
#     marketSellBEARButton = tkinter.Button (tradingGUI, text="Market Sell BEAR", command=marketSellBEAR, height=3,
#                                            width=15)
#     # marketSellBEARButton.grid (row=7, column=1)
#     # limitBuyBEARButton = tkinter.Button (tradingGUI, text="Limit Buy BEAR", command=limitBuyBEAR, height=3, width=15)
#     # limitBuyBEARButton.grid (row=8, column=0)
#     # limitSellBEARButton = tkinter.Button (tradingGUI, text="Limit Sell BEAR", command=limitSellBEAR, height=3, width=15)
#     # limitSellBEARButton.grid (row=8, column=1)
#     # closeBEARButton = tkinter.Button (tradingGUI, text="Close BEAR", command=closeBEAR, height=3, width=15)
#     # closeBEARButton.grid (row=9, column=0, pady=(0, 20))
#     # killBEAROrdersButton = tkinter.Button (tradingGUI, text="Kill BEAR Order", command=killAllBEAROrders, height=3,
#     #                                        width=15)
#     # killBEAROrdersButton.grid (row=9, column=1, pady=(0, 20))


def createUSDButton ():
    closeUSDButton = tkinter.Button (tradingGUI, text="Close USD", command=closeUSD, height=3, width=30)
    closeUSDButton.grid (row=7, column=0, columnspan=3)
    buyUSDButton = tkinter.Button (tradingGUI, text="Buy USD", command=buyUSD, height=3, width=15)
    buyUSDButton.grid (row=8, column=0)
    sellUSDButton = tkinter.Button (tradingGUI, text="Sell USD", command=sellUSD, height=3, width=15)
    sellUSDButton.grid (row=8, column=1)


def createBullBearFlags (BULLFlag, BEARFlag):
    BULLSentimentFlag = tkinter.Button (tradingGUI, textvariable=BULLFlag, command=marketBuyBULL, height=3, width=15)
    BULLSentimentFlag.grid (row=4, column=2)
