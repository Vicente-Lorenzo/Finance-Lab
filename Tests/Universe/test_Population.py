import pytest
from Library.Database.Postgres.Postgres import PostgresDatabaseAPI
from Library.Database.Query import QueryAPI
from Library.Universe import CategoryAPI, ProviderAPI, TickerAPI, Provider, Platform, SecurityAPI, ContractAPI, TimeframeAPI
from Library.Database.Datapoint import DatapointAPI

def test_populate_universe(db):
    by = "Population"

    categories = [
        ("Forex (Major)", "Forex", "Major", "Currency"),
        ("Forex (Minor)", "Forex", "Minor", "Currency"),
        ("Forex (Exotic)", "Forex", "Exotic", "Currency")
    ]
    for uid, primary, secondary, alt in categories:
        cat = CategoryAPI(UID=uid, Primary=primary, Secondary=secondary, Alternative=alt, db=db)
        cat.push(by=by)

    provider_map = {
        Provider.Spotware: "Spotware Systems",
        Provider.Pepperstone: "Pepperstone Europe",
        Provider.ICMarkets: "IC Markets EU Ltd",
        Provider.Bloomberg: "Bloomberg",
        Provider.Yahoo: "Yahoo Finance"
    }

    for p in Provider:
        name = provider_map[p]
        abbrev = p.name
        uid = f"{abbrev} ({Platform.cTrader.name})"
        provider = ProviderAPI(UID=uid, Platform=Platform.cTrader, Name=name, Abbreviation=abbrev, db=db)
        provider.push(by=by)

    forex_data = [
        ("EURUSD", "Forex (Major)", "EUR", "Euro", "USD", "US Dollar", "Euro vs US Dollar"),
        ("USDJPY", "Forex (Major)", "USD", "US Dollar", "JPY", "Japanese Yen", "US Dollar vs Japanese Yen"),
        ("GBPUSD", "Forex (Major)", "GBP", "British Pound", "USD", "US Dollar", "British Pound vs US Dollar"),
        ("USDCHF", "Forex (Major)", "USD", "US Dollar", "CHF", "Swiss Franc", "US Dollar vs Swiss Franc"),
        ("AUDUSD", "Forex (Major)", "AUD", "Australian Dollar", "USD", "US Dollar", "Australian Dollar vs US Dollar"),
        ("USDCAD", "Forex (Major)", "USD", "US Dollar", "CAD", "Canadian Dollar", "US Dollar vs Canadian Dollar"),
        ("NZDUSD", "Forex (Major)", "NZD", "New Zealand Dollar", "USD", "US Dollar", "New Zealand Dollar vs US Dollar"),
        ("EURGBP", "Forex (Minor)", "EUR", "Euro", "GBP", "British Pound", "Euro vs British Pound"),
        ("EURJPY", "Forex (Minor)", "EUR", "Euro", "JPY", "Japanese Yen", "Euro vs Japanese Yen"),
        ("EURCHF", "Forex (Minor)", "EUR", "Euro", "CHF", "Swiss Franc", "Euro vs Swiss Franc"),
        ("EURAUD", "Forex (Minor)", "EUR", "Euro", "AUD", "Australian Dollar", "Euro vs Australian Dollar"),
        ("EURCAD", "Forex (Minor)", "EUR", "Euro", "CAD", "Canadian Dollar", "Euro vs Canadian Dollar"),
        ("EURNZD", "Forex (Minor)", "EUR", "Euro", "NZD", "New Zealand Dollar", "Euro vs New Zealand Dollar"),
        ("GBPJPY", "Forex (Minor)", "GBP", "British Pound", "JPY", "Japanese Yen", "British Pound vs Japanese Yen"),
        ("GBPCHF", "Forex (Minor)", "GBP", "British Pound", "CHF", "Swiss Franc", "British Pound vs Swiss Franc"),
        ("GBPAUD", "Forex (Minor)", "GBP", "British Pound", "AUD", "Australian Dollar", "British Pound vs Australian Dollar"),
        ("GBPCAD", "Forex (Minor)", "GBP", "British Pound", "CAD", "Canadian Dollar", "British Pound vs Canadian Dollar"),
        ("GBPNZD", "Forex (Minor)", "GBP", "British Pound", "NZD", "New Zealand Dollar", "British Pound vs New Zealand Dollar"),
        ("CHFJPY", "Forex (Minor)", "CHF", "Swiss Franc", "JPY", "Japanese Yen", "Swiss Franc vs Japanese Yen"),
        ("AUDJPY", "Forex (Minor)", "AUD", "Australian Dollar", "JPY", "Japanese Yen", "Australian Dollar vs Japanese Yen"),
        ("AUDCHF", "Forex (Minor)", "AUD", "Australian Dollar", "CHF", "Swiss Franc", "Australian Dollar vs Swiss Franc"),
        ("AUDCAD", "Forex (Minor)", "AUD", "Australian Dollar", "CAD", "Canadian Dollar", "Australian Dollar vs Canadian Dollar"),
        ("AUDNZD", "Forex (Minor)", "AUD", "Australian Dollar", "NZD", "New Zealand Dollar", "Australian Dollar vs New Zealand Dollar"),
        ("CADJPY", "Forex (Minor)", "CAD", "Canadian Dollar", "JPY", "Japanese Yen", "Canadian Dollar vs Japanese Yen"),
        ("CADCHF", "Forex (Minor)", "CAD", "Canadian Dollar", "CHF", "Swiss Franc", "Canadian Dollar vs Swiss Franc"),
        ("NZDJPY", "Forex (Minor)", "NZD", "New Zealand Dollar", "JPY", "Japanese Yen", "New Zealand Dollar vs Japanese Yen"),
        ("NZDCHF", "Forex (Minor)", "NZD", "New Zealand Dollar", "CHF", "Swiss Franc", "New Zealand Dollar vs Swiss Franc"),
        ("NZDCAD", "Forex (Minor)", "NZD", "New Zealand Dollar", "CAD", "Canadian Dollar", "New Zealand Dollar vs Canadian Dollar"),
        ("USDHKD", "Forex (Exotic)", "USD", "US Dollar", "HKD", "Hong Kong Dollar", "US Dollar vs Hong Kong Dollar"),
        ("USDSGD", "Forex (Exotic)", "USD", "US Dollar", "SGD", "Singapore Dollar", "US Dollar vs Singapore Dollar"),
        ("USDTRY", "Forex (Exotic)", "USD", "US Dollar", "TRY", "Turkish Lira", "US Dollar vs Turkish Lira"),
        ("USDMXN", "Forex (Exotic)", "USD", "US Dollar", "MXN", "Mexican Peso", "US Dollar vs Mexican Peso"),
        ("USDZAR", "Forex (Exotic)", "USD", "US Dollar", "ZAR", "South African Rand", "US Dollar vs South African Rand"),
        ("USDSEK", "Forex (Exotic)", "USD", "US Dollar", "SEK", "Swedish Krona", "US Dollar vs Swedish Krona"),
        ("USDNOK", "Forex (Exotic)", "USD", "US Dollar", "NOK", "Norwegian Krone", "US Dollar vs Norwegian Krone"),
        ("USDDKK", "Forex (Exotic)", "USD", "US Dollar", "DKK", "Danish Krone", "US Dollar vs Danish Krone"),
        ("USDCNH", "Forex (Exotic)", "USD", "US Dollar", "CNH", "Offshore Chinese Yuan", "US Dollar vs Offshore Chinese Yuan"),
        ("USDTHB", "Forex (Exotic)", "USD", "US Dollar", "THB", "Thai Baht", "US Dollar vs Thai Baht"),
        ("USDRUB", "Forex (Exotic)", "USD", "US Dollar", "RUB", "Russian Ruble", "US Dollar vs Russian Ruble"),
        ("USDPLN", "Forex (Exotic)", "USD", "US Dollar", "PLN", "Polish Zloty", "US Dollar vs Polish Zloty"),
        ("USDHUF", "Forex (Exotic)", "USD", "US Dollar", "HUF", "Hungarian Forint", "US Dollar vs Hungarian Forint"),
        ("USDSAR", "Forex (Exotic)", "USD", "US Dollar", "SAR", "Saudi Riyal", "US Dollar vs Saudi Riyal"),
        ("USDILS", "Forex (Exotic)", "USD", "US Dollar", "ILS", "Israeli New Shekel", "US Dollar vs Israeli New Shekel"),
        ("EURTRY", "Forex (Exotic)", "EUR", "Euro", "TRY", "Turkish Lira", "Euro vs Turkish Lira"),
        ("EURSEK", "Forex (Exotic)", "EUR", "Euro", "SEK", "Swedish Krona", "Euro vs Swedish Krona"),
        ("EURNOK", "Forex (Exotic)", "EUR", "Euro", "NOK", "Norwegian Krone", "Euro vs Norwegian Krone"),
        ("EURZAR", "Forex (Exotic)", "EUR", "Euro", "ZAR", "South African Rand", "Euro vs South African Rand"),
        ("EURHUF", "Forex (Exotic)", "EUR", "Euro", "HUF", "Hungarian Forint", "Euro vs Hungarian Forint"),
        ("EURPLN", "Forex (Exotic)", "EUR", "Euro", "PLN", "Polish Zloty", "Euro vs Polish Zloty"),
        ("GBPMXN", "Forex (Exotic)", "GBP", "British Pound", "MXN", "Mexican Peso", "British Pound vs Mexican Peso"),
    ]

    provider_uid = f"Spotware ({Platform.cTrader.name})"

    for uid, cat, base_asset, base_name, quote_asset, quote_name, desc in forex_data:
        ticker = TickerAPI(UID=uid, Category=cat, BaseAsset=base_asset, BaseName=base_name, QuoteAsset=quote_asset, QuoteName=quote_name, Description=desc, db=db)
        ticker.push(by=by)
        
        contract = ContractAPI(TickerUID=uid, ProviderUID=provider_uid, db=db)
        contract.push(by=by)
        
        sec = SecurityAPI(ProviderUID=provider_uid, CategoryUID=cat, TickerUID=uid, db=db)
        sec.push(by=by)
        
    timeframes = [
        "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10", "M15", "M20", "M30", "M45",
        "H1", "H2", "H3", "H4", "H6", "H8", "H12",
        "D1", "D2", "D3",
        "W1",
        "MN1"
    ]
    for tf in timeframes:
        t = TimeframeAPI(UID=tf, db=db)
        t.push(by=by)