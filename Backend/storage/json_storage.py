"""
Simple JSON file-based storage for cases.
Can be replaced with database later.
"""
import json
import os
from datetime import datetime
from typing import Optional, List
from pathlib import Path

from models.case_models import StoredCase, CaseData


class JSONStorage:
    """File-based JSON storage for case data"""
    
    def __init__(self, data_dir: str = None):
        """
        Initialize storage with data directory.
        
        Args:
            data_dir: Directory to store case files (default: Backend/data/cases)
        """
        if data_dir is None:
            # Default to Backend/data/cases
            backend_dir = Path(__file__).parent.parent
            data_dir = backend_dir / "data" / "cases"
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, case_id: str, case: StoredCase) -> bool:
        """
        Save case to JSON file.
        
        Args:
            case_id: Unique case identifier
            case: Case data to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self.data_dir / f"{case_id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(case.model_dump(), f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            print(f"Error saving case {case_id}: {e}")
            return False
    
    def load(self, case_id: str) -> Optional[StoredCase]:
        """
        Load case from JSON file.
        
        Args:
            case_id: Unique case identifier
            
        Returns:
            StoredCase object if found, None otherwise
        """
        try:
            file_path = self.data_dir / f"{case_id}.json"
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return StoredCase(**data)
        except Exception as e:
            print(f"Error loading case {case_id}: {e}")
            return None
    
    def delete(self, case_id: str) -> bool:
        """
        Delete case file.
        
        Args:
            case_id: Unique case identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self.data_dir / f"{case_id}.json"
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting case {case_id}: {e}")
            return False
    
    def list_all(self) -> List[str]:
        """
        List all case IDs.
        
        Returns:
            List of case IDs
        """
        try:
            return [f.stem for f in self.data_dir.glob("*.json")]
        except Exception as e:
            print(f"Error listing cases: {e}")
            return []
    
    def exists(self, case_id: str) -> bool:
        """
        Check if case exists.
        
        Args:
            case_id: Unique case identifier
            
        Returns:
            True if case exists, False otherwise
        """
        file_path = self.data_dir / f"{case_id}.json"
        return file_path.exists()
