from Library.Formulas import historical_price

print(historical_price("NVDA", "2024-06-26 00:00:00", None, "Close", False).squeeze())
