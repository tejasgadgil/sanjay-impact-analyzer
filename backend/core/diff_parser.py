"""
Git Diff Parser
Extracts changed files from unified diff format
"""
from typing import List, Set
from backend.utils.logger import get_logger

logger = get_logger(__name__)

class DiffParser:
    """Parses unified diff format"""
    
    @staticmethod
    def parse(diff_text: str) -> List[str]:
        """
        Extract changed file paths from unified diff.
        
        Unified diff format:
        diff --git a/path/file.py b/path/file.py
        --- a/path/file.py
        +++ b/path/file.py
        
        Args:
            diff_text: Raw diff text
            
        Returns:
            List of changed file paths
        """
        files = set()
        
        lines = diff_text.split('\n')
        
        for line in lines:
            if line.startswith('+++'):
                # Format: +++ b/path/to/file.py
                filepath = line.replace('+++', '').replace('b/', '').strip()
                if filepath and filepath != '/dev/null':
                    files.add(filepath)
            elif line.startswith('---'):
                # Format: --- a/path/to/file.py
                filepath = line.replace('---', '').replace('a/', '').strip()
                if filepath and filepath != '/dev/null':
                    files.add(filepath)
        
        logger.info(f"Parsed diff: found {len(files)} changed files")
        return sorted(list(files))
    
    @staticmethod
    def convert_filepath_to_module(filepath: str) -> str:
        """
        Convert file path to module name.
        
        Examples:
        - path/to/module_a.py -> module_a
        - src/utils/helper.py -> helper
        """
        # Remove extension
        module = filepath.replace('.py', '')
        
        # Get the last part (filename without extension)
        # For: path/to/module_a.py -> module_a
        if '/' in module:
            module = module.split('/')[-1]
        elif '\\' in module:
            module = module.split('\\')[-1]
        
        return module
