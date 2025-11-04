"""
Impact Analysis Engine
Analyzes impact of code changes using dependency graph
"""
from typing import Dict, List
from backend.core.dependency_graph import DependencyGraph
from backend.core.diff_parser import DiffParser
from backend.utils.logger import get_logger

logger = get_logger(__name__)

class ImpactAnalyzer:
    """
    Analyzes the impact of code changes.
    """
    
    def __init__(self, graph: DependencyGraph):
        self.graph = graph
        self.diff_parser = DiffParser()
    
    def analyze_diff(self, diff_text: str) -> Dict:
        """
        Analyze a git diff to find all affected modules.
        
        Args:
            diff_text: Raw git diff text
            
        Returns:
            Dictionary with analysis results
        """
        logger.info("Starting diff analysis")
        
        # Step 1: Parse diff to get changed files
        changed_files = self.diff_parser.parse(diff_text)
        
        if not changed_files:
            logger.warning("No changed files found in diff")
            return {
                "status": "error",
                "message": "No changed files detected in diff"
            }
        
        # Step 2: Convert files to module names
        changed_modules = [
            self.diff_parser.convert_filepath_to_module(f)
            for f in changed_files
        ]
        
        # Step 3: Find affected modules for each changed module
        all_affected = set()
        impact_details = {}
        
        for module in changed_modules:
            affected = self.graph.find_affected_modules(module)
            impact_details[module] = {
                "affected_count": len(affected),
                "affected_modules": affected
            }
            all_affected.update(affected)
        
        logger.info(f"Total affected modules: {len(all_affected)}")
        
        return {
            "status": "success",
            "changed_files": changed_files,
            "changed_modules": changed_modules,
            "affected_modules": sorted(list(all_affected)),
            "total_affected": len(all_affected),
            "details": impact_details,
            "graph_data": self._build_graph_data(changed_modules, all_affected)
        }
    
    def _build_graph_data(self, changed_modules: List[str], affected_modules: List[str]) -> Dict:
        """
        Build graph visualization data.
        
        Returns:
            Dictionary with nodes and edges for D3.js visualization
        """
        nodes = [
            {"id": m, "type": "changed"} for m in changed_modules
        ] + [
            {"id": m, "type": "affected"} for m in affected_modules
        ]
        
        edges = [
            {"source": cm, "target": am}
            for cm in changed_modules
            for am in affected_modules
        ]
        
        return {
            "nodes": nodes,
            "edges": edges
        }
