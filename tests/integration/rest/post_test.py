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

"""Tests für POST."""

from http import HTTPStatus
from re import search
from typing import Final

from common_test import ctx, rest_url
from httpx import post
from pytest import mark

token: str | None


@mark.rest
@mark.post_request
def test_post() -> None:
    # arrange
    neues_autohaus: Final = {
        "name": "Autohaus Rest",
        "email": "testrest@autohaus.de",
        "anzahl_fahrzeuge": 42,
        "gruendungsdatum": "2022-02-01",
        "homepage": "https://rest-autohaus.de",
        "telefonnummer": "0721123456",
        "adresse": {"plz": "99999", "ort": "Restort", "land": "Deutschland"},
        "autos": [{"kennzeichen": "KARE123", "marke": "VW", "modell": "Golf", "baujahr": 2020}],  # noqa: E501
        "username": "testrest",
    }
    headers = {"Content-Type": "application/json"}

    # act
    response: Final = post(
        rest_url,
        json=neues_autohaus,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.CREATED
    location: Final = response.headers.get("Location")
    assert location is not None
    int_pattern: Final = "[1-9][0-9]*$"
    assert search(int_pattern, location) is not None
    assert not response.text


@mark.rest
@mark.post_request
def test_post_invalid() -> None:
    # arrange
    neues_autohaus_invalid: Final = {
        "name": "a",
        "email": "falsche_email@",
        "anzahl_fahrzeuge": -5,
        "gruendungsdatum": "2022-02-01",
        "homepage": "https://?!",
        "telefonnummer": "0721123456",
        "adresse": {"plz": "1234", "ort": "Restort", "land": "Deutschland"},
        "autos": [],
        "username": "testrestinvalid",
    }
    headers = {"Content-Type": "application/json"}

    # act
    response: Final = post(
        rest_url,
        json=neues_autohaus_invalid,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    body = response.text
    assert "email" in body
    assert "anzahl_fahrzeuge" in body
    assert "homepage" in body
    assert "plz" in body


@mark.rest
@mark.post_request
def test_post_email_exists() -> None:
    # arrange
    email_exists: Final = "kontakt@autohaus-karlsruhe.de"  # WIP
    neues_autohaus: Final = {
        "name": "Autohaus Rest",
        "email": email_exists,
        "anzahl_fahrzeuge": 42,
        "gruendungsdatum": "2022-02-01",
        "homepage": "https://rest-autohaus.de",
        "telefonnummer": "0721123456",
        "adresse": {"plz": "99999", "ort": "Restort", "land": "Deutschland"},
        "autos": [{"kennzeichen": "KARE123", "marke": "VW", "modell": "Golf", "baujahr": 2020}],  # noqa: E501
        "username": "emailexists",
    }
    headers = {"Content-Type": "application/json"}

    # act
    response: Final = post(
        rest_url,
        json=neues_autohaus,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert email_exists in response.text


@mark.rest
@mark.post_request
def test_post_invalid_json() -> None:
    # arrange
    json_invalid: Final = '{"name" "Autohaus"}'
    headers = {"Content-Type": "application/json"}

    # act
    response: Final = post(
        rest_url,
        json=json_invalid,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "should be a valid dictionary" in response.text
