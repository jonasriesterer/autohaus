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

"""Pydantic-Model zum Aktualisieren von Autohausdaten."""

from datetime import date
from typing import Annotated, Any

from loguru import logger
from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, StringConstraints

from autohaus.entity.autohaus import Autohaus

__all__ = ["AutohausUpdateModel"]


class AutohausUpdateModel(BaseModel):
    """Pydantic-Model zum Aktualisieren von Autohausdaten."""

    # https://docs.pydantic.dev/latest/usage/types
    name: Annotated[str, StringConstraints(max_length=64)]
    """Der Name."""
    username: Annotated[str, StringConstraints(max_length=64)]
    """Der Benutzername des Autohauses."""
    email: EmailStr
    """Die E-Mail-Adresse des Autohauses."""
    anzahl_fahrzeuge: Annotated[int, Field(ge=1)]
    """Die Anzahl der Fahrzeuge."""
    gruendungsdatum: date
    """Das Gründungsdatum."""
    homepage: HttpUrl | None = None
    """Die optionale URL der Homepage."""
    telefonnummer: Annotated[str, StringConstraints(max_length=32)] | None = None
    """Die Telefonnummer."""

    model_config = ConfigDict(
        # Beispiel fuer OpenAPI
        # https://fastapi.tiangolo.com/tutorial/schema-extra-example
        json_schema_extra={
            "example": {
                "name": "Test",
                "username": "autohaus_test",
                "email": "kontakt@autohaus-test.de",
                "anzahl_fahrzeuge": 10,
                "gruendungsdatum": "2023-01-31",
                "homepage": "https://test.rest",
                "telefonnummer": "+49 123 456789",
            },
        }
    )

    def to_dict(self) -> dict[str, Any]:
        """Konvertierung der primitiven Attribute in ein Dictionary.

        :return: Dictionary mit den primitiven Autohaus-Attributen
        :rtype: dict[str, Any]
        """
        # Model von Pydantic in ein Dictionary konvertieren
        # https://docs.pydantic.dev/latest/concepts/serialization
        autohaus_dict = self.model_dump()
        autohaus_dict["id"] = None
        autohaus_dict["adresse"] = None
        autohaus_dict["autos"] = []
        autohaus_dict["erzeugt"] = None
        autohaus_dict["aktualisiert"] = None

        # HttpUrl ist ungeeignet fuer SQLAlchemy
        autohaus_dict["homepage"] = str(autohaus_dict["homepage"])
        return autohaus_dict

    def to_autohaus(self) -> Autohaus:
        """Konvertierung in ein Autohaus-Objekt für SQLAlchemy.

        :return: Autohaus-Objekt für SQLAlchemy
        :rtype: Autohaus
        """
        logger.debug("self={}", self)
        # Model von Pydantic in ein Dictionary konvertieren
        # https://docs.pydantic.dev/latest/concepts/serialization
        autohaus_dict = self.to_dict()

        # double star operator = double asterisk operator:
        # Dictionary auspacken als Schluessel-Wert-Paare
        # -> Namen der Schluessel = Namen der Funktionsargumente
        # https://stackoverflow.com/questions/36901/what-does-double-star-asterisk-and-star-asterisk-do-for-parameters
        # https://docs.python.org/3/reference/expressions.html#dictionary-displays
        autohaus = Autohaus(**autohaus_dict)
        logger.debug("autohaus={}", autohaus)
        return autohaus
