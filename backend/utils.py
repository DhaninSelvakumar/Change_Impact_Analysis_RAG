import os
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def ensure_directory(path: str):
    """Ensure directory exists, create if not"""
    Path(path).mkdir(parents=True, exist_ok=True)

def load_config(config_path: str = "config.json") -> dict:
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Config file {config_path} not found, using defaults")
        return {}

def save_analysis_results(results: dict, output_path: str):
    """Save analysis results to file"""
    try:
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {output_path}")
    except Exception as e:
        logger.error(f"Error saving results: {str(e)}")

def validate_folder_structure(folder_path: str) -> bool:
    """Validate if folder exists and contains files"""
    if not os.path.exists(folder_path):
        return False
    
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    return len(files) > 0