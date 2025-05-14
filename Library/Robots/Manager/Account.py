from Library.Robots.Container.Classes import Account

class AccountAPI:
    
    def __init__(self):
        self.Balance: float | None = None
        self.Equity: float | None = None

    def init_account(self, account: Account) -> None:
        self.Balance = account.Balance
        self.Equity = account.Equity

    def update_account(self, account: Account) -> None:
        self.Balance = account.Balance
        self.Equity = account.Equity

    def data(self) -> Account:
        return Account(self.Balance, self.Equity)

    def __repr__(self):
        return repr(self.data())