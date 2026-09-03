import pandas as pd
from src.download.selectsymbols import daysin2025

def calcmeanvol(num, timestamp, symbol):
    for index in range(num-21, num-1):
        dataframe = pd.read_parquet(f"data/minute/{daysin2025[index].date()}.parquet")
        tsdf = dataframe.reorder_levels(["timestamp", "symbol"]).sort_index()
        print(tsdf.loc[(timestamp, symbol), "volume"])

for timestamp in pd.read_parquet("data/minute/2025-01-31.parquet").reorder_levels(["timestamp", "symbol"]).sort_index().index.get_level_values("timestamp"):
    print(timestamp)

calcmeanvol(30, "2025-01-03T14:30:00+00:00", "AAPL")