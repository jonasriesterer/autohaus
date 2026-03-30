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

"""Pydantic-Model für die Autohausdaten."""

from typing import Final

from loguru import logger

from autohaus.entity.autohaus import Autohaus
from autohaus.router.adresse_model import AdresseModel
from autohaus.router.auto_model import AutoModel
from autohaus.router.autohaus_update_model import AutohausUpdateModel

__all__ = ["AutohausModel"]


# https://towardsdatascience.com/pydantic-or-dataclasses-why-not-both-convert-between-them-ba382f0f9a9c
class AutohausModel(AutohausUpdateModel):
    """Pydantic-Model für die Autohausendaten."""

    adresse: AdresseModel
    """Die zugehörige Adresse."""
    autos: list[AutoModel]
    """Die Liste der Autos."""

    def to_autohaus(self) -> Autohaus:
        """Konvertierung in ein Autohaus-Objekt für SQLAlchemy.

        :return: Autohaus-Objekt für SQLAlchemy
        :rtype: Autohaus
        """
        logger.debug("self={}", self)
        autohaus_dict = self.to_dict()

        autohaus: Final = Autohaus(**autohaus_dict)
        autohaus.adresse = self.adresse.to_adresse()
        autohaus.autos = [
            auto_model.to_auto() for auto_model in self.autos
        ]
        logger.debug("autohaus={}", autohaus)
        return autohaus
