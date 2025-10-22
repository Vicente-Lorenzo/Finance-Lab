from pathlib import Path

class PathAPI:

    def __init__(self, path: str):
        self.module = Path(__file__).resolve().parent
        self.path = self.module / path

    def exists(self) -> bool:
        return self.path.exists()

    def read_text(self, **kwargs) -> str:
        return self.path.read_text(**kwargs)

    def read_bytes(self) -> bytes:
        return self.path.read_bytes()

    def write_bytes(self, data: bytes):
        self.path.write_bytes(data)

    def write_text(self, data: str, **kwargs):
        self.path.write_text(data, **kwargs)
