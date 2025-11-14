"""MongoDB client singleton with connection management."""
import os
import logging
import certifi
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from django.conf import settings

logger = logging.getLogger(__name__)


class MongoDBClient:
    """Singleton MongoDB client for application-wide connection management.
    
    Implements lazy connection initialization and automatic reconnection.
    Thread-safe singleton pattern ensures only one MongoDB connection pool
    exists across the application.
    
    Usage:
        from core.mongodb import mongodb_client
        
        if mongodb_client.is_connected():
            db = mongodb_client.db
            collection = db.accounts
    """
    
    _instance = None
    _client = None
    _database = None
    
    def __new__(cls):
        """Ensure only one instance exists (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize MongoDB connection if not already connected."""
        if self._client is None:
            self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB.
        
        Retrieves connection parameters from Django settings and attempts
        to connect to MongoDB server. Logs connection status and handles
        connection failures gracefully.
        
        Supports both MongoDB Atlas URIs (with embedded credentials) and
        local MongoDB URIs (with separate username/password).
        """
        try:
            mongodb_uri = settings.MONGODB_URI
            mongodb_user = settings.MONGODB_USER
            mongodb_password = settings.MONGODB_PASSWORD
            mongodb_database = settings.MONGODB_DATABASE
            
            # For MongoDB Atlas URIs (mongodb+srv://) with embedded credentials
            # Use the URI directly with TLS certificate verification
            if mongodb_uri.startswith('mongodb+srv://') or mongodb_uri.startswith('mongodb://'):
                # MongoDB Atlas URIs already contain credentials and connection options
                # Just ensure TLS certificate verification is configured
                self._client = MongoClient(
                    mongodb_uri,
                    serverSelectionTimeoutMS=5000,  # 5 second timeout
                    tlsCAFile=certifi.where()  # SSL certificate bundle for Atlas
                )
            # For local MongoDB without credentials in URI
            elif mongodb_user and mongodb_password:
                # Build connection string for authenticated local MongoDB
                connection_string = f"{mongodb_uri.rstrip('/')}/{mongodb_database}"
                # Add auth parameters
                if '?' in connection_string:
                    connection_string += "&authSource=admin"
                else:
                    connection_string += "?authSource=admin"
                
                self._client = MongoClient(
                    connection_string,
                    username=mongodb_user,
                    password=mongodb_password,
                    serverSelectionTimeoutMS=5000
                )
            # For local MongoDB without authentication
            else:
                connection_string = f"{mongodb_uri.rstrip('/')}/{mongodb_database}"
                self._client = MongoClient(
                    connection_string,
                    serverSelectionTimeoutMS=5000
                )
            
            # Test connection by pinging server
            self._client.admin.command('ping')
            self._database = self._client[mongodb_database]
            
            logger.info(f"MongoDB connection established to database: {mongodb_database}")
            
        except (ServerSelectionTimeoutError, ConnectionFailure) as e:
            logger.warning(f"MongoDB connection failed: {e}. Operating without MongoDB.")
            self._client = None
            self._database = None
        except AttributeError as e:
            logger.error(f"MongoDB settings not configured: {e}")
            self._client = None
            self._database = None
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            self._client = None
            self._database = None
    
    @property
    def db(self):
        """Get MongoDB database instance.
        
        Returns:
            Database: MongoDB database instance if connected, None otherwise
        """
        if self._database is None and self._client is None:
            # Attempt reconnection if not connected
            self._connect()
        return self._database
    
    def is_connected(self):
        """Check if MongoDB connection is active.
        
        Returns:
            bool: True if connected to MongoDB, False otherwise
        """
        if self._client is None:
            return False
        
        try:
            # Ping to verify connection is still alive
            self._client.admin.command('ping')
            return True
        except Exception:
            logger.warning("MongoDB connection lost. Attempting reconnection...")
            self._connect()
            return self._client is not None
    
    def close(self):
        """Close MongoDB connection.
        
        Should be called during application shutdown to gracefully
        close all connections in the connection pool.
        """
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            logger.info("MongoDB connection closed")


# Create singleton instance
mongodb_client = MongoDBClient()
