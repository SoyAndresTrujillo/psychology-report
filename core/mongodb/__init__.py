"""MongoDB integration package for dual-database architecture."""
from .client import mongodb_client
from .services import mongo_service

__all__ = ['mongodb_client', 'mongo_service']
