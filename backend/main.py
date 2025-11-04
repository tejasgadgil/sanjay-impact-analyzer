"""
FastAPI Application for Impact Analysis Tool
Main entry point
"""
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path

from backend.config import config
from backend.core.dependency_graph import DependencyGraph
from backend.core.impact_analyzer import ImpactAnalyzer
from backend.llm.gemini_analyzer import GeminiAnalyzer
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Code Impact Analysis Tool",
    description="Analyze impact of code changes across dependencies",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analysis engines
graph = DependencyGraph()
impact_analyzer = ImpactAnalyzer(graph)
llm_analyzer = GeminiAnalyzer()

# Load sample projects on startup
@app.on_event("startup")
async def startup_event():
    """Load dependency graphs for all sample projects"""
    logger.info("Loading sample projects...")
    
    sample_projects_path = config.SAMPLE_PROJECTS_PATH
    
    try:
        graph.build_graph(sample_projects_path, '')  # Empty string for repository_name disables prefix
        logger.info("✓ Loaded all sample projects")
    except Exception as e:
        logger.error(f"Failed to load sample projects: {e}")
        
        logger.info("Startup complete")

# API

@app.get("/api/graph")
async def get_graph():
    """
    Get the full dependency graph visualization data.
    Returns nodes and edges in D3.js compatible format.
    """
    try:
        graph_dict = graph.to_dict()
        
        # Transform to D3.js format
        nodes = [
            {"id": node, "type": "module"}
            for node in graph_dict["nodes"]
        ]
        
        edges = [
            {
                "source": edge["source"],
                "target": edge["target"],
                "type": "depends_on"
            }
            for edge in graph_dict["edges"]
        ]
        
        return {
            "status": "success",
            "nodes": nodes,
            "edges": edges,
            "total_modules": len(nodes),
            "total_dependencies": len(edges)
        }
    except Exception as e:
        logger.error(f"Error fetching graph: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/api/analyze-diff")
async def analyze_diff(file: UploadFile = File(...)):
    content = await file.read()
    diff_text = content.decode('utf-8')

    # Perform static analysis
    result = impact_analyzer.analyze_diff(diff_text)
    if result["status"] != "success":
        return result

    # Always call Gemini without fallback
    try:
        llm_analysis = llm_analyzer.analyze_impact(
            result["changed_modules"],
            result["affected_modules"]
        )
    except Exception as e:
        # Instead of fallback, you can raise or return error here
        return {
            "status": "error",
            "message": f"Gemini LLM call failed: {str(e)}"
        }

    result["llm_analysis"] = llm_analysis
    return result


@app.post("/api/analyze-diff-text")
async def analyze_diff_text(request: dict):
    """
    Analyze diff provided as text.
    
    Request body: {"diff_text": "..."}
    """
    logger.info("Received diff text for analysis")
    
    try:
        diff_text = request.get("diff_text", "")
        
        if not diff_text:
            return {
                "status": "error",
                "message": "No diff text provided"
            }
        
        # Analyze the diff
        result = impact_analyzer.analyze_diff(diff_text)
        
        if result["status"] != "success":
            return result
        
        # Get LLM analysis
        llm_analysis = llm_analyzer.analyze_impact(
            result["changed_modules"],
            result["affected_modules"]
        )
        
        result["llm_analysis"] = llm_analysis
        
        return result
    
    except Exception as e:
        logger.error(f"Error analyzing diff text: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "gemini_available": llm_analyzer.available,
        "sample_projects_loaded": len(graph.module_to_files) > 0
    }

@app.get("/api/graph-stats")
async def graph_stats():
    """Get statistics about loaded graphs"""
    return {
        "total_modules": len(graph.module_to_files),
        "total_dependencies": sum(len(v) for v in graph.graph.values()),
        "modules": list(graph.module_to_files.keys())
    }

# @app.get("/", response_class=HTMLResponse)
# async def index():
#     """Serve HTML UI"""
#     return get_html_ui()

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve HTML UI"""
    html_path = Path(__file__).parent / "static" / "index.html"
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Error: HTML template not found"


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=8000,
        log_level='info'
    )
