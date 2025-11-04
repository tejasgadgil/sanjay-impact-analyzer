"""
Dependency Graph Builder
Parses Python code and builds a directed graph of dependencies
"""
import ast
import os
from typing import Dict, List, Set
from collections import defaultdict
from backend.utils.logger import get_logger

logger = get_logger(__name__)

class DependencyGraph:
    """
    Builds and manages a dependency graph for a Python codebase.
    
    Graph structure:
    - Nodes: module names (e.g., "module_a", "utils.helper")
    - Edges: dependencies (A -> B means A depends on/imports B)
    """
    
    def __init__(self):
        # Adjacency list: {module: {dependent_modules}}
        self.graph = defaultdict(set)
        self.files_to_modules = {}  # {file_path: module_name}
        self.module_to_files = {}   # {module_name: file_path}
    
    def parse_python_file(self, filepath: str) -> List[str]:
        """
        Extract imports from a Python file using AST.
        
        Args:
            filepath: Path to Python file
            
        Returns:
            List of imported module names
        """
        imports = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
        except Exception as e:
            logger.warning(f"Failed to parse {filepath}: {e}")
            return imports
        
        # Extract all imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                # Handle: import module, import module as alias
                for alias in node.names:
                    imports.append(alias.name)
            
            elif isinstance(node, ast.ImportFrom):
                # Handle: from module import name
                if node.module:
                    imports.append(node.module)
        
        return imports
    
    def build_graph(self, directory: str, repository_name: str = "") -> Dict:
        """
        Scan directory and build dependency graph.

        Args:
            directory: Root directory to scan
            repository_name: Name of the repository (for prefixing module names); if empty, no prefix

        Returns:
            Dictionary with graph info
        """

        logger.info(f"Building dependency graph for {directory}")

        # Step 1: Find all Python files
        python_files = {}

        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                # Include .py files including __init__.py but exclude __pycache__ and other dunder folders
                if filename.endswith('.py') and (filename == '__init__.py' or not filename.startswith('__')):
                    filepath = os.path.join(root, filename)

                    # Convert file path to module name
                    rel_path = os.path.relpath(filepath, directory)
                    module_name = rel_path.replace('/', '.').replace('\\', '.').replace('.py', '')

                    # Prefix module names with repo name if provided
                    if repository_name:
                        module_name = repository_name + '.' + module_name

                    python_files[module_name] = filepath
                    self.files_to_modules[filepath] = module_name
                    self.module_to_files[module_name] = filepath

        logger.info(f"Found {len(python_files)} Python files: {list(python_files.keys())}")

        # Step 2: Build dependency graph
        for module_name, filepath in python_files.items():
            imports = self.parse_python_file(filepath)
            logger.info(f"Module '{module_name}' imports: {imports}")

            for imp in imports:
                matched = False
                for other_module in python_files.keys():
                    if imp == other_module or imp.startswith(other_module + '.'):
                        self.graph[other_module].add(module_name)
                        logger.info(f"Added edge: '{module_name}' depends on '{other_module}'")
                        matched = True
                if not matched:
                    logger.info(f"No matching module found for import '{imp}' in module '{module_name}'")

        logger.info(f"Graph built with {len(self.graph)} nodes")
        return {
            "nodes": len(python_files),
            "edges": sum(len(v) for v in self.graph.values()),
            "modules": list(python_files.keys())
        }

    def find_affected_modules(self, changed_module: str, max_depth: int = 5) -> List[str]:
        """
        Find all modules affected by changes to changed_module using BFS.
        
        Args:
            changed_module: Name of the changed module
            max_depth: Maximum depth to traverse
            
        Returns:
            List of affected module names
        """
        affected = set()
        queue = [(changed_module, 0)]
        visited = {changed_module}
        
        logger.debug(f"Finding affected modules for: {changed_module}")
        
        while queue:
            current, depth = queue.pop(0)
            
            if depth >= max_depth:
                continue
            
            # Find all modules that depend on current
            for dependent in self.graph.get(current, []):
                if dependent not in visited:
                    affected.add(dependent)
                    visited.add(dependent)
                    queue.append((dependent, depth + 1))
                    logger.debug(f"  → Found affected: {dependent} (depth: {depth + 1})")
        
        logger.info(f"Total affected modules: {len(affected)}")
        return sorted(list(affected))
    
    def get_module_file(self, module_name: str) -> str:
        """Get the file path for a module"""
        return self.module_to_files.get(module_name, "Unknown")
    
    def to_dict(self) -> Dict:
        """Export graph as dictionary"""
        return {
            "nodes": list(self.module_to_files.keys()),
            "edges": [
                {"source": target, "target": dependent}
                for target, dependents in self.graph.items()
                for dependent in dependents
            ]
        }
    
    def print_summary(self):
        print(f"Total modules (nodes): {len(self.module_to_files)}")
        print("Modules:")
        for mod in sorted(self.module_to_files.keys()):
            print(f" - {mod}")
        print("Dependencies (edges):")
        for src, targets in self.graph.items():
            for tgt in targets:
                print(f" - {src} -> {tgt}")

