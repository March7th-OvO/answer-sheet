from collections.abc import Sequence
from typing import Any

from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError


def map_request_validation_error(exc: RequestValidationError | ValidationError) -> tuple[str, str]:
    return map_validation_errors(exc.errors())


def map_validation_errors(errors: Sequence[dict[str, Any]]) -> tuple[str, str]:
    for error in errors:
        location = tuple(str(part) for part in error.get("loc", ()))
        message = error.get("msg", "")

        if "optionCount must equal options length" in message:
            return ("OPTION_COUNT_MISMATCH", "optionCount 必须等于 options.length")

        if "pageSize" in location and error.get("type") == "literal_error":
            return ("UNSUPPORTED_PAGE_SIZE", "MVP 阶段仅支持 A4 纸张")

    return ("INVALID_REQUEST", "请求参数不合法")
