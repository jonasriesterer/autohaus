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

"""DTO-Klasse für Autohaus daten, insbesondere ohne Decorators für SQLAlchemy."""

from dataclasses import dataclass
from datetime import date

import strawberry

from autohaus.entity import Autohaus
from autohaus.service.adresse_dto import AdresseDTO

__all__ = ["AutohausDTO"]


# Mit der Funktion asdict() kann ein Objekt einfach in ein dict konvertiert werden
# init=True (default): __init__ fuer die "member variables" wird generiert
# eq=True (default): __eq__ wird generiert
# unsafe_hash=False (default): __hash__ passend zu __eq__ wird generiert
# repr=True (default): __repr__ wird generiert
# frozen=False (default): mutable
# kw_only=False (default): Initialisierungs-Fkt auch ohne "Keyword Arguments" aufrufen
# slots=False (default): __dict__ zur Speicherung statt slots
# slots: schnellerer Zugriff, kompakte Speicherung
# https://stackoverflow.com/questions/472000/usage-of-slots
@dataclass(eq=False, slots=True, kw_only=True)
# Strawberry konvertiert automatisch zwischen snake_case (Python) und camelCase (Schema)
@strawberry.type
class AutohausDTO:
    """DTO-Klasse für aus gelesene oder gespeicherte Autohausdaten: ohne Decorators."""

    id: int
    version: int
    name: str
    anzahl_fahrzeuge: int
    gruendungsdatum: date
    homepage: str | None
    telefonnummer: str | None
    adresse: AdresseDTO

    # asdict kann nicht verwendet werden: Rueckwaertsverweise Autohaus - Adresse
    # https://github.com/python/cpython/issues/94345
    def __init__(self, autohaus: Autohaus):
        """Initialisierung von AutohausDTO durch ein Entity-Objekt von Autohaus.

        :param autohaus: Autohaus-Objekt mit Decorators zu SQLAlchemy
        """
        autohaus_id = autohaus.id
        self.id = autohaus_id if autohaus_id is not None else -1
        self.version = autohaus.version
        self.name = autohaus.name
        self.anzahl_fahrzeuge = autohaus.anzahl_fahrzeuge
        self.gruendungsdatum = autohaus.gruendungsdatum
        self.homepage = autohaus.homepage
        self.telefonnummer = autohaus.telefonnummer
        self.adresse = AdresseDTO(autohaus.adresse)
        
