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

"""Geschäftslogik zum Schreiben von Patientendaten."""

from typing import Final

from loguru import logger

from autohaus.entity import Autohaus
from autohaus.repository import AutohausRepository, Session
from autohaus.security import User, UserService
from autohaus.service.autohaus_dto import AutohausDTO
from autohaus.service.exceptions import (
    EmailExistsError,
    NotFoundError,
    UsernameExistsError,
    VersionOutdatedError,
)
from autohaus.service.mailer import send_mail

__all__ = ["AutohausWriteService"]


class AutohausWriteService:
    """Service-Klasse mit Geschäftslogik für Autohaus."""

    def __init__(self, repo: AutohausRepository, user_service: UserService) -> None:
        """Konstruktor mit abhängigem AutohausRepository und UserService."""
        self.repo: AutohausRepository = repo
        self.user_service: UserService = user_service

    def create(self, autohaus: Autohaus) -> AutohausDTO:
        """Einen neuen Autohaus anlegen.

        :param autohaus: Der neue Autohaus ohne ID
        :return: Der neu angelegte Autohaus mit generierter ID
        :rtype: AutohausDTO
        """
        logger.debug(
            "autohaus={}, adresse={}, autos={}",
            autohaus,
            autohaus.adresse,
            autohaus.autos,
        )

        username: Final = autohaus.username
        if username is None:
            raise ValueError

        # https://www.keycloak.org/docs-api/latest/rest-api:
        # GET /admin/realms/{realm}/users
        if self.user_service.username_exists(username):
            raise UsernameExistsError(username)

        email: Final = autohaus.email
        if self.user_service.email_exists(email):
            raise EmailExistsError(email=email)

        user: Final = User(
            username=username,
            email=autohaus.email,
            vorname=autohaus.name,
            nachname=autohaus.name,
            password="p",  # noqa: S106 # NOSONAR
            roles=[],
        )
        user_id = self.user_service.create_user(user)
        logger.debug("user_id={}", user_id)

        # durch "with" erhaelt man einen "Context Manager", der die Ressource/Session
        # am Endes des Blocks schliesst
        with Session() as session:
            autohaus_db: Final = self.repo.create(autohaus=autohaus, session=session)
            autohaus_dto: Final = AutohausDTO(autohaus_db)
            session.commit()

        send_mail(autohaus_dto=autohaus_dto)
        logger.debug("autohaus_dto={}", autohaus_dto)
        return autohaus_dto

    def update(self, autohaus: Autohaus, autohaus_id: int, version: int) -> AutohausDTO:
        """Daten eines Autohauses ändern.

        :param autohaus: Die neuen Daten
        :param autohaus_id: ID des zu aktualisierenden Autohauses
        :param version: Version für optimistische Synchronisation
        :return: Der aktualisierte Autohaus
        :rtype: AutohausDTO
        :raises NotFoundError: Falls der zu aktualisierende Autohaus nicht existiert
        :raises VersionOutdatedError: Falls die Versionsnummer nicht aktuell ist
        """
        logger.debug("autohaus_id={}, version={}, {}", autohaus_id, version, autohaus)

        with Session() as session:
            if (
                autohaus_db := self.repo.find_by_id(
                    autohaus_id=autohaus_id, session=session
                )
            ) is None:
                raise NotFoundError(autohaus_id)
            if autohaus_db.version > version:
                raise VersionOutdatedError(version)
            autohaus_db.set(autohaus)
            if (
                autohaus_updated := self.repo.update(autohaus=autohaus_db, session=session)  # noqa: E501
            ) is None:
                raise NotFoundError(autohaus_id)
            autohaus_dto: Final = AutohausDTO(autohaus_updated)
            logger.debug("{}", autohaus_dto)

            session.commit()
            # CAVEAT: Die erhoehte Versionsnummer ist erst COMMIT sichtbar
            autohaus_dto.version += 1
            return autohaus_dto

    def delete_by_id(self, autohaus_id: int) -> None:
        """Einen Autohaus anhand seiner ID löschen.

        :param autohaus_id: ID des zu löschenden Autohauses
        """
        logger.debug("autohaus_id={}", autohaus_id)
        with Session() as session:
            self.repo.delete_by_id(autohaus_id=autohaus_id, session=session)
            session.commit()
