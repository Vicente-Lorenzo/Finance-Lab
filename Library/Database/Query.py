import re
from typing import Callable
from Library.Utility import PathAPI

class QueryAPI:

    _INTERPOLATION_PARAMETER_TOKEN_ = re.compile(r"::([A-Za-z_]\w*)::")
    _NAMED_PARAMETER_TOKEN_ = re.compile(r":([A-Za-z_]\w*):")
    _POSITIONAL_PARAMETER_TOKEN_ = re.compile(r":\?:")
    _PARAMETER_TOKEN_ = re.compile(rf"(?:{_POSITIONAL_PARAMETER_TOKEN_.pattern})|(?:{_NAMED_PARAMETER_TOKEN_.pattern})")

    def __init__(self, data: str | PathAPI):
        self._query_: str = data.file.read_text() if isinstance(data, PathAPI) else data

    def __call__(self, token: Callable[[int], str], *args, **kwargs) -> tuple[str, tuple | None]:
        query = str(self._query_)
        interpolation_keys = set(self._INTERPOLATION_PARAMETER_TOKEN_.findall(query))
        if interpolation_keys:
            query = self._INTERPOLATION_PARAMETER_TOKEN_.sub(r"{\1}", query)
            query = query.format(**kwargs)
            for k in interpolation_keys:
                kwargs.pop(k, None)
        parameters: list = []
        parameters_index: int = 0
        query_parts: list[str] = []
        query_cursor: int = 0
        named_parameters: dict = dict(kwargs)
        positional_parameters: list = list(args)
        positional_parameters_index: int = 0
        for match in self._PARAMETER_TOKEN_.finditer(query):
            query_parts.append(query[query_cursor:match.start()])
            parameters_index += 1
            query_parts.append(token(parameters_index))
            name = match.group(1)
            if name is not None:
                if name not in named_parameters:
                    raise KeyError(f"Missing named parameter '{name}' for :{name}: placeholder")
                parameters.append(named_parameters[name])
            else:
                if positional_parameters_index >= len(positional_parameters):
                    raise ValueError("Not enough positional parameters for :?: placeholders")
                parameters.append(positional_parameters[positional_parameters_index])
                positional_parameters_index += 1
            query_cursor = match.end()
        query_parts.append(query[query_cursor:])
        query = "".join(query_parts)
        return query, (tuple(parameters) if parameters else None)

    def __repr__(self):
        return self._query_
