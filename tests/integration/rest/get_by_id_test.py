# ruff: noqa: S101, D103
# Copyright (C) 2022 - present Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Tests für GET mit Pfadparameter für die ID."""

from http import HTTPStatus
from typing import Final

from common_test import ctx, login, rest_url
from httpx import get
from pytest import mark


@mark.rest
@mark.get_request
@mark.parametrize("autohaus_id", [100, 101, 102])
def test_get_by_id_admin(autohaus_id: int) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/{autohaus_id}",
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    id_actual: Final = response_body.get("id")
    assert id_actual is not None
    assert id_actual == autohaus_id


@mark.rest
@mark.get_request
@mark.parametrize("autohaus_id", [0, 999999])
def test_get_by_id_not_found(autohaus_id: int) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/{autohaus_id}",
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND


@mark.rest
@mark.get_request
def test_get_by_id_patient() -> None:
    # arrange
    autohaus_id: Final = 100
    token: Final = login(username="autohaus_karlsruhe")
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/{autohaus_id}",
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    autohaus_id_response: Final = response_body.get("id")
    assert autohaus_id_response is not None
    assert autohaus_id_response == autohaus_id


@mark.rest
@mark.get_request
@mark.parametrize("autohaus_id", [100, 101])
def test_get_by_id_admin_explicit(autohaus_id: int) -> None:
    # arrange
    token: Final = login(username="admin")
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/{autohaus_id}",
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    id_actual: Final = response_body.get("id")
    assert id_actual is not None
    assert id_actual == autohaus_id


@mark.rest
@mark.get_request
@mark.parametrize("autohaus_id", [0, 999999])
def test_get_by_id_admin_not_found(autohaus_id: int) -> None:
    # arrange
    token: Final = login(username="admin")
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/{autohaus_id}",
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND


@mark.rest
@mark.get_request
@mark.parametrize("autohaus_id", [100, 101, 102])
def test_get_by_id_ungueltiger_token(autohaus_id: int) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}XXX"}

    # act
    response: Final = get(
        f"{rest_url}/{autohaus_id}",
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@mark.rest
@mark.get_request
@mark.parametrize("autohaus_id", [100, 101, 102])
def test_get_by_id_ohne_token(autohaus_id: int) -> None:
    # act
    response: Final = get(f"{rest_url}/{autohaus_id}", verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@mark.rest
@mark.get_request
@mark.parametrize("autohaus_id,if_none_match", [(100, '"0"'), (101, '"0"')])
def test_get_by_id_etag(autohaus_id: int, if_none_match: str) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-None-Match": if_none_match,
    }

    # act
    response: Final = get(
        f"{rest_url}/{autohaus_id}",
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_MODIFIED
    assert not response.text


@mark.rest
@mark.get_request
@mark.parametrize(
    "autohaus_id,if_none_match", [(100, 'xxx"'), (101, "xxx"), (102, "xxx")]
)  # noqa: E501
def test_get_by_id_etag_invalid(autohaus_id: int, if_none_match: str) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-None-Match": if_none_match,
    }

    # act
    response: Final = get(
        f"{rest_url}/{autohaus_id}",
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    id_actual: Final = response_body.get("id")
    assert id_actual is not None
    assert id_actual == autohaus_id
