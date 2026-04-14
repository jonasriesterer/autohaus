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

"""Tests für Mutations mit GraphQL."""

from http import HTTPStatus
from typing import Final

from common_test import ctx, graphql_url
from httpx import post
from pytest import mark


@mark.graphql
@mark.mutation
def test_create() -> None:
    # arrange
    query: Final = {
        "query": """
            mutation {
                create(
                    autohausInput: {
                        name: "Autohaus Graphql"
                        email: "testgraphql@autohaus.de"
                        anzahlFahrzeuge: 42
                        gruendungsdatum: "2022-01-31"
                        homepage: "https://graphql.de"
                        telefonnummer: "0721123456"
                        adresse: {
                            plz: "99999"
                            ort: "Mutationort"
                            land: "Deutschland"
                        }
                        autos: [
                            {
                                kennzeichen: "KA-AB 12"
                                marke: "VW"
                                modell: "Golf"
                                baujahr: 2020
                            }
                        ]
                        username: "testgraphql"
                    }
                ) {
                    id
                }
            }
        """,
    }

    # act
    response: Final = post(graphql_url, json=query, verify=ctx)

    # assert
    assert response is not None
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    assert isinstance(response_body["data"]["create"]["id"], int)
    assert response_body.get("errors") is None


@mark.graphql
@mark.mutation
def test_create_invalid() -> None:
    # arrange
    query: Final = {
        "query": """
            mutation {
                create(
                    autohausInput: {
                        name: ""
                        email: "falsche_email@"
                        anzahlFahrzeuge: -5
                        gruendungsdatum: "2022-01-31"
                        homepage: "https://?!"
                        telefonnummer: "0721123456"
                        adresse: {
                            plz: "1234"
                            ort: "Testort"
                            land: "Deutschland"
                        }
                        autos: []
                        username: "testgraphql"
                    }
                ) {
                    id
                }
            }
        """,
    }

    # act
    response: Final = post(graphql_url, json=query, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    assert response_body["data"] is None
    errors: Final = response_body["errors"]
    assert isinstance(errors, list)
    assert len(errors) > 0  