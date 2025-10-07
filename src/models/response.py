from dataclasses import dataclass


@dataclass
class Response:
    id: int
    message: str | None = None
