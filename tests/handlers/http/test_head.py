from typing import TYPE_CHECKING

import pytest

from starlite import (
    File,
    HttpMethod,
    ImproperlyConfiguredException,
    create_test_client,
    head,
)
from starlite.status_codes import HTTP_200_OK

if TYPE_CHECKING:
    from starlite.response import FileResponse


def test_head_decorator() -> None:
    @head("/")
    def handler() -> None:
        return

    with create_test_client(handler) as client:
        response = client.head("/")
        assert response.status_code == HTTP_200_OK


def test_head_decorator_raises_validation_error_if_body_is_declared() -> None:
    with pytest.raises(ImproperlyConfiguredException):

        @head("/")
        def handler() -> dict:
            return {}


def test_head_decorator_raises_validation_error_if_method_is_passed() -> None:
    with pytest.raises(ImproperlyConfiguredException):

        @head("/", http_method=HttpMethod.HEAD)
        def handler() -> None:
            return


def test_head_decorator_does_not_raise_for_file() -> None:
    @head("/")
    def handler() -> File:
        ...


def test_head_decorator_does_not_raise_for_file_response() -> None:
    @head("/")
    def handler() -> "FileResponse":
        ...
