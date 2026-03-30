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

"""Pydantic-Model für die Autos."""

from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from autohaus.entity.auto import Auto

__all__ = ["AutoModel"]


class AutoModel(BaseModel):
    """Pydantic-Model für die auto_dict."""

    kennzeichen: Annotated[str, StringConstraints(max_length=8)]
    """Das Kennzeichen."""
    marke: Annotated[str, StringConstraints(max_length=64)]
    """Die Marke."""
    modell: Annotated[str, StringConstraints(max_length=64)]
    """Das Modell."""
    baujahr: Decimal
    """Das Baujahr."""

    model_config = ConfigDict(
        # Beispiel fuer OpenAPI
        # https://fastapi.tiangolo.com/tutorial/schema-extra-example
        json_schema_extra={
            "example": {
                "kennzeichen": "ABCD1234",
                "marke": "Porsche",
                "modell": "911 Turbo S",
                "baujahr": "2024",
            },
        }
    )

    def to_auto(self) -> Auto:
        """Konvertierung in ein Auto-Objekt für SQLAlchemy.

        :return: Auto-Objekt für SQLAlchemy
        :rtype: Auto
        """
        # Model von Pydantic in ein Dictionary konvertieren
        # https://docs.pydantic.dev/latest/concepts/serialization
        auto_dict = self.model_dump()
        auto_dict["id"] = None
        auto_dict["autohaus_id"] = None
        auto_dict["autohaus"] = None

        # double star operator = double asterisk operator:
        # Dictionary auspacken als Schluessel-Wert-Paare
        # -> Namen der Schluessel = Namen der Funktionsargumente
        # https://stackoverflow.com/questions/36901/what-does-double-star-asterisk-and-star-asterisk-do-for-parameters
        # https://docs.python.org/3/reference/expressions.html#dictionary-displays
        return Auto(**auto_dict)
