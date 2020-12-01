from QuantConnect.Data.UniverseSelection import *
from Selection.FundamentalUniverseSelectionModel import FundamentalUniverseSelectionModel

class HighPESelectionModel(FundamentalUniverseSelectionModel):
    
    def __init__(self, filterFineData = True, universeSettings = None, securityInitializer = None):
        super().__init__(filterFineData, universeSettings, securityInitializer)
        self.lastDay = -1
        self.coarseSelection = {}

    def SelectCoarse(self, algorithm, coarse):
        if algorithm.Time.day == self.lastDay:
            return Universe.Unchanged
        coarse = [c for c in coarse if c.HasFundamentalData and c.Volume > 1e6 and c.Price > 0]
        coarse = sorted(coarse, key=lambda c: c.Volume, reverse=True)
        self.coarseSelection = {x.Symbol : x.Volume for x in coarse}
        return [c.Symbol for c in coarse]

    def SelectFine(self, algorithm, fine):
        fine = [f for f in fine if f.CompanyReference.CountryId == "USA" 
            and f.CompanyReference.PrimaryExchangeID in ["NYS","NAS"] 
            and (algorithm.Time - f.SecurityReference.IPODate).days > 180 
            and f.MarketCap > 1e9]
        self.lastDay = algorithm.Time.day
        fine = [f for f in fine if f.OperationRatios.RevenueGrowth.ThreeMonths > 0 and f.EarningRatios.DilutedEPSGrowth.ThreeMonths > 1 and f.ValuationRatios.PERatio > 400]
        fine = sorted(fine, key=lambda f: self.coarseSelection[f.Symbol], reverse=True)
        fine = [f.Symbol for f in fine][:15]
        fine = fine
        return fine