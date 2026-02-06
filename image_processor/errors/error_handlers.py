from collections import defaultdict
from typing import Union

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_CONTENT


async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse({"errors": [exc.detail]}, status_code=exc.status_code)


async def http422_error_handler(
        _: Request,
        exc: Union[RequestValidationError, ValidationError],
) -> JSONResponse:
    reformatted_message = defaultdict(list)
    for pydantic_error in exc.errors():
        loc, msg = pydantic_error['loc'], pydantic_error['msg']
        filtered_loc = loc[1:] if loc[0] in ('body', 'query', 'path') else loc
        field_string = ".".join([str(i) for i in filtered_loc])
        reformatted_message[field_string].append(msg)

    return JSONResponse(
        {"errors": reformatted_message},
        status_code=HTTP_422_UNPROCESSABLE_CONTENT,
    )
