import os
import difflib
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

def read_file(file_path: str) -> str:
    """Read file content with error handling"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with different encoding
        with open(file_path, 'r', encoding='latin-1') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        return ""

def get_detailed_diff(old_text: str, new_text: str) -> Dict:
    """Get detailed differences between two texts"""
    differ = difflib.unified_diff(
        old_text.splitlines(keepends=True),
        new_text.splitlines(keepends=True),
        lineterm=""
    )
    
    diff_lines = list(differ)
    
    # Count changes
    additions = len([line for line in diff_lines if line.startswith('+')])
    deletions = len([line for line in diff_lines if line.startswith('-')])
    
    return {
        "additions": additions,
        "deletions": deletions,
        "diff_preview": "".join(diff_lines[:20])  # First 20 lines of diff
    }

def compare_documents(old_folder: str, new_folder: str) -> List[Dict]:
    """Compare documents between old and new versions"""
    differences = []
    
    old_files = set(os.listdir(old_folder))
    new_files = set(os.listdir(new_folder))
    
    # --- NEW: match files by content similarity ---
    for old_file in old_files:
        for new_file in new_files:
            old_path = os.path.join(old_folder, old_file)
            new_path = os.path.join(new_folder, new_file)

            if os.path.isfile(old_path) and os.path.isfile(new_path):
                old_content = read_file(old_path)
                new_content = read_file(new_path)

                similarity = difflib.SequenceMatcher(None, old_content, new_content).ratio()
                if similarity > 0.6:  # threshold: treat as modified
                    diff_details = get_detailed_diff(old_content, new_content)
                    differences.append({
                        "file": f"{old_file} → {new_file}",
                        "type": "modified",
                        "description": f"{old_file} updated to {new_file}",
                        "details": diff_details
                    })
    
    # Check for deleted files
    deleted_files = old_files - new_files
    for file_name in deleted_files:
        differences.append({
            "file": file_name,
            "type": "deleted",
            "description": f"File {file_name} was deleted",
            "details": {"impact": "high"}
        })
    
    # Check for new files
    new_files_only = new_files - old_files
    for file_name in new_files_only:
        differences.append({
            "file": file_name,
            "type": "added",
            "description": f"New file {file_name} was added",
            "details": {"impact": "medium"}
        })
    
    logger.info(f"Found {len(differences)} differences")
    return differences
