```markdown
# Code Impact Analysis Tool - Iteration 1

A lightweight tool to analyze the impact of code changes across modular systems.

## Features (Iteration 1)

- ✅ Parse Python dependency graphs
- ✅ Analyze git diffs
- ✅ Identify affected modules
- ✅ LLM-powered impact reasoning (Gemini 2.5 Flash)
- ✅ Beautiful web UI with graph visualization

## Tech Stack

- **Backend**: FastAPI + Python
- **Frontend**: HTML + D3.js
- **LLM**: Google Gemini 2.5 Flash
- **Visualization**: D3.js directed graph

## Quick Start

### 1. Clone and Setup
```

git clone <your-repo>
cd impact-analyzer

# Create virtual environment

python3 -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

# Install dependencies

pip install -r requirements.txt

# Copy environment file

cp .env.example .env

```

### 2. Configure Gemini API (Optional)

To enable LLM analysis:
- Get API key from [Google AI Studio](https://aistudio.google.com/)
- Add to `.env`:

```

GEMINI_API_KEY=your_key_here

```

### 3. Run the Server

```

python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

```

Or use the provided script:

```

chmod +x scripts/run.sh
./scripts/run.sh

```

### 4. Open the UI

Visit: [http://localhost:8000](http://localhost:8000/)

---

## How to Use

### Method 1: Upload Diff File

```

# Generate a diff

git diff main..feature-branch > changes.diff

# Upload via UI

# 1. Open http://localhost:8000

# 2. Click "Upload Diff"

# 3. Select changes.diff

# 4. Click "Analyze File"

```

### Method 2: Command Line

```

from backend.core.dependency_graph import DependencyGraph
from backend.core.impact_analyzer import ImpactAnalyzer

graph = DependencyGraph()
graph.build_graph('./sample_projects/repo_a')

analyzer = ImpactAnalyzer(graph)
result = analyzer.analyze_diff(open('test.diff').read())

print(result)

```

---

## Project Structure

```

impact-analyzer/
├── backend/
│ ├── core/ # Analysis engines
│ ├── llm/ # LLM integrations
│ ├── utils/ # Utilities
│ └── main.py # FastAPI app
├── sample_projects/ # Test repositories
├── test_diffs/ # Sample diffs
└── scripts/ # Helper scripts

```

---

## API Endpoints

### POST `/api/analyze-diff`
Upload a `.diff` file for analysis
**Request:** Multipart form with `file` field
**Response:**
```

{
"status": "success",
"changed_files": ["module_a.py"],
"affected_modules": ["module_b", "module_c"],
"total_affected": 2,
"llm_analysis": {
"module_b": {
"reason": "Imports from module_a",
"potential_issue": "Type mismatch",
"risk": "HIGH"
}
},
"graph_data": {...}
}

```

### GET `/api/health`
Health check endpoint

### GET `/api/graph-stats`
Get statistics about loaded dependency graphs

---

## Iteration 2 Roadmap

- ✅ Multi-repository support
- ✅ Suggested code changes
- ✅ Automated PR generation
- ✅ GitHub integration
- ✅ Risk scoring refinement

---

## Troubleshooting

**Port 8000 already in use**
```

python -m uvicorn backend.main:app --port 8001

```

**Gemini API not working**
- Check `.env` has valid API key
- Tool still works without Gemini (uses fallback analysis)

**Python version issues**
- Requires Python 3.8+
- Use `python3` instead of `python` on Mac/Linux

---

## Contributing

This is a hackathon project. For Iteration 2+, consider:
- Multi-language support (Java, TypeScript)
- Database for caching analyses
- GitHub webhook integration
- Automated PR creation

## License

MIT
```
