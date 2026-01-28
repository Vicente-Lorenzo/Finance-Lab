import re
from typing import Callable
from Library.Utility import PathAPI

class QueryAPI:

    _INTERPOLATION_PARAMETER_TOKEN_ = re.compile(r"::([A-Za-z_]\w*)::")
    _NAMED_PARAMETER_TOKEN_ = re.compile(r":([A-Za-z_]\w*):")
    _POSITIONAL_PARAMETER_TOKEN_ = re.compile(r":\?:")
    _PARAMETER_TOKEN_ = re.compile(rf"{_POSITIONAL_PARAMETER_TOKEN_.pattern}|{_NAMED_PARAMETER_TOKEN_.pattern}")

    def __init__(self, data: str | PathAPI):
        self._query_: str = data.file.read_text() if isinstance(data, PathAPI) else data

    def compile(self, token: Callable[[int], str], **kwargs) -> tuple[str, list[int | str]]:
        query = str(self._query_)
        interpolation = set(self._INTERPOLATION_PARAMETER_TOKEN_.findall(query))
        if interpolation:
            missing = interpolation.difference(kwargs.keys())
            if missing:
                k = next(iter(missing))
                raise KeyError(f"Missing interpolation parameter '{k}' for ::{k}:: placeholder")
            query = self._INTERPOLATION_PARAMETER_TOKEN_.sub(r"{\1}", query)
            query = query.format(**kwargs)
        configuration: list[int | str] = []
        parameters_index: int = 0
        positional_index: int = 0
        query_parts: list[str] = []
        query_cursor: int = 0
        for match in self._PARAMETER_TOKEN_.finditer(query):
            query_parts.append(query[query_cursor:match.start()])
            parameters_index += 1
            query_parts.append(token(parameters_index))
            name = match.group(1)
            if name is not None:
                configuration.append(name)
            else:
                configuration.append(positional_index)
                positional_index += 1
            query_cursor = match.end()
        query_parts.append(query[query_cursor:])
        query = "".join(query_parts)
        return query, configuration

    @staticmethod
    def bind(configuration, *args, **kwargs) -> tuple:
        args = args or ()
        kwargs = kwargs or {}
        parameters = []
        for spec in configuration:
            match spec:
                case int() as i:
                    if i >= len(args):
                        raise ValueError("Not enough positional parameters for :?: placeholders")
                    parameters.append(args[i])
                case str() as k:
                    if k not in kwargs:
                        raise KeyError(f"Missing named parameter '{k}' for :{k}: placeholder")
                    parameters.append(kwargs[k])
        return tuple(parameters)

    def __call__(self, token: Callable[[int], str], *args, **kwargs) -> tuple[str, list[int | str], tuple | None]:
        query, configuration = self.compile(token, **kwargs)
        parameters = self.bind(configuration, *args, **kwargs) if configuration else None
        return query, configuration, parameters

    def __repr__(self):
        return repr(self._query_)
