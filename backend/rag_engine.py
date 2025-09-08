from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class RagEngine:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.embedder = SentenceTransformer(model_name)
        self.documents = []
        self.file_names = []
        self.index = None
        logger.info(f"RAG Engine initialized with model: {model_name}")
    
    def build_index(self, folder_path: str):
        """Build FAISS index from documents in folder"""
        try:
            documents = []
            file_names = []
            
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if content.strip():  # Only add non-empty files
                                documents.append(content)
                                file_names.append(file_name)
                    except Exception as e:
                        logger.warning(f"Could not read file {file_name}: {str(e)}")
            
            if not documents:
                logger.warning("No documents found to index")
                return
            
            logger.info(f"Embedding {len(documents)} documents...")
            embeddings = self.embedder.encode(documents, show_progress_bar=True)
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(np.array(embeddings).astype('float32'))
            
            self.documents = documents
            self.file_names = file_names
            
            logger.info(f"FAISS index built with {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error building index: {str(e)}")
            raise
    
    def search_related(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search for related documents using semantic similarity"""
        if not self.index or not self.documents:
            logger.warning("Index not built or no documents available")
            return []
        
        try:
            # Encode query
            query_embedding = self.embedder.encode([query])
            
            # Search
            distances, indices = self.index.search(
                np.array(query_embedding).astype('float32'), 
                min(top_k, len(self.documents))
            )
            
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.documents):  # Valid index
                    results.append({
                        "file_name": self.file_names[idx],
                        "content": self.documents[idx][:500] + "..." if len(self.documents[idx]) > 500 else self.documents[idx],
                        "similarity_score": float(1 / (1 + distance)),  # Convert distance to similarity
                        "rank": i + 1
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching related documents: {str(e)}")
            return []