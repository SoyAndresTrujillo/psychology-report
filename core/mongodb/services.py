"""MongoDB service layer for business logic and data operations."""
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from .client import mongodb_client
from .serializers import AccountSerializer, AppointmentSerializer

logger = logging.getLogger(__name__)


class MongoDBService:
    """Service layer for MongoDB operations.
    
    Provides high-level methods for saving, retrieving, and querying
    data in MongoDB. Handles errors gracefully and logs all operations.
    """
    
    @staticmethod
    def save_account(account_instance) -> bool:
        """Save account data to MongoDB.
        
        Performs upsert operation to create or update account document
        in MongoDB. Maintains sync with Django ORM by using django_id
        as unique identifier.
        
        Args:
            account_instance: Django Account model instance
            
        Returns:
            bool: True if save successful, False otherwise
            
        Side Effects:
            - Creates or updates document in MongoDB accounts collection
            - Logs success/failure messages
        """
        if not mongodb_client.is_connected():
            logger.warning("MongoDB not connected. Skipping account save.")
            return False
        
        try:
            collection = mongodb_client.db.accounts
            account_data = AccountSerializer.serialize(account_instance)
            
            # Upsert operation: update if exists, insert if not
            result = collection.update_one(
                {'django_id': account_instance.id},
                {
                    '$set': account_data,
                    '$setOnInsert': {'created_at': datetime.utcnow()}
                },
                upsert=True
            )
            
            action = 'updated' if result.matched_count > 0 else 'created'
            logger.info(
                f"Account {action} in MongoDB: "
                f"django_id={account_instance.id}, "
                f"email={account_instance.email}"
            )
            return True
            
        except Exception as e:
            logger.error(
                f"Failed to save account to MongoDB: "
                f"django_id={account_instance.id}, error={str(e)}"
            )
            return False
    
    @staticmethod
    def get_account(django_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve account from MongoDB by Django ID.
        
        Args:
            django_id: Primary key from Django Account model
            
        Returns:
            dict: MongoDB document if found, None otherwise
        """
        if not mongodb_client.is_connected():
            return None
        
        try:
            collection = mongodb_client.db.accounts
            document = collection.find_one({'django_id': django_id})
            
            if document:
                logger.debug(f"Retrieved account from MongoDB: django_id={django_id}")
            else:
                logger.debug(f"Account not found in MongoDB: django_id={django_id}")
            
            return document
            
        except Exception as e:
            logger.error(
                f"Failed to retrieve account from MongoDB: "
                f"django_id={django_id}, error={str(e)}"
            )
            return None
    
    @staticmethod
    def search_accounts(query: str) -> List[Dict[str, Any]]:
        """Search accounts by name or email.
        
        Args:
            query: Search query string
            
        Returns:
            list: List of matching account documents
        """
        if not mongodb_client.is_connected():
            return []
        
        try:
            collection = mongodb_client.db.accounts
            
            # Create text search query
            search_filter = {
                '$or': [
                    {'name': {'$regex': query, '$options': 'i'}},
                    {'last_name': {'$regex': query, '$options': 'i'}},
                    {'email': {'$regex': query, '$options': 'i'}},
                    {'full_name': {'$regex': query, '$options': 'i'}},
                ]
            }
            
            results = list(collection.find(search_filter).limit(50))
            logger.info(f"Account search returned {len(results)} results for query: {query}")
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search accounts in MongoDB: error={str(e)}")
            return []
    
    @staticmethod
    def save_appointment(appointment_instance) -> bool:
        """Save appointment data to MongoDB.
        
        Args:
            appointment_instance: Django Appointment model instance
            
        Returns:
            bool: True if save successful, False otherwise
        """
        if not mongodb_client.is_connected():
            logger.warning("MongoDB not connected. Skipping appointment save.")
            return False
        
        try:
            collection = mongodb_client.db.appointments
            appointment_data = AppointmentSerializer.serialize(appointment_instance)
            
            result = collection.update_one(
                {'django_id': appointment_instance.id},
                {
                    '$set': appointment_data,
                    '$setOnInsert': {'created_at': datetime.utcnow()}
                },
                upsert=True
            )
            
            action = 'updated' if result.matched_count > 0 else 'created'
            logger.info(
                f"Appointment {action} in MongoDB: django_id={appointment_instance.id}"
            )
            return True
            
        except Exception as e:
            logger.error(
                f"Failed to save appointment to MongoDB: "
                f"django_id={appointment_instance.id}, error={str(e)}"
            )
            return False
    
    @staticmethod
    def get_appointment(django_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve appointment from MongoDB by Django ID.
        
        Args:
            django_id: Primary key from Django Appointment model
            
        Returns:
            dict: MongoDB document if found, None otherwise
        """
        if not mongodb_client.is_connected():
            return None
        
        try:
            collection = mongodb_client.db.appointments
            return collection.find_one({'django_id': django_id})
            
        except Exception as e:
            logger.error(
                f"Failed to retrieve appointment from MongoDB: "
                f"django_id={django_id}, error={str(e)}"
            )
            return None
    
    @staticmethod
    def verify_data_consistency(django_id: int, model_type: str = 'account') -> bool:
        """Verify data consistency between Django ORM and MongoDB.
        
        Args:
            django_id: Primary key from Django model
            model_type: Type of model ('account' or 'appointment')
            
        Returns:
            bool: True if data is consistent, False otherwise
        """
        if not mongodb_client.is_connected():
            return False
        
        try:
            if model_type == 'account':
                from accounts.models import Account
                django_obj = Account.objects.get(id=django_id)
                mongo_doc = MongoDBService.get_account(django_id)
                
                if not mongo_doc:
                    return False
                
                # Check key fields match
                return (
                    mongo_doc['email'] == django_obj.email and
                    mongo_doc['name'] == django_obj.name and
                    mongo_doc['last_name'] == django_obj.last_name
                )
            
            return False
            
        except Exception as e:
            logger.error(f"Data consistency check failed: {str(e)}")
            return False


# Create singleton instance
mongo_service = MongoDBService()
