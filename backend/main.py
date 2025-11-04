"""
FastAPI Application for Impact Analysis Tool
Main entry point
"""
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

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

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve HTML UI"""
    return get_html_ui()

def get_html_ui() -> str:
    """Get the HTML UI"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Code Impact Analysis Tool</title>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
            }
            
            header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px 20px;
                text-align: center;
            }
            
            header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            header p {
                font-size: 1.1em;
                opacity: 0.9;
            }
            
            .content {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                padding: 40px;
            }
            
            .section {
                display: flex;
                flex-direction: column;
            }
            
            .section h2 {
                color: #333;
                margin-bottom: 20px;
                font-size: 1.5em;
                border-bottom: 3px solid #667eea;
                padding-bottom: 10px;
            }
            
            .upload-area {
                border: 3px dashed #667eea;
                border-radius: 8px;
                padding: 40px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
                background: #f8f9ff;
            }
            
            .upload-area:hover {
                background: #f0f2ff;
                border-color: #764ba2;
            }
            
            .upload-area input[type="file"] {
                display: none;
            }
            
            .upload-icon {
                font-size: 3em;
                margin-bottom: 10px;
            }
            
            .upload-text {
                color: #666;
                margin-bottom: 10px;
            }
            
            textarea {
                width: 100%;
                min-height: 200px;
                padding: 15px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-family: 'Monaco', 'Courier New', monospace;
                font-size: 0.9em;
                resize: vertical;
                transition: border-color 0.3s ease;
            }
            
            textarea:focus {
                outline: none;
                border-color: #667eea;
            }
            
            .button-group {
                display: flex;
                gap: 10px;
                margin-top: 15px;
            }
            
            button {
                flex: 1;
                padding: 12px 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 1em;
                font-weight: 600;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            }
            
            button:active {
                transform: translateY(0);
            }
            
            .results {
                margin-top: 40px;
                padding: 30px;
                background: #f8f9ff;
                border-radius: 8px;
                display: none;
            }
            
            .results.active {
                display: block;
            }
            
            .results h3 {
                color: #333;
                margin-bottom: 20px;
                font-size: 1.3em;
            }
            
            .summary {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 30px;
            }
            
            .stat-box {
                background: white;
                padding: 20px;
                border-radius: 8px;
                border-left: 4px solid #667eea;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .stat-label {
                color: #999;
                font-size: 0.9em;
                margin-bottom: 5px;
            }
            
            .stat-value {
                color: #333;
                font-size: 1.8em;
                font-weight: bold;
            }
            
            .module-cards {
                display: grid;
                gap: 15px;
                margin-top: 20px;
            }
            
            .module-card {
                background: white;
                padding: 20px;
                border-radius: 8px;
                border-left: 4px solid #667eea;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .module-card.risk-high {
                border-left-color: #ff6b6b;
            }
            
            .module-card.risk-medium {
                border-left-color: #ffc93c;
            }
            
            .module-card.risk-low {
                border-left-color: #26de81;
            }
            
            .module-name {
                font-weight: 600;
                font-size: 1.1em;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .risk-badge {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.85em;
                font-weight: 600;
            }
            
            .risk-high .risk-badge {
                background: #ff6b6b;
                color: white;
            }
            
            .risk-medium .risk-badge {
                background: #ffc93c;
                color: white;
            }
            
            .risk-low .risk-badge {
                background: #26de81;
                color: white;
            }
            
            .module-reason {
                color: #666;
                font-size: 0.95em;
                margin-bottom: 8px;
                line-height: 1.4;
            }
            
            .module-issue {
                color: #999;
                font-size: 0.9em;
                font-style: italic;
                padding-top: 8px;
                border-top: 1px solid #eee;
            }
            
            svg {
                border: 1px solid #ddd;
                border-radius: 8px;
                background: white;
                margin-top: 20px;
            }
            
            .loading {
                display: none;
                text-align: center;
                padding: 20px;
            }
            
            .loading.active {
                display: block;
            }
            
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .error {
                background: #ffe0e0;
                color: #c92a2a;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
                display: none;
            }
            
            .error.active {
                display: block;
            }
            
            @media (max-width: 768px) {
                .content {
                    grid-template-columns: 1fr;
                }
                
                header h1 {
                    font-size: 1.8em;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🔍 Code Impact Analysis</h1>
                <p>Analyze impact of code changes across your modules</p>
            </header>
            
            <div class="content">
                <!-- Left column: Upload -->
                <div class="section">
                    <h2>Upload Diff</h2>
                    <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                        <div class="upload-icon">📁</div>
                        <div class="upload-text">Click to upload or drag & drop</div>
                        <div style="color: #999; font-size: 0.9em;">.diff or .patch files</div>
                    </div>
                    <input type="file" id="fileInput" accept=".diff,.patch" />
                    <button onclick="uploadFile()" style="margin-top: 15px;">Analyze File</button>
                </div>
                
                <!-- Right column: Results -->
                <div class="section">
                    <h2>Analysis Results</h2>
                    
                    <div class="loading" id="loading">
                        <div class="spinner"></div>
                        <p style="margin-top: 15px; color: #666;">Analyzing...</p>
                    </div>
                    
                    <div class="error" id="error"></div>
                    
                    <div class="results" id="results">
                        <div class="summary" id="summary"></div>
                        <div class="module-cards" id="moduleCards"></div>
                    </div>
                </div>
            </div>
            
            <!-- Graph visualization (full width) -->
            <div style="padding: 40px; border-top: 1px solid #eee;">
                <h2 style="margin-bottom: 20px;">Dependency Graph</h2>
                <svg id="graph" width="100%" height="400"></svg>
            </div>
        </div>
        
        <script>
            function uploadFile() {
                const fileInput = document.getElementById('fileInput');
                const file = fileInput.files;
                
                if (!file) {
                    showError('Please select a file');
                    return;
                }
                
                const formData = new FormData();
                formData.append('file', file);
                
                showLoading(true);
                clearError();
                
                fetch('/api/analyze-diff', {
                    method: 'POST',
                    body: formData
                })
                .then(r => r.json())
                .then(data => {
                    showLoading(false);
                    if (data.status === 'success') {
                        displayResults(data);
                    } else {
                        showError(data.message || 'Analysis failed');
                    }
                })
                .catch(err => {
                    showLoading(false);
                    showError('Error: ' + err);
                });
            }
            
            function displayResults(data) {
                // Summary
                const summary = document.getElementById('summary');
                summary.innerHTML = `
                    <div class="stat-box">
                        <div class="stat-label">Changed Files</div>
                        <div class="stat-value">${data.changed_files.length}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Changed Modules</div>
                        <div class="stat-value">${data.changed_modules.length}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Affected Modules</div>
                        <div class="stat-value">${data.total_affected}</div>
                    </div>
                `;
                
                // Module cards
                const moduleCards = document.getElementById('moduleCards');
                moduleCards.innerHTML = '';
                
                data.affected_modules.forEach(module => {
                    const analysis = data.llm_analysis[module] || {};
                    const risk = analysis.risk || 'MEDIUM';
                    const reason = analysis.reason || 'Dependency on changed code';
                    const issue = analysis.potential_issue || '';
                    
                    const card = document.createElement('div');
                    card.className = `module-card risk-${risk.toLowerCase()}`;
                    card.innerHTML = `
                        <div class="module-name">
                            ${module}
                            <span class="risk-badge">${risk}</span>
                        </div>
                        <div class="module-reason">${reason}</div>
                        ${issue ? '<div class="module-issue">⚠️ ' + issue + '</div>' : ''}
                    `;
                    moduleCards.appendChild(card);
                });
                
                // Graph
                drawGraph(data.graph_data);
                
                // Show results
                document.getElementById('results').classList.add('active');
            }
            
            function drawGraph(data) {
                const svg = d3.select('#graph');
                svg.selectAll('*').remove();
                
                const width = svg.node().clientWidth;
                const height = 400;
                
                const simulation = d3.forceSimulation(data.nodes)
                    .force('link', d3.forceLink(data.edges).id(d => d.id).distance(80))
                    .force('charge', d3.forceManyBody().strength(-300))
                    .force('center', d3.forceCenter(width / 2, height / 2));
                
                const link = svg.selectAll('line')
                    .data(data.edges)
                    .enter().append('line')
                    .attr('stroke', '#ddd')
                    .attr('stroke-width', 2);
                
                const node = svg.selectAll('circle')
                    .data(data.nodes)
                    .enter().append('circle')
                    .attr('r', d => d.type === 'changed' ? 15 : 10)
                    .attr('fill', d => d.type === 'changed' ? '#ff6b6b' : '#667eea')
                    .attr('opacity', 0.8)
                    .call(d3.drag()
                        .on('start', dragStarted)
                        .on('drag', dragged)
                        .on('end', dragEnded));
                
                const label = svg.selectAll('text')
                    .data(data.nodes)
                    .enter().append('text')
                    .text(d => d.id)
                    .attr('font-size', 11)
                    .attr('text-anchor', 'middle')
                    .attr('dy', 3)
                    .attr('fill', 'white')
                    .attr('font-weight', 'bold');
                
                simulation.on('tick', () => {
                    link.attr('x1', d => d.source.x)
                        .attr('y1', d => d.source.y)
                        .attr('x2', d => d.target.x)
                        .attr('y2', d => d.target.y);
                    
                    node.attr('cx', d => d.x).attr('cy', d => d.y);
                    label.attr('x', d => d.x).attr('y', d => d.y);
                });
                
                function dragStarted(event, d) {
                    if (!event.active) simulation.alphaTarget(0.3).restart();
                    d.fx = d.x;
                    d.fy = d.y;
                }
                
                function dragged(event, d) {
                    d.fx = event.x;
                    d.fy = event.y;
                }
                
                function dragEnded(event, d) {
                    if (!event.active) simulation.alphaTarget(0);
                    d.fx = null;
                    d.fy = null;
                }
            }
            
            function showLoading(show) {
                document.getElementById('loading').classList.toggle('active', show);
            }
            
            function showError(msg) {
                const error = document.getElementById('error');
                error.textContent = msg;
                error.classList.add('active');
            }
            
            function clearError() {
                document.getElementById('error').classList.remove('active');
            }
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=8000,
        log_level='info'
    )
