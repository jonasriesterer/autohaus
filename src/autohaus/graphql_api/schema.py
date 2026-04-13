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

"""Schema für GraphQL durch Strawberry.

Alternative: https://github.com/graphql-python/graphene.
"""
from collections.abc import Sequence
from typing import Final

import strawberry
from fastapi import Request
from loguru import logger
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info

from autohaus.config.graphql import graphql_ide
from autohaus.graphql_api.graphql_types import (
    AutohausInput,
    CreatePayload,
    LoginResult,
    Suchparameter,
)
from autohaus.repository import AutohausRepository, Pageable
from autohaus.router.autohaus_model import AutohausModel
from autohaus.security import Role, TokenService, UserService
from autohaus.service import (
    AutohausDTO,
    AutohausService,
    AutohausWriteService,
    NotFoundError,
)

__all__ = ["Query", "graphql_router"]


_repo: Final = AutohausRepository()
_service: AutohausService = AutohausService(repo=_repo)
_user_service: UserService = UserService()
_write_service: AutohausWriteService = AutohausWriteService(
    repo=_repo, user_service=_user_service
)
_token_service: Final = TokenService()


@strawberry.type  # vgl. @dataclass
class Query:
    """Queries, um Autohausdaten zu lesen."""

    @strawberry.field
    def autohaus(self, autohaus_id: strawberry.ID, info: Info) -> AutohausDTO | None:
        """Daten zu einem Autohaus lesen.

        :param autohaus_id: ID des gesuchten Autohauses
        :return: Gesuchtes Autohaus
        :rtype: Autohaus
        :raises NotFoundError: Falls kein Autohaus gefunden wurde, wird zu GraphQLError
        """
        logger.debug("autohaus_id={}", autohaus_id)

        request: Final[Request] = info.context.get("request")
        user: Final = _token_service.get_user_from_request(request=request)
        if user is None:
            return None

        try:
            autohaus_dto: Final = _service.find_by_id(
                autohaus_id=int(autohaus_id),
            )
        except NotFoundError:
            return None
        logger.debug("{}", autohaus_dto)
        return autohaus_dto

    @strawberry.field
    def autohaeuser(
        self, suchparameter: Suchparameter, info: Info
    ) -> Sequence[AutohausDTO]:
        """Autohaeuser anhand von Suchparameter suchen.

        :param suchparameter: nachname, email usw.
        :return: Die gefundenen Autohaeuser
        :rtype: list[Autohaus]
        :raises NotFoundError: Falls kein Autohaus gefunden wurde, wird zu GraphQLError
        """
        logger.debug("suchparameter={}", suchparameter)

        request: Final[Request] = info.context["request"]
        user: Final = _token_service.get_user_from_request(request)
        if user is None or Role.ADMIN not in user.roles:
            return []

        # suchparameter: input type -> Dictionary
        # https://stackoverflow.com/questions/61517/python-dictionary-from-an-objects-fields
        suchparameter_dict: Final[dict[str, str]] = dict(vars(suchparameter))
        # nicht-gesetzte Suchparameter aus dem Dictionary entfernen
        # Dict Comprehension ab Python 2.7 (2001) https://peps.python.org/pep-0274
        suchparameter_filtered = {
            key: value
            for key, value in suchparameter_dict.items()
            # leerer String "" ist falsy
            if value is not None and value
        }
        logger.debug("suchparameter_filtered={}", suchparameter_filtered)

        pageable: Final = Pageable.create(size=str(0))
        try:
            autohaeuser_dto: Final = _service.find(
                suchparameter=suchparameter_filtered, pageable=pageable
            )
        except NotFoundError:
            return []
        logger.debug("{}", autohaeuser_dto)
        return autohaeuser_dto.content


@strawberry.type
class Mutation:
    """Mutations, um Autohausdaten anzulegen, zu ändern oder zu löschen."""

    @strawberry.mutation
    def create(self, autohaus_input: AutohausInput) -> CreatePayload:
        """Einen neuen Autohaus anlegen.

        :param autohaus_input: Daten des neuen Autohauses
        :return: ID des neuen Autohauses
        :rtype: CreatePayload
        :raises EmailExistsError: Falls die Emailadresse bereits existiert
        :raises UsernameExistsError: Falls der Benutzername bereits existiert
        """
        logger.debug("autohaus_input={}", autohaus_input)

        autohaus_dict = autohaus_input.__dict__
        autohaus_dict["adresse"] = autohaus_input.adresse.__dict__
        # List Comprehension ab Python 2.0 (2000) https://peps.python.org/pep-0202
        autohaus_dict["autos"] = [
            auto.__dict__ for auto in autohaus_input.autos
        ]

        # Dictonary mit Pydantic validieren
        autohaus_model: Final = AutohausModel.model_validate(autohaus_dict)

        autohaus_dto: Final = _write_service.create(autohaus=autohaus_model.to_autohaus())  # noqa: E501
        payload: Final = CreatePayload(id=autohaus_dto.id)  # pyright: ignore[reportArgumentType ]

        logger.debug("{}", payload)
        return payload

    # Mutation, weil evtl. der Login-Zeitpunkt gespeichert wird
    @strawberry.mutation
    def login(self, username: str, password: str) -> LoginResult:
        """Einen Token zu Benutzername und Passwort ermitteln.

        :param username: Benutzername
        :param password: Passwort
        :rtype: LoginResult
        """
        logger.debug("username={}, password={}", username, password)
        token_mapping = _token_service.token(username=username, password=password)

        token = token_mapping["access_token"]
        user = _token_service.get_user_from_token(token)
        # List Comprehension ab Python 2.0 (2000) https://peps.python.org/pep-0202
        roles: Final = [role.value for role in user.roles]
        return LoginResult(token=token, expiresIn="1d", roles=roles)


schema: Final = strawberry.Schema(query=Query)

Context = dict[str, Request]


# Dependency Injection: Request von FastAPI weiterreichen an den Kontext von Strawberry
def get_context(request: Request) -> Context:
    return {"request": request}


# https://strawberry.rocks/docs/integrations/fastapi
graphql_router: Final = GraphQLRouter[Context](
    schema, context_getter=get_context, graphql_ide=graphql_ide
)
