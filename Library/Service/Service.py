import atexit
from typing import Callable

from Library.Statistics import Timer
from Library.Logging import HandlerLoggingAPI

class ServiceAPI:

    def __init__(self, api=None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._api_ = api
        self._guard_ = None
        self._log_: HandlerLoggingAPI = HandlerLoggingAPI(self.__class__.__name__)

    def guarded(self) -> bool:
        return self._guard_ is not None

    def connected(self) -> bool:
        if self._api_ is not None:
            return self._api_.connected()
        raise NotImplementedError(f"{self.__class__.__name__}.connected() is not implemented")

    def _connect_(self, **kwargs) -> None:
        raise NotImplementedError(f"{self.__class__.__name__}._connect_() is not implemented")

    def connect(self, **kwargs):
        if self._api_ is not None:
            return self._api_.connect(**kwargs)
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

    def __enter__(self):
        return self.connect()

    def disconnected(self) -> bool:
        if self._api_ is not None:
            return self._api_.disconnected()
        raise NotImplementedError(f"{self.__class__.__name__}.disconnected() is not implemented")

    def _disconnect_(self) -> None:
        raise NotImplementedError(f"{self.__class__.__name__}._disconnect_() is not implemented")

    def disconnect(self):
        if self._api_ is not None:
            return self._api_.disconnect()
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

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type or exc_val or exc_tb:
            self._log_.exception(lambda: f"Exception type: {exc_type}")
            self._log_.exception(lambda: f"Exception value: {exc_val}")
            self._log_.exception(lambda: f"Traceback: {exc_tb}")
        self.disconnect()
        return not exc_type

    def __del__(self):
        try: self.disconnect()
        except: pass

    def _fetch_(self, fetch: Callable, abort: Callable = None):
        timer = Timer()
        timer.start()
        try:
            self.connect()
            result = fetch()
            return timer, result
        except Exception as e:
            if abort is not None: abort()
            self._log_.error(lambda: "Fetch Operation: Failed")
            self._log_.exception(lambda: str(e))
            raise
        finally:
            timer.stop()

    def _execute_(self, execute: Callable, abort: Callable = None):
        timer = Timer()
        timer.start()
        try:
            self.connect()
            execute()
            return timer
        except Exception as e:
            if abort is not None: abort()
            self._log_.error(lambda: "Execute Operation: Failed")
            self._log_.exception(lambda: str(e))
            raise
        finally:
            timer.stop()