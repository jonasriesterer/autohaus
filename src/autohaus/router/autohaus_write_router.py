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

"""PatientWriteRouter."""

from typing import Annotated, Final

from fastapi import APIRouter, Depends, Request, Response, status
from loguru import logger

from autohaus.problem_details import create_problem_details
from autohaus.router.autohaus_model import AutohausModel
from autohaus.router.autohaus_update_model import AutohausUpdateModel
from autohaus.router.constants import IF_MATCH, IF_MATCH_MIN_LEN
from autohaus.router.dependencies import get_write_service
from autohaus.security import Role, RolesRequired
from autohaus.service.autohaus_write_service import AutohausWriteService

__all__ = ["autohaus_write_router"]


autohaus_write_router: Final = APIRouter(tags=["Schreiben"])


@autohaus_write_router.post("")
def post(
    autohaus_model: AutohausModel,
    request: Request,
    service: Annotated[AutohausWriteService, Depends(get_write_service)],
) -> Response:
    """POST-Request, um einen neuen Autohaus anzulegen.

    :param autohaus_model: Autohausdaten als Pydantic-Model
    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit der Request-URL
    :param service: Injizierter Service für Geschäftslogik
    :rtype: Response
    :raises ValidationError: Falls es bei Pydantic Validierungsfehler gibt
    :raises EmailExistsError: Falls die Emailadresse bereits existiert
    :raises UsernameExistsError: Falls der Benutzername bereits existiert
    """
    logger.debug("autohaus_model={}", autohaus_model)
    autohaus_dto: Final = service.create(autohaus=autohaus_model.to_autohaus())
    logger.debug("autohaus_dto={}", autohaus_dto)

    return Response(
        status_code=status.HTTP_201_CREATED,
        headers={"Location": f"{request.url}/{autohaus_dto.id}"},
    )


@autohaus_write_router.put(
    "/{autohaus_id}",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.PATIENT]))],
)
def put(
    autohaus_id: int,
    autohaus_update_model: AutohausUpdateModel,
    request: Request,
    service: Annotated[AutohausWriteService, Depends(get_write_service)],
) -> Response:
    """PUT-Request, um ein Autohaus zu aktualisieren.

    :param autohaus_id: ID des zu aktualisierenden Autohauses als Pfadparameter
    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit If-Match im Header
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit Statuscode 204
    :rtype: Response
    :raises ValidationError: Falls es bei Marshmallow Validierungsfehler gibt
    :raises EmailExistsError: Falls die neue Emailadresse bereits
    :raises NotFoundError: Falls zur id kein Patient existiert
    :raises VersionOutdatedError: Falls die Versionsnummer nicht aktuell ist
    """
    if_match_value: Final = request.headers.get(IF_MATCH)
    logger.debug(
        "autohaus_id={}, if_match={}, autohaus_update_model={}",
        autohaus_id,
        if_match_value,
        autohaus_update_model,
    )

    if if_match_value is None:
        return create_problem_details(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
        )

    if (
        len(if_match_value) < IF_MATCH_MIN_LEN
        or not if_match_value.startswith('"')
        or not if_match_value.endswith('"')
    ):
        return create_problem_details(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
        )

    version: Final = if_match_value[1:-1]
    try:
        version_int: Final = int(version)
    except ValueError:
        return Response(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
        )

    autohaus: Final = autohaus_update_model.to_autohaus()
    autohaus_modified: Final = service.update(
        autohaus=autohaus,
        autohaus_id=autohaus_id,
        version=version_int,
    )
    logger.debug("autohaus_modified={}", autohaus_modified)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        headers={"ETag": f'"{autohaus_modified.version}"'},
    )


@autohaus_write_router.delete(
    "/{autohaus_id}",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.PATIENT]))],
)
def delete_by_id(
    autohaus_id: int,
    service: Annotated[AutohausWriteService, Depends(get_write_service)],
) -> Response:
    """DELETE-Request, um ein Autohaus anhand seiner ID zu löschen.

    :param autohaus_id: ID des zu löschenden Autohauses
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit Statuscode 204
    :rtype: Response
    """
    logger.debug("autohaus_id={}", autohaus_id)
    service.delete_by_id(autohaus_id=autohaus_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
