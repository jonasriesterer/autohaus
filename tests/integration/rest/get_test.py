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

"""Tests für GET mit Query-Parameter."""

from http import HTTPStatus
from typing import Final

from common_test import ctx, login, rest_url
from httpx import get
from pytest import mark


@mark.rest
@mark.get_request
@mark.parametrize("email", ["info@autohaus-acme.de", "kontakt@motors.com"]) # ACHTUNG: An Test-DB anpassen!
def test_get_by_email(email: str) -> None:
    # arrange
    params = {"email": email}
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(rest_url, params=params, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    content: Final = response_body["content"]
    assert isinstance(content, list)
    assert len(content) == 1
    autohaus = content[0]
    assert autohaus is not None
    assert autohaus.get("email") == email
    assert autohaus.get("id") is not None


@mark.rest
@mark.get_request
@mark.parametrize("email", ["nicht@vorhanden.com", "fake@autohaus.de"])
def test_get_by_email_not_found(email: str) -> None:
    # arrange
    params = {"email": email}
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(rest_url, params=params, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND


@mark.rest
@mark.get_request
@mark.parametrize("teil", ["Auto", "Motor"]) # ACHTUNG: An Test-DB anpassen!
def test_get_by_name(teil: str) -> None:
    # arrange
    params = {"name": teil}
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(rest_url, params=params, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    content: Final = response_body["content"]
    for a in content:
        name = a.get("name")
        assert name is not None and isinstance(name, str)
        assert teil.lower() in name.lower()
        assert a.get("id") is not None


@mark.rest
@mark.get_request
@mark.parametrize("name", ["Notfound Autohaus", "Foo-Bar Motors"])
def test_get_by_name_not_found(name: str) -> None:
    # arrange
    params = {"name": name}
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(rest_url, params=params, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND


@mark.rest
@mark.get_request
@mark.parametrize("teil", ["a", "n"]) # ACHTUNG: An Test-DB anpassen!
def test_get_namen(teil: str) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/namen/{teil}", # Endpoint angepasst!
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    namen: Final = response.json()
    assert isinstance(namen, list)
    assert len(namen) > 0
    for name in namen:
        assert teil in name.lower()


@mark.rest
@mark.get_request
@mark.parametrize("teil", ["xxx", "Abc"])
def test_get_namen_not_found(teil: str) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/namen/{teil}", # Endpoint angepasst!
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND