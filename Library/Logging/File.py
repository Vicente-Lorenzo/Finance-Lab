from pathlib import Path
from io import TextIOWrapper

from Library.Logging import VerboseLevel, BufferLoggingAPI
from Library.Utility import inspect_file

class FileLoggingAPI(BufferLoggingAPI):

    _dir_path_: Path = None
    _file_name_: str = None
    _file_extension_: str = None
    _file_path_: Path = None
    _file_: TextIOWrapper = None

    @classmethod
    def _setup_class_(cls) -> None:
        super()._setup_class_()
        cls.set_dir_path(inspect_file("Logs", resolve=True))
        cls.set_file_extension(file_extension="text.log")

    @classmethod
    def set_dir_path(cls, dir_path: Path) -> None:
        cls._dir_path_ = dir_path

    @classmethod
    def set_file_name(cls, file_name: str) -> None:
        cls._file_name_ = file_name

    @classmethod
    def set_file_extension(cls, file_extension: str) -> None:
        cls._file_extension_ = file_extension

    @classmethod
    def get_file_hyperlink(cls) -> str:
        return cls._file_path_.as_uri()

    @classmethod
    def _output_log_(cls, verbose: VerboseLevel, log: str) -> None:
        return cls._buffer_pushone_(log=log + "\n")

    @staticmethod
    def _format_file_name_(file_name: str):
        if not file_name: return file_name
        file_name = file_name.replace(' ', '-')
        file_name = file_name.replace('/', '-')
        file_name = file_name.replace('\\', '-')
        file_name = file_name.replace(':', '')
        return file_name

    @classmethod
    def _enter_(cls):
        now = cls.now()
        unique_date = now.strftime("%Y-%m-%d")
        unique_time = now.strftime("%H-%M-%S")
        tokens = []
        if cls._user_info_:
            tokens.append(cls._format_file_name_(file_name=cls._user_info_))
        if cls._host_info_:
            tokens.append(cls._format_file_name_(file_name=cls._host_info_))
        if cls._exec_info_:
            tokens.append(cls._format_file_name_(file_name=cls._exec_info_))
        tokens.append(cls._format_file_name_(file_name=unique_date))
        tokens.append(cls._format_file_name_(file_name=unique_time))
        if cls._file_name_:
            tokens.append(cls._format_file_name_(file_name=cls._file_name_))
        if cls._path_info_:
            tokens.append(cls._format_file_name_(file_name=cls._path_info_))
        file_name = "__".join(tokens)
        cls._file_path_ = cls._dir_path_ / f"{file_name}.{cls._file_extension_}"
        if not cls._dir_path_.exists():
            cls._dir_path_.mkdir(parents=True, exist_ok=True)
        cls._file_ = cls._file_path_.open("w")
        cls.disable_entering()

    @classmethod
    def _exit_(cls):
        logs = cls._buffer_pullall_()
        cls._file_.writelines(logs)
        cls._file_.close()
        cls.enable_entering()
