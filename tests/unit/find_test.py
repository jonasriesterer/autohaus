# ruff: noqa: S101, D103, ARG005
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

"""Unit-Tests für find() von AutohausService."""

from datetime import date
from typing import TYPE_CHECKING

from pytest import fixture, mark, raises

from autohaus.entity import Adresse, Autohaus
from autohaus.repository import Pageable
from autohaus.service import NotFoundError

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@fixture
def session_mock(mocker: MockerFixture):
    session = mocker.Mock()
    # Patching von "with Session() as session:" in autohaus_service.py
    mocker.patch(
        "autohaus.service.autohaus_service.Session",
        return_value=mocker.MagicMock(
            __enter__=lambda self: session,
            __exit__=lambda self, exc_type, exc, tb: None,
        ),
    )
    return session


@mark.unit
@mark.unit_find
def test_find_by_name(autohaus_service, session_mock) -> None:
    # Arrange
    name = "Mocktest Autohaus"
    autohaus_id = 1
    adresse_mock = Adresse(
        id=1,
        plz="11111",
        ort="Mockort",
        land="Deutschland",
        autohaus_id=autohaus_id,
        autohaus=None,
    )
    autohaus_mock = Autohaus(
        id=autohaus_id,
        name=name,
        email="mock@email.test",
        username="mocktest",
        anzahl_fahrzeuge=50,
        gruendungsdatum=date(2025, 1, 31),
        homepage="https://www.test.de",
        telefonnummer="0123456789",  # noqa: FURB156
        adresse=adresse_mock,
        autos=[],
    )
    adresse_mock.autohaus = autohaus_mock
    suchparameter = {"name": name}
    pageable = Pageable(size=5, number=0)
    # session.scalars(select(Autohaus)...).all()
    session_mock.scalars.return_value.all.return_value = [autohaus_mock]

    # Act
    autohaus_slice = autohaus_service.find(
        suchparameter=suchparameter, pageable=pageable
    )

    # Assert
    assert len(autohaus_slice.content) == 1
    assert autohaus_slice.content[0].name == name


@mark.unit
@mark.unit_find
def test_find_by_name_not_found(autohaus_service, session_mock) -> None:
    # Arrange
    name = "Notfound Autohaus"
    suchparameter = {"name": name}
    pageable = Pageable(size=5, number=0)
    # session.scalars(select(Autohaus)...).all()
    session_mock.scalars.return_value.all.return_value = []

    # Act
    with raises(NotFoundError) as err:
        autohaus_service.find(suchparameter=suchparameter, pageable=pageable)

    # Assert
    assert err.type == NotFoundError
    assert str(err.value) == "Not Found"  # super().__init__("Not Found")
    assert err.value.suchparameter is not None
    assert err.value.suchparameter.get("name") == name  # pyright: ignore[reportOptionalMemberAccess]
