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
from autohaus.graphql_api.graphql_types import Suchparameter
from autohaus.repository import AutohausRepository, Pageable
from autohaus.security import Role, TokenService
from autohaus.service import (
    AutohausDTO,
    AutohausService,
    NotFoundError,
)

__all__ = ["Query", "graphql_router"]


_repo: Final = AutohausRepository()
_service: AutohausService = AutohausService(repo=_repo)
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


schema: Final = strawberry.Schema(query=Query)

Context = dict[str, Request]


# Dependency Injection: Request von FastAPI weiterreichen an den Kontext von Strawberry
def get_context(request: Request) -> Context:
    return {"request": request}


# https://strawberry.rocks/docs/integrations/fastapi
graphql_router: Final = GraphQLRouter[Context](
    schema, context_getter=get_context, graphql_ide=graphql_ide
)
