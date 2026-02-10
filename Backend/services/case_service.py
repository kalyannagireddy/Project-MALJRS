"""
Case management service.
Handles CRUD operations for cases.
"""
import uuid
from datetime import datetime
from typing import Optional, List

from models.case_models import CaseData, StoredCase
from storage.json_storage import JSONStorage


class CaseService:
    """Service for managing legal cases"""
    
    def __init__(self, storage: Optional[JSONStorage] = None):
        """
        Initialize case service.
        
        Args:
            storage: Storage backend (default: JSONStorage)
        """
        self.storage = storage or JSONStorage()
    
    def create_case(self, case_data: CaseData) -> str:
        """
        Create a new case.
        
        Args:
            case_data: Case data from frontend
            
        Returns:
            Unique case ID
        """
        case_id = f"case_{uuid.uuid4().hex[:12]}"
        now = datetime.now()
        
        stored_case = StoredCase(
            id=case_id,
            data=case_data,
            createdAt=now,
            updatedAt=now,
            status="draft"
        )
        
        self.storage.save(case_id, stored_case)
        return case_id
    
    def get_case(self, case_id: str) -> Optional[StoredCase]:
        """
        Retrieve a case by ID.
        
        Args:
            case_id: Unique case identifier
            
        Returns:
            StoredCase if found, None otherwise
        """
        return self.storage.load(case_id)
    
    def update_case(self, case_id: str, case_data: CaseData) -> bool:
        """
        Update an existing case.
        
        Args:
            case_id: Unique case identifier
            case_data: Updated case data
            
        Returns:
            True if successful, False if case not found
        """
        stored_case = self.storage.load(case_id)
        if not stored_case:
            return False
        
        # Update data and timestamp
        stored_case.data = case_data
        stored_case.updatedAt = datetime.now()
        
        return self.storage.save(case_id, stored_case)
    
    def update_status(
        self, 
        case_id: str, 
        status: str
    ) -> bool:
        """
        Update case status.
        
        Args:
            case_id: Unique case identifier
            status: New status
            
        Returns:
            True if successful, False if case not found
        """
        stored_case = self.storage.load(case_id)
        if not stored_case:
            return False
        
        stored_case.status = status
        stored_case.updatedAt = datetime.now()
        
        return self.storage.save(case_id, stored_case)
    
    def delete_case(self, case_id: str) -> bool:
        """
        Delete a case.
        
        Args:
            case_id: Unique case identifier
            
        Returns:
            True if successful, False if case not found
        """
        return self.storage.delete(case_id)
    
    def list_cases(self) -> List[str]:
        """
        List all case IDs.
        
        Returns:
            List of case IDs
        """
        return self.storage.list_all()
    
    def case_exists(self, case_id: str) -> bool:
        """
        Check if case exists.
        
        Args:
            case_id: Unique case identifier
            
        Returns:
            True if exists, False otherwise
        """
        return self.storage.exists(case_id)
