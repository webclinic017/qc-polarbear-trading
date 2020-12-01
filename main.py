from Selection.QC500UniverseSelectionModel import QC500UniverseSelectionModel
from Alphas.MacdAlphaModel import MacdAlphaModel
from Alphas.RsiAlphaModel import RsiAlphaModel
from Portfolio.BlackLittermanOptimizationPortfolioConstructionModel import BlackLittermanOptimizationPortfolioConstructionModel
from Portfolio.EqualWeightingPortfolioConstructionModel import EqualWeightingPortfolioConstructionModel
from Portfolio.MeanVarianceOptimizationPortfolioConstructionModel import MeanVarianceOptimizationPortfolioConstructionModel
from Portfolio.MaximumSharpeRatioPortfolioOptimizer import MaximumSharpeRatioPortfolioOptimizer
from Execution.ImmediateExecutionModel import ImmediateExecutionModel
from Risk.MaximumDrawdownPercentPerSecurity import MaximumDrawdownPercentPerSecurity
from HighPESelectionModel import HighPESelectionModel
from LargeCapSelectionModel import LargeCapSelectionModel
from MACDAlphaModel import MACDAlphaModel
from StochAlphaModel import StochAlphaModel
class SimpleProject(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2020, 8, 1)
        # self.SetEndDate(2020, 10, 20)
        self.SetCash(10000)
        resolution = Resolution.Hour
        self.UniverseSettings.Resolution = resolution
        self.SetAlpha(MACDAlphaModel(resolution))
        # self.SetUniverseSelection(ManualUniverseSelectionModel(self.CreateUSEquities(['TSLA', 'ZM'])))
        # self.SetPortfolioConstruction(BlackLittermanOptimizationPortfolioConstructionModel(
        #     rebalance = resolution,
        #     portfolioBias = PortfolioBias.Long,
        #     resolution = resolution))
        self.SetPortfolioConstruction(EqualWeightingPortfolioConstructionModel())
        self.SetUniverseSelection(HighPESelectionModel())
        self.SetExecution(ImmediateExecutionModel())
        self.SetRiskManagement(MaximumDrawdownPercentPerSecurity(0.03))

    def OnData(self, data):
        pass
    
    def CreateUSEquities(self, symbols):
        return [Symbol.Create(s, SecurityType.Equity, Market.USA) for s in symbols]
        
    def GetSymbolsFromDropBox(self, dateTime = None):
        symbols = self.Download("https://www.dropbox.com/s/5eiq5vcyqyzeun3/quant-stocks.csv?dl=1")
        self.Log(symbols)
        return self.CreateUSEquities(symbols.split(','))
    
    def GetSymbolsFromDropBoxUrl(self, url):
        symbols = self.Download(url)
        self.Log(symbols)
        return self.CreateUSEquities(symbols.split(','))