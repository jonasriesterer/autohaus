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

"""Repository fuer persistente Autohausdaten."""

# "list" ist eine mutable "Sequence"
# https://docs.python.org/3/library/stdtypes.html#lists
# https://docs.python.org/3/library/stdtypes.html#typesseq
from collections.abc import Mapping
from typing import Final

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from autohaus.entity.autohaus import Autohaus
from autohaus.repository.pageable import Pageable
from autohaus.repository.slice import Slice

__all__ = ["AutohausRepository"]


class AutohausRepository:
    """Repository-Klasse mit CRUD-Methoden für die Entity-Klasse Autohaus."""

    def find_by_id(self, autohaus_id: int | None, session: Session) -> Autohaus | None:
        """Suche mit der Autohaus-ID.

        :param autohaus_id: ID des gesuchten Autohaus
        :param session: Session für SQLAlchemy
        :return: Der gefundene Autohaus oder None
        :rtype: Autohaus | None
        """
        logger.debug("autohaus_id={}", autohaus_id)  # NOSONAR

        if autohaus_id is None:
            return None

        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#querying
        # https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#relationship-loading-with-loader-options
        # https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#sqlalchemy.orm.joinedload
        statement: Final = (
            select(Autohaus)
            .options(joinedload(Autohaus.adresse))
            .where(Autohaus.id == autohaus_id)
        )
        autohaus: Final = session.scalar(statement)

        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#get-by-primary-key
        # autohaus: Final[Autohaus | None] = session.get(Autohaus, autohaus_id)

        logger.debug("{}", autohaus)
        return autohaus

    def find(
        self,
        suchparameter: Mapping[str, str],
        pageable: Pageable,
        session: Session,
    ) -> Slice[Autohaus]:
        """Suche mit Suchparameter.

        :param suchparameter: Suchparameter als Dictionary
        :param pageable: Anzahl Datensätze und Seitennummer
        :param session: Session für SQLAlchemy
        :return: Tupel, d.h. readonly Liste, der gefundenen Autohäuser oder leeres Tupel
        :rtype: Slice[Autohaus]
        """
        log_str: Final = "{}"
        logger.debug(log_str, suchparameter)
        if not suchparameter:
            return self._find_all(pageable=pageable, session=session)

        # Iteration ueber die Schluessel des Dictionaries mit den Suchparameter
        for key, value in suchparameter.items():
            if key == "email":
                autohaus = self._find_by_email(email=value, session=session)
                logger.debug(log_str, autohaus)
                return (
                    Slice(content=(autohaus,), total_elements=1)
                    if autohaus is not None
                    else Slice(content=(), total_elements=0)
                )
            if key in ("name"):
                autohaeuser = self._find_by_name(
                    teil=value, pageable=pageable, session=session
                )
                logger.debug(log_str, autohaeuser)
                return autohaeuser
        return Slice(content=(), total_elements=0)

    def _find_all(self, pageable: Pageable, session: Session) -> Slice[Autohaus]:
        logger.debug("aufgerufen")
        offset = pageable.number * pageable.size
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#querying
        statement: Final = (
            (
                select(Autohaus)
                .options(joinedload(Autohaus.adresse))
                .limit(pageable.size)
                .offset(offset)
            )
            if pageable.size != 0
            else (select(Autohaus).options(joinedload(Autohaus.adresse)))
        )
        autohaeuser: Final = (session.scalars(statement)).all()
        anzahl: Final = self._count_all_rows(session)
        autohaus_slice: Final = Slice(content=tuple(autohaeuser), total_elements=anzahl)
        logger.debug("autohaus_slice={}", autohaus_slice)
        return autohaus_slice

    def _count_all_rows(self, session: Session) -> int:
        statement: Final = select(func.count()).select_from(Autohaus)
        count: Final = session.execute(statement).scalar()
        return count if count is not None else 0

    def _find_by_name(
        self,
        teil: str,
        pageable: Pageable,
        session: Session,
    ) -> Slice[Autohaus]:
        logger.debug("teil={}", teil)
        offset = pageable.number * pageable.size
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#querying
        statement: Final = (
            (
                select(Autohaus)
                .options(joinedload(Autohaus.adresse))
                .filter(Autohaus.name.ilike(f"%{teil}%"))
                .limit(pageable.size)
                .offset(offset)
            )
            if pageable.size != 0
            else (
                select(Autohaus)
                .options(joinedload(Autohaus.adresse))
                .filter(Autohaus.name.ilike(f"%{teil}%"))
            )
        )
        autohaeuser: Final = session.scalars(statement).all()
        anzahl: Final = self._count_rows_name(teil, session)
        autohaus_slice: Final = Slice(content=tuple(autohaeuser), total_elements=anzahl)
        logger.debug("{}", autohaus_slice)
        return autohaus_slice

    def _find_by_email(self, email: str, session: Session) -> Autohaus | None:
        """Einen Autohaus anhand der Emailadresse suchen.

        :param email: Emailadresse
        :param session: Session für SQLAlchemy
        :return: Gefundener Autohaus, falls es einen Autohaus gibt, sonst None
        :rtype: Autohaus | None
        """
        logger.debug("email={}", email)  # NOSONAR
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#querying
        statement: Final = (
            select(Autohaus)
            .options(joinedload(Autohaus.adresse))
            .where(Autohaus.email == email)
        )
        autohaus: Final = session.scalar(statement)
        logger.debug("{}", autohaus)
        return autohaus

    def _count_rows_name(self, teil: str, session: Session) -> int:
        statement: Final = (
            select(func.count())
            .select_from(Autohaus)
            .filter(Autohaus.name.ilike(f"%{teil}%"))
        )
        count: Final = session.execute(statement).scalar()
        return count if count is not None else 0

    def create(self, autohaus: Autohaus, session: Session) -> Autohaus:
        """Speichere einen neuen Autohaus ab.

        :param autohaus: Die Daten des neuen Autohauses ohne ID
        :param session: Session für SQLAlchemy
        :return: Der neu angelegte Autohaus mit generierter ID
        :rtype: Autohaus
        """
        logger.debug(
            "autohaus={}, autohaus.adresse={}, autohaus.autos={}",
            autohaus,
            autohaus.adresse,
            autohaus.autos,
        )
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#adding-new-or-existing-items
        session.add(instance=autohaus)
        # flush(), damit die ID aus der Sequence vor COMMIT fuer Logging verfuegbar ist
        # https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html#flushing
        session.flush(objects=[autohaus])
        logger.debug("autohaus_id={}", autohaus.id)
        return autohaus

    def update(self, autohaus: Autohaus, session: Session) -> Autohaus | None:
        """Aktualisiere einen Autohaus.

        :param autohaus: Die neuen Autohausbereitungen
        :param session: Session für SQLAlchemy
        :return: Der aktualisierte Autohaus oder None, falls kein Autohaus mit der ID
        existiert
        :rtype: Autohaus | None
        """
        logger.debug("{}", autohaus)

        if (
            autohaus_db := self.find_by_id(autohaus_id=autohaus.id, session=session)
        ) is None:
            # Autohausbereitungen wurden i.a. zuvor in der Session aktualisiert
            return None

        # session.add(autohaus_db) nicht notwendig, da bereits in der Session zugegriffen  # noqa: E501
        # CAVEAT: Die erhoehte Versionsnummer ist erst *nach* COMMIT sichtbar

        logger.debug("{}", autohaus_db)
        return autohaus_db

    def delete_by_id(self, autohaus_id: int, session: Session) -> None:
        """Lösche die Daten zu einem Autohaus.

        :param autohaus_id: Die ID des zu löschenden Autohauses
        :param session: Session für SQLAlchemy
        """
        logger.debug("autohaus_id={}", autohaus_id)

        # delete(Autohaus).where(Autohaus.autohaus_id == autohaus_id) OHNE cascade
        # "walrus operator" https://peps.python.org/pep-0572
        if (autohaus := self.find_by_id(autohaus_id=autohaus_id, session=session)) is None:  # noqa: E501
            return
        session.delete(autohaus)
        logger.debug("ok")

    def exists_username(self, username: str | None, session: Session) -> bool:
        """Abfrage, ob es den Benutzernamen bereits gibt.

        :param username: Benutzername
        :param session: Session für SQLAlchemy
        :return: True, falls es den Benutzernamen bereits gibt
        :rtype: bool
        """
        logger.debug("username={}", username)
        if username is None:
            return False

        statement: Final = select(Autohaus.username).filter_by(username=username)
        username_db: Final = session.scalar(statement)
        logger.debug("username_db={}", username_db)
        return username_db is not None
