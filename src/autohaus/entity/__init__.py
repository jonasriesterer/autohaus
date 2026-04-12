"""Entity-Paket für das Autohaus-Projekt."""

from autohaus.entity.adresse import Adresse
from autohaus.entity.auto import Auto
from autohaus.entity.autohaus import Autohaus
from autohaus.entity.base import Base

__all__ = [
    "Adresse",
    "Auto",
    "Autohaus",
    "Base",
]
