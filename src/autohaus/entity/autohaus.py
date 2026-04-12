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

"""Entity-Klasse für Autohausdaten."""

from datetime import date, datetime
from typing import Any, Self

from sqlalchemy import Identity, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from autohaus.entity.adresse import Adresse
from autohaus.entity.auto import Auto
from autohaus.entity.base import Base

# https://docs.python.org/3/library/dataclasses.html
# vgl.: record in Java, data class in Kotlin
# eq=False: __eq__ wird *NICHT* generiert, alternativ: eigene Methode __eq__
# repr=False: __repr__ wird *NICHT* generiert, alternativ: eigene Methode __repr__
# frozen=True: immutable
# slots=True: statt Speicherung in __dict__ -> schnellerer Zugriff, kompakte Speicherung
# https://stackoverflow.com/questions/472000/usage-of-slots
# kw_only=True: Initialisierungs-Fkt darf nur mit "Keyword Arguments" aufgerufen werden
# @dataclass(frozen=True, slots=True, kw_only=True)


# https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html#native-support-for-dataclasses-mapped-as-orm-models
# https://docs.sqlalchemy.org/en/20/orm/dataclasses.html
# "frozen" und "slots" wird in SQLAlchemy noch nicht unterstuetzt
# https://docs.sqlalchemy.org/en/20/core/type_basics.html#generic-camelcase-types
# noinspection PyUnresolvedReferences
class Autohaus(Base):
    """Entity-Klasse für Autohausdaten."""

    __tablename__ = "autohaus"

    # es gibt auch die "Build-in" Funktion id(objekt)
    # https://docs.python.org/3/library/functions.html#id
    # https://stackoverflow.com/questions/15667189/what-is-the-id-function-used-for#answer-15667328
    name: Mapped[str]
    """Der Name."""

    username: Mapped[str]
    """Der Benutzername des Autohauses."""

    email: Mapped[str]
    """Die E-Mail-Adresse des Autohauses."""

    anzahl_fahrzeuge: Mapped[int]
    """Die Anzahl der Fahrzeuge."""

    gruendungsdatum: Mapped[date]
    """Das Gründungsdatum."""

    homepage: Mapped[str | None]
    """Die optionale URL der Homepage."""

    telefonnummer: Mapped[str | None]
    """Die optionale Telefonnummer."""

    id: Mapped[int | None] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )
    """Die generierte ID gemäß der zugehörigen IDENTITY-Spalte."""

    # https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#one-to-one
    # https://docs.sqlalchemy.org/en/20/orm/dataclasses.html#relationship-configuration
    # https://docs.sqlalchemy.org/en/20/orm/relationship_api.html#sqlalchemy.orm.relationship.params.innerjoin
    # https://docs.sqlalchemy.org/en/20/orm/cascades.html
    # https://docs.sqlalchemy.org/en/20/orm/relationship_api.html#sqlalchemy.orm.relationship.params.cascade
    adresse: Mapped[Adresse] = relationship(
        back_populates="autohaus",
        innerjoin=True,
        cascade="save-update, delete",
    )
    """Die in einer 1:1-Beziehung referenzierte Adresse."""

    autos: Mapped[list[Auto]] = relationship(
        back_populates="autohaus",
        cascade="save-update, delete",
    )
    """Die in einer 1:N-Beziehung referenzierten Autos."""

    # https://docs.sqlalchemy.org/en/20/orm/versioning.html#simple-version-counting
    version: Mapped[int] = mapped_column(nullable=False, default=0)
    """Die Versionsnummer für optimistische Synchronisation."""

    # https://docs.sqlalchemy.org/en/20/orm/dataclasses.html#column-defaults
    erzeugt: Mapped[datetime | None] = mapped_column(
        insert_default=func.now(),
        default=None,
    )
    """Der Zeitstempel für das initiale INSERT in die DB-Tabelle."""

    aktualisiert: Mapped[datetime | None] = mapped_column(
        insert_default=func.now(),
        onupdate=func.now(),
        default=None,
    )
    """Der Zeitstempel vom letzen UPDATE in der DB-Tabelle."""

    # https://docs.sqlalchemy.org/en/20/orm/versioning.html#simple-version-counting
    __mapper_args__ = {"version_id_col": version}

    def set(self, autohaus: Self) -> None:
        """Primitive Attributwerte überschreiben, z.B. vor DB-Update.

        :param autohaus: Autohaus-Objekt mit den aktuellen Daten
        """
        self.name = autohaus.name
        self.anzahl_fahrzeuge = autohaus.anzahl_fahrzeuge
        self.gruendungsdatum = autohaus.gruendungsdatum
        self.homepage = autohaus.homepage
        self.telefonnummer = autohaus.telefonnummer

    def __eq__(self, other: Any) -> bool:
        """Vergleich auf Gleicheit, ohne Joins zu verursachen."""
        # Vergleich der Referenzen: id(self) == id(other)
        if self is other:
            return True
        if not isinstance(other, type(self)):
            return False
        return self.id is not None and self.id == other.id

    def __hash__(self) -> int:
        """Hash-Funktion anhand der ID, ohne Joins zu verursachen."""
        return hash(self.id) if self.id is not None else hash(type(self))

    # __repr__ fuer Entwickler/innen, __str__ fuer User
    def __repr__(self) -> str:
        """Ausgabe eines Autohauses als String, ohne Joins zu verursachen."""
        return (
            f"A(id={self.id}, version={self.version}, "
            + f"name={self.name}, username={self.username}, email={self.email}, "
            + f"anzahl_fahrzeuge={self.anzahl_fahrzeuge}, "
            + f"gruendungsdatum={self.gruendungsdatum}, homepage={self.homepage}, "
            + f"telefonnummer={self.telefonnummer}"
            + f"erzeugt={self.erzeugt}, aktualisiert={self.aktualisiert})"
        )
