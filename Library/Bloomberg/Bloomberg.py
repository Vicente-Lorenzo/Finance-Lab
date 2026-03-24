import atexit
import blpapi

from Library.Statistics import Timer
from Library.Logging import HandlerLoggingAPI
from Library.Dataframe import pd, pl, DataframeAPI
from Library.Bloomberg.Reference import ReferenceAPI
from Library.Bloomberg.Historical import HistoricalAPI
from Library.Bloomberg.Intraday import IntradayAPI
from Library.Bloomberg.Query import QueryAPI
from Library.Bloomberg.Streaming import StreamingAPI

class BloombergAPI(DataframeAPI):

    def __init__(self, *, host: str = "localhost", port: int = 8194, legacy: bool = False) -> None:
        super().__init__(legacy=legacy)
        self._host_: str = host
        self._port_: int = port
        self._session_ = None
        self._guard_ = None
        self._log_ = HandlerLoggingAPI(self.__class__.__name__)
        self.reference = ReferenceAPI(self)
        self.historical = HistoricalAPI(self)
        self.intraday = IntradayAPI(self)
        self.query = QueryAPI(self)
        self.streaming = StreamingAPI(self)

    def connected(self) -> bool:
        return self._session_ is not None

    def guarded(self) -> bool:
        return self._guard_ is not None

    def connect(self):
        try:
            if self.connected():
                self._log_.debug(lambda: "Connect Operation: Skipped (Already Connected)")
                return self
            timer = Timer()
            timer.start()
            options = blpapi.SessionOptions()
            options.setServerHost(self._host_)
            options.setServerPort(self._port_)
            self._session_ = blpapi.Session(options)
            if not self._session_.start(): raise ConnectionError("Failed to start Bloomberg session.")
            if not self.guarded():
                self._guard_ = self.disconnect
                try: atexit.register(self._guard_)
                except: pass
            timer.stop()
            self._log_.info(lambda: f"Connect Operation: Connected ({timer.result()})")
            return self
        except Exception as e:
            self._log_.error(lambda: "Connect Operation: Failed")
            self._log_.exception(lambda: str(e))
            raise

    def disconnect(self):
        try:
            if not self.connected():
                self._log_.debug(lambda: "Disconnect Operation: Skipped (Not Connected)")
                return self
            timer = Timer()
            timer.start()
            self._session_.stop()
            self._session_ = None
            timer.stop()
            if self.guarded():
                try: atexit.unregister(self._guard_)
                except: pass
                self._guard_ = None
            self._log_.info(lambda: f"Disconnect Operation: Disconnected ({timer.result()})")
            return self
        except Exception as e:
            self._log_.error(lambda: "Disconnect Operation: Failed")
            self._log_.exception(lambda: str(e))
            raise

    def __enter__(self):
        return self.connect()

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if exception_type or exception_value or exception_traceback:
            self._log_.exception(lambda: f"Exception type: {exception_type}")
            self._log_.exception(lambda: f"Exception value: {exception_value}")
            self._log_.exception(lambda: f"Traceback: {exception_traceback}")
        self.disconnect()
        return not exception_type

    def __del__(self):
        try: self.disconnect()
        except: pass

    @staticmethod
    def _parse_element_(element) -> any:
        if element.isNull(): return None
        if element.isArray(): return [BloombergAPI._parse_element_(v) for v in element.values()]
        if element.datatype() == blpapi.DataType.CHOICE: return BloombergAPI._parse_element_(element.getChoice())
        if element.datatype() == blpapi.DataType.SEQUENCE:
            result = {}
            for i in range(element.numElements()):
                sub_element = element.getElement(i)
                result[str(sub_element.name())] = BloombergAPI._parse_element_(sub_element)
            return result
        return element.getValue()

    def execute(self, service_uri: str, request_type: str, build_request: callable) -> list:
        try:
            self.connect()
            timer = Timer()
            timer.start()
            if not self._session_.openService(service_uri): raise RuntimeError(f"Failed to open service {service_uri}")
            service = self._session_.getService(service_uri)
            request = service.createRequest(request_type)
            build_request(request)
            self._session_.sendRequest(request)
            data = []
            while True:
                event = self._session_.nextEvent(500)
                if event.eventType() in (blpapi.Event.PARTIAL_RESPONSE, blpapi.Event.RESPONSE):
                    for msg in event:
                        parsed = self._parse_element_(msg.asElement())
                        if parsed: data.append(parsed)
                if event.eventType() == blpapi.Event.RESPONSE: break
            timer.stop()
            self._log_.info(lambda: f"Execute Operation: {request_type} ({timer.result()})")
            return data
        except Exception as e:
            self._log_.error(lambda: f"Execute Operation: Failed for {request_type}")
            self._log_.exception(lambda: str(e))
            raise