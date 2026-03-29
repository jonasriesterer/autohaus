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

"""Entity-Klasse für Auto."""

from decimal import Decimal

from sqlalchemy import ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from autohaus.entity.base import Base


class Auto(Base):
    """Entity-Klasse für Auto."""

    __tablename__ = "auto"

    kennzeichen: Mapped[str]
    """Das Kennzeichen."""

    marke: Mapped[str]
    """Die Marke."""

    modell: Mapped[str]
    """Das Modell."""

    baujahr: Mapped[Decimal]
    """Das Baujahr."""

    id: Mapped[int] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )
    """Die generierte ID gemäß der zugehörigen IDENTITY-Spalte."""

    autohaus_id: Mapped[int] = mapped_column(ForeignKey("autohaus.id"))
    """ID des zugehörigen Autohauses als Fremdschlüssel in der DB-Tabelle."""

    autohaus: Mapped[Autohaus] = relationship(  # noqa: F821 # ty: ignore[unresolved-reference] # pyright: ignore[reportUndefinedVariable ]
        back_populates="autos",
    )
    """Das zugehörige transiente Autohaus-Objekt."""

    # __repr__ fuer Entwickler/innen, __str__ fuer User
    def __repr__(self) -> str:
        """Ausgabe des Autos als String ohne die Autohausdaten."""
        return (
            f"Auto(kennzeichen={self.kennzeichen}, marke={self.marke}, "
            + f"modell={self.modell}, baujahr={self.baujahr})"
        )
