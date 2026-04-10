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
"""Modul für den Zugriffsschutz."""

from autohaus.security.auth_router import router, token
from autohaus.security.exceptions import AuthorizationError, LoginError
from autohaus.security.response_headers import set_response_headers
from autohaus.security.role import Role
from autohaus.security.roles_required import RolesRequired
from autohaus.security.token_service import TokenService
from autohaus.security.user import User
from autohaus.security.user_service import UserService

__all__ = [
    "AuthorizationError",
    "LoginError",
    "Role",
    "RolesRequired",
    "TokenService",
    "User",
    "UserService",
    "router",
    "set_response_headers",
    "token",
]
