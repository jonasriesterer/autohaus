"""Modul für den DB-Zugriff."""

from autohaus.repository.autohaus_repository import AutohausRepository
from autohaus.repository.pageable import MAX_PAGE_SIZE, Pageable
from autohaus.repository.session_factory import Session, engine
from autohaus.repository.slice import Slice

# https://docs.python.org/3/tutorial/modules.html#importing-from-a-package
__all__ = [
    "MAX_PAGE_SIZE",
    "AutohausRepository",
    "Pageable",
    "Session",
    "Slice",
    "engine",
]
