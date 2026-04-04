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

"""AutohausGetRouter."""

from dataclasses import asdict
from typing import Annotated, Any, Final

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import JSONResponse
from loguru import logger

from autohaus.repository import Pageable
from autohaus.repository.slice import Slice
from autohaus.router.constants import ETAG, IF_NONE_MATCH, IF_NONE_MATCH_MIN_LEN
from autohaus.router.dependencies import get_service
from autohaus.router.page import Page
from autohaus.security.role import Role
from autohaus.security.roles_required import RolesRequired
from autohaus.security.user import User
from autohaus.service.autohaus_dto import AutohausDTO
from autohaus.service.autohaus_service import AutohausService

__all__ = ["autohaus_router"]


# APIRouter auf Basis der Klasse Router von Starlette
autohaus_router: Final = APIRouter(tags=["Lesen"])


@autohaus_router.get(
    "/{autohaus_id}",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.PATIENT]))],
)
def get_by_id(
    autohaus_id: int,
    request: Request,
    service: Annotated[AutohausService, Depends(get_service)],
) -> Response:
    """Suche mit der autohaus-ID.

    :param autohaus_id: ID des gesuchten Autohäuser als Pfadparameter
    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit ggf. If-None-Match im Header
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit dem gefundenen Autohausdatensatz
    :rtype: Response
    :raises NotFoundError: Falls kein Autohaus gefunden wurde
    :raises ForbiddenError: Falls die Autohausdaten nicht gelesen werden dürfen
    """
    # User-Objekt ist durch Depends(RolesRequired()) in Request.state gepuffert
    user: Final[User] = request.state.current_user
    logger.debug("autohaus_id={}, user={}", autohaus_id, user)

    autohaus: Final = service.find_by_id(autohaus_id=autohaus_id)
    logger.debug("{}", autohaus)

    if_none_match: Final = request.headers.get(IF_NONE_MATCH)
    if (
        if_none_match is not None
        and len(if_none_match) >= IF_NONE_MATCH_MIN_LEN
        and if_none_match.startswith('"')
        and if_none_match.endswith('"')
    ):
        version = if_none_match[1:-1]
        logger.debug("version={}", version)
        if version is not None:
            try:
                if int(version) == autohaus.version:
                    return Response(status_code=status.HTTP_304_NOT_MODIFIED)
            except ValueError:
                logger.debug("invalid version={}", version)

    return JSONResponse(
        content=_autohaus_to_dict(autohaus),
        headers={ETAG: f'"{autohaus.version}"'},
    )


@autohaus_router.get(
    "",
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
)
def get(
    request: Request,
    service: Annotated[AutohausService, Depends(get_service)],
) -> JSONResponse:
    """Suche mit Query-Parameter.

    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit Query-Parameter
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit einer Seite mit Autohaus-Daten
    :rtype: Response
    :raises NotFoundError: Falls keine Autohäuser gefunden wurden
    """
    query_params: Final = request.query_params
    log_str: Final = "{}"
    logger.debug(log_str, query_params)

    page: Final = query_params.get("page")
    size: Final = query_params.get("size")
    pageable: Final = Pageable.create(number=page, size=size)

    suchparameter = dict(query_params)
    if "page" in query_params:
        del suchparameter["page"]
    if "size" in query_params:
        del suchparameter["size"]

    autohaus_slice: Final = service.find(suchparameter=suchparameter, pageable=pageable)

    result: Final = _autohaus_slice_to_page(autohaus_slice, pageable)
    logger.debug(log_str, result)
    return JSONResponse(content=result)


def _autohaus_slice_to_page(
    autohaus_slice: Slice[AutohausDTO],
    pageable: Pageable,
) -> dict[str, Any]:
    autohaus_dict: Final = tuple(
        _autohaus_to_dict(autohaus) for autohaus in autohaus_slice.content
    )
    page: Final = Page.create(
        content=autohaus_dict,
        pageable=pageable,
        total_elements=autohaus_slice.total_elements,
    )
    return asdict(obj=page)


def _autohaus_to_dict(autohaus: AutohausDTO) -> dict[str, Any]:
    # https://docs.python.org/3/library/dataclasses.html
    autohaus_dict: Final = asdict(obj=autohaus)
    autohaus_dict.pop("version")
    autohaus_dict.update({"gruendungsdatum": autohaus.gruendungsdatum.isoformat()})
    return autohaus_dict
