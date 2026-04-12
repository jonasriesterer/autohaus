# # ruff: noqa: S101, D103, ARG005
# # Copyright (C) 2022 - present Juergen Zimmermann, Hochschule Karlsruhe
# #
# # This program is free software: you can redistribute it and/or modify
# # it under the terms of the GNU General Public License as published by
# # the Free Software Foundation, either version 3 of the License, or
# # (at your option) any later version.
# #
# # This program is distributed in the hope that it will be useful,
# # but WITHOUT ANY WARRANTY; without even the implied warranty of
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# # GNU General Public License for more details.
# #
# # You should have received a copy of the GNU General Public License
# # along with this program.  If not, see <https://www.gnu.org/licenses/>.

# """Unit-Tests für find_by_id() von AutohausService."""

# from copy import deepcopy
# from datetime import date
# from typing import TYPE_CHECKING

# from pytest import fixture, mark, raises

# from autohaus.entity import Adresse, Auto, Autohaus

# if TYPE_CHECKING:
#     from pytest_mock import MockerFixture


# @fixture
# def session_mock(mocker: MockerFixture):
#     session = mocker.Mock()
#     # Patching von "with Session() as session:" in autohaus_write_service.py
#     mocker.patch(
#         "autohaus.service.autohaus_write_service.Session",
#         return_value=mocker.MagicMock(
#             __enter__=lambda self: session,
#             __exit__=lambda self, exc_type, exc, tb: None,
#         ),
#     )
#     return session


# @mark.unit
# @mark.unit_create
# def test_create(
#     autohaus_write_service, session_mock, keycloak_admin_mock, mocker
# ) -> None:
#     # Arrange
#     email = "mock@email.test"
#     adresse = Adresse(
#         id=999,
#         plz="11111",
#         ort="Mockort",
#         land="Deutschland",
#         autohaus_id=None,
#         autohaus=None,
#     )
#     autohaus = Autohaus(
#         id=None,
#         name="Mocktest",
#         anzahl_fahrzeuge=10,
#         gruendungsdatum=date(2025, 1, 31),
#         email="T@test.de",
#         username="mocktest",
#         adresse=adresse,
#         autos=[],
#     )
#     adresse.autohaus = autohaus
#     autohaus_db_mock = deepcopy(autohaus)
#     generierte_id = 1
#     autohaus_db_mock.id = generierte_id
#     autohaus_db_mock.adresse.id = generierte_id

#     # Patch fuer KeycloakAdmin.get_user_id() und KeycloakAdmin.get_users()
#     keycloak_admin_mock.get_user_id.return_value = None
#     keycloak_admin_mock.get_users.return_value = []

#     # session.scalar(select(func.count()).where(Autohaus.email == email)
#     session_mock.scalar.return_value = 0
#     session_mock.add.return_value = None

#     def flush_side_effect(objects=None):
#         for obj in objects or []:
#             obj.id = generierte_id  # Emulation: generierter PK in session.flush()

#     session_mock.flush.side_effect = flush_side_effect

#     # Patch fuer die Funktion send_mail
#     mocker.patch("autohaus.service.autohaus_write_service.send_mail", return_value=None)

#     # Act
#     autohaus_dto = autohaus_write_service.create(autohaus=autohaus)

#     # Assert
#     assert autohaus_dto.id == generierte_id


# @mark.unit
# @mark.unit_create
# def test_create_username_none(autohaus_write_service) -> None:
#     # Arrange
#     adresse = Adresse(
#         id=999,
#         plz="11111",
#         ort="Mockort",
#         land="Deutschland",
#         autohaus_id=None,
#         autohaus=None,
#     )
#     autohaus = Autohaus(
#         id=None,
#         name="Mocktest",
#         anzahl_fahrzeuge=10,
#         gruendungsdatum=date(2025, 1, 31),
#         email="T@test.de",
#         username=None,
#         adresse=adresse,
#         autos=[],
#     )
#     adresse.autohaus = autohaus

#     # Act
#     with raises(ValueError) as err:
#         autohaus_write_service.create(autohaus=autohaus)

#     # Assert
#     assert err.type is ValueError



