from Library.Classes import AccountType, AssetType, MarginMode, Account

class AccountAPI:

    def __init__(self):
        self.AccountType: AccountType | None = None
        self.AssetType: AssetType | None = None
        self.Balance: float | None = None
        self.Equity: float | None = None
        self.Credit: float | None = None
        self.Leverage: float | None = None
        self.MarginUsed: float | None = None
        self.MarginFree: float | None = None
        self.MarginLevel: float | None = None
        self.MarginStopLevel: float | None = None
        self.MarginMode: MarginMode | None = None

    def init_account(self, account: Account) -> None:
        self.AccountType = account.AccountType
        self.AssetType = account.AssetType
        self.Balance = account.Balance
        self.Equity = account.Equity
        self.Credit = account.Credit
        self.Leverage = account.Leverage
        self.MarginUsed = account.MarginUsed
        self.MarginFree = account.MarginFree
        self.MarginLevel = account.MarginLevel
        self.MarginStopLevel = account.MarginStopLevel
        self.MarginMode = account.MarginMode

    def update_account(self, account: Account) -> None:
        self.Balance = account.Balance
        self.Equity = account.Equity
        self.Credit = account.Credit
        self.MarginUsed = account.MarginUsed
        self.MarginFree = account.MarginFree
        self.MarginLevel = account.MarginLevel

    def data(self) -> Account:
        return Account(
            AccountType=self.AccountType,
            AssetType=self.AssetType,
            Balance=self.Balance,
            Equity=self.Equity,
            Credit=self.Credit,
            Leverage=self.Leverage,
            MarginUsed=self.MarginUsed,
            MarginFree=self.MarginFree,
            MarginLevel=self.MarginLevel,
            MarginStopLevel=self.MarginStopLevel,
            MarginMode=self.MarginMode
        )

    def __repr__(self):
        return repr(self.data())
