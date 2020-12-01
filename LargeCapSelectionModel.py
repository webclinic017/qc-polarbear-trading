from QuantConnect.Data.UniverseSelection import *
from Selection.FundamentalUniverseSelectionModel import FundamentalUniverseSelectionModel

class LargeCapSelectionModel(FundamentalUniverseSelectionModel):

    def __init__(self, filterFineData = True, universeSettings = None, securityInitializer = None):
        super().__init__(filterFineData, universeSettings, securityInitializer)
        self.lastDay = -1
        self.coarseSelection = {}

    def SelectCoarse(self, algorithm, coarse):
        if algorithm.Time.day == self.lastDay:
            return Universe.Unchanged
        coarse = [c for c in coarse if c.HasFundamentalData and c.Volume > 5e5 and c.Price > 0]
        coarse = sorted(coarse, key=lambda c: c.Volume, reverse=True)
        self.coarseSelection = {x.Symbol : x.Volume for x in coarse}
        return [c.Symbol for c in coarse]

    def SelectFine(self, algorithm, fine):
        fine = [f for f in fine if f.CompanyReference.CountryId == "USA"
            and f.CompanyReference.PrimaryExchangeID in ["NYS","NAS"] 
            and (algorithm.Time - f.SecurityReference.IPODate).days > 180 
            and f.MarketCap > 50e9]
        self.lastDay = algorithm.Time.day
        fine = [f for f in fine if f.EarningReports.DilutedEPS.ThreeMonths > 0]
        fine = sorted(fine, key=lambda f: f.ValuationRatios.PERatio, reverse=True)
        algorithm.Log(", ".join([f.Symbol.Value for f in fine]))
        fine = [f.Symbol for f in fine][:10]
        return fine