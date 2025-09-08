from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from llama_model import LlamaAnalyzer
from diff_detector import compare_documents
from rag_engine import RagEngine
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Change Impact Analysis API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
rag_engine = None
llama_analyzer = None

@app.on_event("startup")
async def startup_event():
    global rag_engine, llama_analyzer
    logger.info("Initializing RAG engine and LLaMA analyzer...")
    rag_engine = RagEngine()
    llama_analyzer = LlamaAnalyzer()
    logger.info("Initialization complete!")

@app.get("/")
async def root():
    return {"message": "Change Impact Analysis API is running"}

@app.post("/analyze/")
async def analyze_changes(old_folder: str, new_folder: str):
    try:
        # Validate folders exist
        if not os.path.exists(old_folder) or not os.path.exists(new_folder):
            raise HTTPException(status_code=400, detail="One or both folders don't exist")
        
        logger.info(f"Analyzing changes between {old_folder} and {new_folder}")
        
        # Step 1: Compare documents
        differences = compare_documents(old_folder, new_folder)
        
        if not differences:
            return {"differences": [], "impact": "No changes detected between document versions."}
        
        # Step 2: Build RAG index from old version for context
        rag_engine.build_index(old_folder)
        
        # Step 3: Find related contexts for each change
        related_contexts = []
        for diff in differences:
            contexts = rag_engine.search_related(diff["description"], top_k=2)
            related_contexts.extend(contexts)
        
        # Step 4: Use LLaMA for impact analysis
        impact_analysis = llama_analyzer.analyze_impact(differences, related_contexts)
        
        return {
            "differences": differences,
            "impact_analysis": impact_analysis,
            "related_contexts_count": len(related_contexts)
        }
        
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/build-index/")
async def build_knowledge_base(folder_path: str):
    """Build RAG index from a knowledge base folder"""
    try:
        if not os.path.exists(folder_path):
            raise HTTPException(status_code=400, detail="Folder doesn't exist")
        
        rag_engine.build_index(folder_path)
        return {"message": f"Knowledge base built from {folder_path}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build index: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)