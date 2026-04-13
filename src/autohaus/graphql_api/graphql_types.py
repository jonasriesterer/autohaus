# Copyright (C) 2023 - present Juergen Zimmermann, Hochschule Karlsruhe
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

"""Schema für GraphQL."""

from datetime import date
from decimal import Decimal

import strawberry

__all__ = [
    "AdresseInput",
    "AutoInput",
    "AutohausInput",
    "CreatePayload",
    "LoginResult",
    "Suchparameter",
]

# SDL (schema definition language):
# type Autohaus {
#     id: ID!
#     name: String!
#     username: String!
#     email: String!
#     anzahlFahrzeuge: Int!
#     gruendungsdatum: Date!
#     homepage: String
#     telefonnummer: String
#     adresse: Adresse!
#     autos: [Auto!]!
# }
# input AutohausInput {
#     name: String!
#     username: String!
#     email: String!
#     anzahlFahrzeuge: Int!
#     gruendungsdatum: Date!
#     homepage: String
#     telefonnummer: String
#     adresse: AdresseInput!
#     autos: [AutoInput!]!
# }
# input Suchparameter {
#     name: String
#     email: String
# }


@strawberry.input
class Suchparameter:
    """Suchparameter für die Suche nach Autohausdaten."""

    name: str | None = None
    """Name des Autohauses als Suchkriterium."""

    email: str | None = None
    """Emailadresse als Suchkriterium."""


@strawberry.input
class AdresseInput:
    """Adresse eines neuen Autohauses."""

    plz: str
    """Postleitzahl des neuen Autohauses."""

    ort: str
    """Ort des neuen Autohauses."""

    land: str
    """Land des neuen Autohauses."""


@strawberry.input
class AutoInput:
    """Eingabedaten für ein Auto."""

    kennzeichen: str
    """Kennzeichen des Autos."""

    marke: str
    """Marke des Autos."""

    modell: str
    """Modell des Autos."""

    baujahr: Decimal
    """Baujahr des Autos."""


@strawberry.input
class AutohausInput:
    """Daten für ein neues Autohaus."""

    name: str
    """Name des Autohauses."""

    username: str
    """Benutzername des Autohauses."""

    email: str
    """Emailadresse des Autohauses."""

    anzahl_fahrzeuge: int
    """Anzahl der Fahrzeuge im Autohaus."""

    gruendungsdatum: date
    """Gründungsdatum des Autohauses."""

    homepage: str | None
    """Optionale Homepage des Autohauses."""

    telefonnummer: str | None
    """Optionale Telefonnummer des Autohauses."""

    adresse: AdresseInput
    """Adresse des Autohauses."""

    autos: list[AutoInput]
    """Liste der Autos im Autohaus."""


@strawberry.type
class CreatePayload:
    """Resultat-Typ, wenn ein neues Autohaus angelegt wurde."""

    id: int
    """ID des neu angelegten Autohauses."""


@strawberry.type
class LoginResult:
    """Resultat-Typ, wenn ein Login erfolgreich war."""

    token: str
    """Token des eingeloggten Users."""
    expiresIn: str  # noqa: N815  # NOSONAR
    """Gültigkeitsdauer des Tokens."""
    roles: list[str]
    """Rollen des eingeloggten Users."""
