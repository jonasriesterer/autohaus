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

"""Tests für PUT."""

from http import HTTPStatus
from typing import Final

from common_test import ctx, login, rest_url
from httpx import put
from pytest import mark

EMAIL_UPDATE: Final = "update@autohaus-acme.de.put"
HOMEPAGE_UPDATE: Final = "https://www.acme-autohaus.ch.put"


@mark.rest
@mark.put_request
def test_put() -> None:
    # arrange
    autohaus_id: Final = 101
    if_match: Final = '"0"'
    geaendertes_autohaus: Final = {
        "name": "Autohaus Update",
        "email": EMAIL_UPDATE,
        "username": "testput",
        "anzahl_fahrzeuge": 99,
        "gruendungsdatum": "2022-01-09",
        "homepage": HOMEPAGE_UPDATE,
        "telefonnummer": "0721987654",
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{autohaus_id}",
        json=geaendertes_autohaus,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert not response.text


@mark.rest
@mark.put_request
def test_put_invalid() -> None:
    # arrange
    autohaus_id: Final = 101
    geaendertes_autohaus_invalid: Final = {
        "name": "a",
        "email": "falsche_email_put@",
        "username": "testput",
        "anzahl_fahrzeuge": -10,
        "gruendungsdatum": "2022-02-04",
        "homepage": "https://?!",
        "telefonnummer": "0721987654",
    }
    token: Final = login()
    assert token is not None
    headers = {
        "If-Match": '"0"',
        "Authorization": f"Bearer {token}",
    }

    # act
    response: Final = put(
        f"{rest_url}/{autohaus_id}",
        json=geaendertes_autohaus_invalid,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "email" in response.text
    assert "anzahl_fahrzeuge" in response.text
    assert "homepage" in response.text


@mark.rest
@mark.put_request
def test_put_nicht_vorhanden() -> None:
    # arrange
    autohaus_id: Final = 999999
    if_match: Final = '"0"'
    geaendertes_autohaus: Final = {
        "name": "Autohaus Update",
        "email": EMAIL_UPDATE,
        "username": "testput",
        "anzahl_fahrzeuge": 99,
        "gruendungsdatum": "2022-01-03",
        "homepage": HOMEPAGE_UPDATE,
        "telefonnummer": "0721987654",
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{autohaus_id}",
        json=geaendertes_autohaus,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND


@mark.rest
@mark.put_request
def test_put_ohne_versionsnr() -> None:
    # arrange
    autohaus_id: Final = 101
    geaendertes_autohaus: Final = {
        "name": "Autohaus Update",
        "email": EMAIL_UPDATE,
        "username": "testput",
        "anzahl_fahrzeuge": 99,
        "gruendungsdatum": "2022-01-03",
        "homepage": HOMEPAGE_UPDATE,
        "telefonnummer": "0721987654",
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
    }

    # act
    response: Final = put(
        f"{rest_url}/{autohaus_id}",
        json=geaendertes_autohaus,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_REQUIRED


@mark.rest
@mark.put_request
def test_put_alte_versionsnr() -> None:
    # arrange
    autohaus_id: Final = 101
    if_match: Final = '"-1"'
    geaendertes_autohaus: Final = {
        "name": "Autohaus Update",
        "email": EMAIL_UPDATE,
        "username": "testput",
        "anzahl_fahrzeuge": 99,
        "gruendungsdatum": "2022-01-03",
        "homepage": HOMEPAGE_UPDATE,
        "telefonnummer": "0721987654",
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{autohaus_id}",
        json=geaendertes_autohaus,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_FAILED


@mark.rest
@mark.put_request
def test_put_ungueltige_versionsnr() -> None:
    # arrange
    autohaus_id: Final = 101
    if_match: Final = '"xy"'
    geaendertes_autohaus: Final = {
        "name": "Autohaus Update",
        "email": EMAIL_UPDATE,
        "username": "testput",
        "anzahl_fahrzeuge": 99,
        "gruendungsdatum": "2022-01-03",
        "homepage": HOMEPAGE_UPDATE,
        "telefonnummer": "0721987654",
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{autohaus_id}",
        json=geaendertes_autohaus,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_FAILED
    assert not response.text


@mark.rest
@mark.put_request
def test_put_versionsnr_ohne_quotes() -> None:
    # arrange
    autohaus_id: Final = 101
    if_match: Final = "0"
    geaendertes_autohaus: Final = {
        "name": "Autohaus Update",
        "email": EMAIL_UPDATE,
        "username": "testput",
        "anzahl_fahrzeuge": 99,
        "gruendungsdatum": "2022-01-03",
        "homepage": HOMEPAGE_UPDATE,
        "telefonnummer": "0721987654",
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{autohaus_id}",
        json=geaendertes_autohaus,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_FAILED
