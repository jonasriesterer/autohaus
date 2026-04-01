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

"""Geschäftslogik zum Lesen von Autohausdaten."""

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Final

from loguru import logger
from openpyxl import Workbook  # pyright: ignore[reportMissingModuleSource]

from autohaus.config import excel_enabled
from autohaus.repository import (
    Pageable,
    AutohausRepository,
    Session,
    Slice,
)
from autohaus.security import Role, User
from autohaus.service.exceptions import ForbiddenError, NotFoundError
from autohaus.service.autohaus_dto import AutohausDTO

__all__ = ["AutohausService"]


class AutohausService:
    """Service-Klasse mit Geschäftslogik für Autohaus."""

    def __init__(self, repo: AutohausRepository) -> None:
        """Konstruktor mit abhängigem AutohausRepository."""
        self.repo: AutohausRepository = repo

    def find_by_id(self, autohaus_id: int, user: User) -> AutohausDTO:
        """Suche mit der Autohaus-ID.

        :param autohaus_id: ID für die Suche
        :param user: User aus dem Token
        :return: Das gefundene autohaus
        :rtype: AutohausDTO
        :raises NotFoundError: Falls kein autohaus gefunden
        :raises ForbiddenError: Falls die Autohausdaten nicht gelesen werden dürfen
        """
        logger.debug("autohaus_id={}, user={}", autohaus_id, user)

        # Session-Objekt ist die Schnittstelle zur DB, nutzt intern ein Transaktionsobj.
        # implizites "autobegin()" bei einem with-Block
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#opening-and-closing-a-session
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#using-a-sessionmaker
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#auto-begin
        # durch "with" erhaelt man einen "Context Manager", der die Ressource/Session
        # am Endes des Blocks schliesst
        with Session() as session:
            user_is_admin: Final = Role.ADMIN in user.roles

            if (
                autohaus := self.repo.find_by_id(autohaus_id=autohaus_id, session=session)
            ) is None:
                if user_is_admin:
                    message: Final = f"Kein Autohaus mit der ID {autohaus_id}"
                    logger.debug("NotFoundError: {}", message)
                    # "Throw Exceptions Instead of Returning Errors"
                    raise NotFoundError(autohaus_id=autohaus_id)
                logger.debug("nicht admin")
                raise ForbiddenError

            if autohaus.username != user.username and not user_is_admin:
                logger.debug(
                    "autohaus.username={}, user.username={}, user.roles={}",
                    autohaus.username,
                    user.username,
                    user.roles,
                )
                raise ForbiddenError

            autohaus_dto: Final = AutohausDTO(autohaus)
            session.commit()

        logger.debug("{}", autohaus_dto)
        return autohaus_dto

    # ab Python 3.9 (2019) ist der Element-Type in eckigen Klammern und
    # der Name von eingebauten Collections ist kleingeschrieben.
    def find(
        self,
        suchparameter: Mapping[str, str],
        pageable: Pageable,
    ) -> Slice[AutohausDTO]:
        """Suche mit Suchparameter.

        :param suchparameter: Suchparameter
        :return: Liste der gefundenen Autohäuser
        :rtype: Slice[AutohausDTO]
        :raises NotFoundError: Falls keine Autohäuser gefunden wurden
        """
        logger.debug("{}", suchparameter)
        with Session() as session:
            autohaus_slice: Final = self.repo.find(
                suchparameter=suchparameter, pageable=pageable, session=session
            )
            if len(autohaus_slice.content) == 0:
                raise NotFoundError(suchparameter=suchparameter)

            # tuple mit einem "Generator"-Ausdruck
            # vgl. List Comprehension ab Python 2.0 (2000) https://peps.python.org/pep-0202
            autohaeuser_dto: Final = tuple(
                AutohausDTO(autohaus) for autohaus in autohaus_slice.content
            )
            session.commit()

        if excel_enabled:
            self._create_excelsheet(autohaeuser_dto)
        autohaeuser_dto_slice = Slice(
            content=autohaeuser_dto, total_elements=autohaus_slice.total_elements
        )
        logger.debug("{}", autohaeuser_dto_slice)
        return autohaeuser_dto_slice

    def find_namen(self, teil: str) -> Sequence[str]:
        """Suche namen zu einem Teilstring.

        :param teil: Teilstring der gesuchten Namen
        :return: Liste der gefundenen Namen oder eine leere Liste
        :rtype: list[str]
        :raises NotFoundError: Falls keine Namen gefunden wurden
        """
        logger.debug("teil={}", teil)
        with Session() as session:
            namen: Final = self.repo.find_namen(teil=teil, session=session)
            session.commit()

        logger.debug("{}", namen)
        if len(namen) == 0:
            raise NotFoundError
        return namen

    def _create_excelsheet(self, autohaeuser: tuple[AutohausDTO, ...]) -> None:
        """Ein Excelsheet mit den gefundenen Autohäuser erstellen.

        :param autohaeuser: Autohausdaten für das Excelsheet
        """
        # https://automatetheboringstuff.com/2e/chapter13
        workbook: Final = Workbook()
        worksheet: Final = workbook.active
        if worksheet is None:
            return

        worksheet.append(["Name", "anzahl_fahrzeug", "gruendungsdatum"])
        for autohaus in autohaeuser:
            
            worksheet.append((
                autohaus.nachname,
                autohaus.anzahl_fahrzeug,
                autohaus.gruendungsdatum
            ))

        timestamp: Final = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        workbook.save(f"autohaeuser-{timestamp}.xlsx")
 