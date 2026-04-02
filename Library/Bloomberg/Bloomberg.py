import blpapi

from Library.Service import ServiceAPI
from Library.Dataframe import DataframeAPI

from Library.Bloomberg.Query import QueryAPI
from Library.Bloomberg.Intraday import IntradayAPI
from Library.Bloomberg.Streaming import StreamingAPI
from Library.Bloomberg.Reference import ReferenceAPI
from Library.Bloomberg.Historical import HistoricalAPI

class BloombergAPI(ServiceAPI, DataframeAPI):

    def __init__(self, *,
                 host: str = "localhost",
                 port: int = 8194,
                 legacy: bool = False) -> None:
        super().__init__(legacy=legacy)

        self._host_: str = host
        self._port_: int = port

        self._session_ = None
        self._services_ = set()

        self.reference = ReferenceAPI(self)
        self.historical = HistoricalAPI(self)
        self.streaming = StreamingAPI(self)
        self.intraday = IntradayAPI(self)
        self.query = QueryAPI(self)

    def connected(self) -> bool:
        return self._session_ is not None

    def _connect_(self, **kwargs) -> None:
        options = blpapi.SessionOptions()
        options.setServerHost(self._host_)
        options.setServerPort(self._port_)
        self._session_ = blpapi.Session(options)
        if not self._session_.start():
            self._session_ = None
            raise ConnectionError(f"Failed to start Bloomberg session at {self._host_}:{self._port_}")

    def disconnected(self) -> bool:
        return self._session_ is None

    def _disconnect_(self) -> None:
        if self._session_ is not None:
            self._session_.stop()
            self._session_ = None
            self._services_.clear()

    def _service_(self, uri: str) -> blpapi.Service:
        if uri not in self._services_:
            if not self._session_.openService(uri):
                raise ConnectionError(f"Failed to open Bloomberg service: {uri}")
            self._services_.add(uri)
        return self._session_.getService(uri)