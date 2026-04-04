from __future__ import annotations

import blpapi
from datetime import datetime

from Library.Statistics import Timer
from Library.Dataframe import pd, pl
from Library.Service import ServiceAPI

class IntradayAPI(ServiceAPI):

    def bars(self,
             security: str,
             start: datetime,
             end: datetime = None,
             interval: int = 1,
             type: str = "TRADE") -> pd.DataFrame | pl.DataFrame:
        try:
            self.connect()
            service = self._api_._service_("//blp/refdata")
            request = service.createRequest("IntradayBarRequest")
            request.set("security", security)
            request.set("eventType", type)
            request.set("interval", interval)
            request.set("startDateTime", start)
            if end: request.set("endDateTime", end)
            correlation = blpapi.CorrelationId(security)
            self._api_._session_.sendRequest(request, correlationId=correlation)
            timer = Timer()
            timer.start()
            data = []
            while True:
                event = self._api_._session_.nextEvent(1000)
                if event.eventType() in [blpapi.Event.RESPONSE, blpapi.Event.PARTIAL_RESPONSE]:
                    for message in event:
                        if not message.hasElement("barData"): continue
                        bar_data = message.getElement("barData")
                        if not bar_data.hasElement("barTickData"): continue
                        bars = bar_data.getElement("barTickData")
                        for i in range(bars.numValues()):
                            bar = bars.getValueAsElement(i)
                            row = {"Security": security}
                            for j in range(bar.numElements()):
                                element = bar.getElement(j)
                                name = str(element.name())
                                row[name.capitalize() if name == "time" else name] = element.getValue()
                            data.append(row)
                    if event.eventType() == blpapi.Event.RESPONSE: break
                elif event.eventType() == blpapi.Event.TIMEOUT: break
            timer.stop()
            df = self.frame(data).drop_nulls(subset=["Date"]) if data else self.frame(data)
            self._log_.info(lambda: f"Bars Operation: Fetched {len(df)} bars ({timer.result()})")
            return df
        except Exception as e:
            self._log_.error(lambda: "Bars Operation: Failed")
            self._log_.exception(lambda: str(e))
            raise

    def ticks(self,
              security: str,
              start: datetime,
              end: datetime = None,
              types: str | list[str] = "TRADE") -> pd.DataFrame | pl.DataFrame:
        try:
            self.connect()
            service = self._api_._service_("//blp/refdata")
            request = service.createRequest("IntradayTickRequest")
            request.set("security", security)
            request.set("eventTypes", [types] if isinstance(types, str) else types)
            request.set("startDateTime", start)
            if end: request.set("endDateTime", end)
            request.set("includeConditionCodes", True)
            correlation = blpapi.CorrelationId(security)
            self._api_._session_.sendRequest(request, correlationId=correlation)
            timer = Timer()
            timer.start()
            data = []
            while True:
                event = self._api_._session_.nextEvent(1000)
                if event.eventType() in [blpapi.Event.RESPONSE, blpapi.Event.PARTIAL_RESPONSE]:
                    for message in event:
                        if not message.hasElement("tickData"): continue
                        tick_data = message.getElement("tickData")
                        if not tick_data.hasElement("tickData"): continue
                        ticks = tick_data.getElement("tickData")
                        for i in range(ticks.numValues()):
                            tick = ticks.getValueAsElement(i)
                            row = {"Security": security}
                            for j in range(tick.numElements()):
                                element = tick.getElement(j)
                                name = str(element.name())
                                row[name.capitalize() if name == "time" else name] = element.getValue()
                            data.append(row)
                    if event.eventType() == blpapi.Event.RESPONSE: break
                elif event.eventType() == blpapi.Event.TIMEOUT: break
            timer.stop()
            df = self.frame(data).drop_nulls(subset=["Time"]) if data else self.frame(data)
            self._log_.info(lambda: f"Ticks Operation: Fetched {len(df)} ticks ({timer.result()})")
            return df
        except Exception as e:
            self._log_.error(lambda: "Ticks Operation: Failed")
            self._log_.exception(lambda: str(e))
            raise