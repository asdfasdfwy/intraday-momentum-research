from src.download.selectsymbols import daysin2025
import math

portval = int(input("Starting portfolio:"))
cash = portval
portstocks = {}

def buy(ticker, boughtat):
    global cash, portval
    number = math.floor((portval*0.5)/boughtat)
    cashneeded = number*boughtat
    if cash >= cashneeded:
        portstocks[ticker] = [number, boughtat, 0]
        cash -= number*boughtat

def sell(ticker, currentval):
    global cash, portval
    profpershare = currentval - portstocks[ticker][1]
    portval += profpershare*portstocks[ticker][0]
    cash += portstocks[ticker][0]*currentval
    del portstocks[ticker]

for day in daysin2025:
    print(f"{day.date()}: {portval}")