from QuantConnect import *
from QuantConnect.Indicators import *
from QuantConnect.Algorithm import *
from QuantConnect.Algorithm.Framework import *
from QuantConnect.Algorithm.Framework.Alphas import *
from collections import defaultdict

class StochAlphaModel(AlphaModel):

    def __init__(self, resolution = Resolution.Daily):
        self.symbolData = {}
        self.resolution = resolution

    def Update(self, algorithm, data):
        insights = []
        for symbol, symbolData in self.symbolData.items():
            # algorithm.Log(str(symbol) + " " + str(algorithm.Portfolio[symbol].Profit))
            direction = symbolData.PreviousDirection
            symbolData.kWindow.Add(symbolData.stoch.StochK.Current)
            symbolData.dWindow.Add(symbolData.stoch.StochD.Current)
            if symbolData.IsReady():
                curK, curD = symbolData.kWindow[0], symbolData.dWindow[0]
                prevK, prevD = symbolData.kWindow[1], symbolData.dWindow[1]
                algorithm.Log(f"{symbol}: {curK} {curD}, {prevK} {prevD}")
                if algorithm.Securities[symbol].Invested:
                    if curK <= curD:
                        direction = InsightDirection.Flat
                    else:
                        direction = InsightDirection.Up
                else:
                    if curK > curD and prevK <= prevD and curK.Value <= 30:
                        direction = InsightDirection.Up
                    else:
                        direction = InsightDirection.Flat
                insight = Insight.Price(symbol, timedelta(hours=1), direction, 1, None, None, None)
                symbolData.PreviousDirection = direction
                insights.append(insight)
        return insights

    def OnSecuritiesChanged(self, algorithm, changes):
        for added in changes.AddedSecurities:
            history = algorithm.History(added.Symbol, 50, self.resolution)
            self.symbolData[added.Symbol] = SymbolData(algorithm, added, self.resolution, history)
        for removed in changes.RemovedSecurities:
            data = self.symbolData.pop(removed.Symbol, None)

class SymbolData:
    def __init__(self, algorithm, security, resolution, history):
        self.windowSize = 2
        self.Security = security
        self.stoch = Stochastic(14, 14, 3)
        self.kWindow = RollingWindow[IndicatorDataPoint](self.windowSize)
        self.dWindow = RollingWindow[IndicatorDataPoint](self.windowSize)
        algorithm.RegisterIndicator(security.Symbol, self.stoch, resolution)
        self.PreviousDirection = InsightDirection.Flat
        for time, row in history.loc[security.Symbol].iterrows():
            tradeBar = TradeBar(time, security.Symbol, row.open, row.high, row.low, row.close, row.volume)
            self.stoch.Update(tradeBar)
            if self.stoch.IsReady:
                self.kWindow.Add(self.stoch.StochK.Current)
                self.dWindow.Add(self.stoch.StochD.Current)
        
    def IsReady(self):
        return self.stoch.IsReady and self.dWindow.IsReady and self.kWindow.IsReady and self.dWindow.Size == self.windowSize and self.kWindow.Size == self.windowSize