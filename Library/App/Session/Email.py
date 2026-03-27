from dataclasses import dataclass, field

from Library.App.Session.Storage import StorageAPI

@dataclass(kw_only=True)
class EmailAPI(StorageAPI):

    to: str | list = field(default=None, init=True, repr=True)
    cc: str | list = field(default=None, init=True, repr=True)
    bcc: str | list = field(default=None, init=True, repr=True)
    subject: str | list = field(default=None, init=True, repr=True)
    message: str | list = field(default=None, init=True, repr=True)