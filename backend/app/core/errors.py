from dataclasses import dataclass


@dataclass(slots=True)
class AppError(Exception):
    error_code: str
    message: str

    def __str__(self) -> str:
        return f"{self.error_code}: {self.message}"
