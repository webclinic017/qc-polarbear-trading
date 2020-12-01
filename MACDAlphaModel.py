from QuantConnect import *
from QuantConnect.Indicators import *
from QuantConnect.Algorithm import *
from QuantConnect.Algorithm.Framework import *
from QuantConnect.Algorithm.Framework.Alphas import *
from collections import defaultdict


class MACDAlphaModel(AlphaModel):

    def __init__(self, resolution = Resolution.Daily):
        self.symbolData = {}
        self.resolution = resolution

    def Update(self, algorithm, data):
        insights = []
        for symbol, symbolData in self.symbolData.items():
            algorithm.Log(str(symbol) + " " + str(algorithm.Portfolio[symbol].Profit))
            direction = symbolData.PreviousDirection
            normalizedMacd = symbolData.macd.Current.Value - symbolData.macd.Signal.Current.Value
            symbolData.macdWindow.Add(normalizedMacd)
            if symbolData.IsReady():
                curMacd = symbolData.macdWindow[0]
                prevMacd = symbolData.macdWindow[1]
                prevPrevMacd = symbolData.macdWindow[2]
                security = algorithm.Securities[symbol]
                if algorithm.Securities[symbol].Invested:
                    if curMacd > 0.0001:
                        if curMacd < prevMacd < prevPrevMacd:
                            direction = InsightDirection.Flat
                    else:
                        direction = InsightDirection.Flat
                else:
                    if curMacd > 0.0001 and curMacd > prevMacd:
                        direction = InsightDirection.Up
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
        self.Security = security
        self.macd = MovingAverageConvergenceDivergence(1, 14, 20, MovingAverageType.Triangular)
        self.macdWindow = RollingWindow[float](3)
        algorithm.RegisterIndicator(security.Symbol, self.macd, resolution)
        self.PreviousDirection = InsightDirection.Flat
        for time, row in history.loc[security.Symbol].iterrows():
            self.macd.Update(time, row["close"])
            if self.macd.IsReady:
                normalizedMacd = self.macd.Current.Value - self.macd.Signal.Current.Value
                self.macdWindow.Add(normalizedMacd)
                
        
    def IsReady(self):
        return self.macdWindow.IsReady and self.macdWindow.Size == 3 and self.macd.IsReady