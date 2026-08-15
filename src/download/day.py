from src.download.selectsymbols import daysin2025, getsymbols

for index in range(0,len(daysin2025)):
    if (index >= 87):
        totaldf = getsymbols(daysin2025[index])
        totaldf.to_parquet(f"data/day/{daysin2025[index].date()}.parquet")
        print(f"{index+1}/{len(daysin2025)} downloaded")