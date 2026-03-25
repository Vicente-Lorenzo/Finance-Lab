import atexit
from abc import ABC, abstractmethod

from Library.Statistics import Timer
from Library.Logging import HandlerLoggingAPI

class API(ABC):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._guard_ = None
        self._log_ = HandlerLoggingAPI(self.__class__.__name__)

    @abstractmethod
    def connected(self) -> bool:
        raise NotImplementedError

    def disconnected(self) -> bool:
        return not self.connected()

    def guarded(self) -> bool:
        return self._guard_ is not None

    @abstractmethod
    def _connect_(self, **kwargs):
        raise NotImplementedError

    def connect(self, **kwargs):
        try:
            if self.connected():
                self._log_.debug(lambda: "Connect Operation: Skipped (Already Connected)")
                return self
            if not self.disconnected():
                self._log_.warning(lambda: "Connect Operation: Disconnecting (Bad Connection)")
                self.disconnect()
            timer = Timer()
            timer.start()
            self._connect_(**kwargs)
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

    @abstractmethod
    def _disconnect_(self):
        raise NotImplementedError

    def disconnect(self):
        try:
            if self.disconnected():
                self._log_.debug(lambda: "Disconnect Operation: Skipped (Already Disconnected)")
                return self
            timer = Timer()
            timer.start()
            self._disconnect_()
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