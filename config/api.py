"""
Django Bolt API – re-export for autodiscovery.

All routes and middleware live in the api/ package. This module exists so
runbolt can find the BoltAPI instance via config.api:api.
"""

from api import api

__all__ = ["api"]
