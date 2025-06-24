from typing import List, Dict, Any, Optional
import pinecone
from config import settings


class VectorService:
    """Service for vector storage and retrieval using Pinecone."""
    
    def __init__(self):
        self.index = None
        self.initialized = False
        
        if settings.pinecone_api_key and settings.pinecone_environment:
            self._initialize_pinecone()
    
    def _initialize_pinecone(self):
        """Initialize Pinecone client and index."""
        try:
            pinecone.init(
                api_key=settings.pinecone_api_key,
                environment=settings.pinecone_environment
            )
            
            # Check if index exists, create if not
            if settings.pinecone_index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=settings.pinecone_index_name,
                    dimension=1536,  # OpenAI embedding dimension
                    metric="cosine"
                )
            
            self.index = pinecone.Index(settings.pinecone_index_name)
            self.initialized = True
        except Exception as e:
            print(f"Failed to initialize Pinecone: {e}")
            self.initialized = False
    
    def store_issue_context(self, issue_id: str, issue_data: Dict[str, Any], embeddings: List[float]) -> bool:
        """Store issue context in vector database."""
        if not self.initialized or not self.index:
            return False
        
        try:
            metadata = {
                "issue_id": issue_id,
                "title": issue_data.get("title", ""),
                "body": issue_data.get("body", ""),
                "author": issue_data.get("user", {}).get("login", ""),
                "type": "issue"
            }
            
            self.index.upsert(
                vectors=[(issue_id, embeddings, metadata)]
            )
            return True
        except Exception as e:
            print(f"Failed to store issue context: {e}")
            return False
    
    def store_repository_context(self, repo_name: str, file_path: str, content: str, embeddings: List[float]) -> bool:
        """Store repository file context in vector database."""
        if not self.initialized or not self.index:
            return False
        
        try:
            vector_id = f"{repo_name}:{file_path}"
            metadata = {
                "repo_name": repo_name,
                "file_path": file_path,
                "content": content[:1000],  # Limit content size
                "type": "repository_file"
            }
            
            self.index.upsert(
                vectors=[(vector_id, embeddings, metadata)]
            )
            return True
        except Exception as e:
            print(f"Failed to store repository context: {e}")
            return False
    
    def search_similar_issues(self, query_embeddings: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar issues based on embeddings."""
        if not self.initialized or not self.index:
            return []
        
        try:
            results = self.index.query(
                vector=query_embeddings,
                top_k=top_k,
                filter={"type": "issue"},
                include_metadata=True
            )
            
            return [
                {
                    "issue_id": match.metadata.get("issue_id"),
                    "title": match.metadata.get("title"),
                    "body": match.metadata.get("body"),
                    "author": match.metadata.get("author"),
                    "score": match.score
                }
                for match in results.matches
            ]
        except Exception as e:
            print(f"Failed to search similar issues: {e}")
            return []
    
    def search_repository_context(self, query_embeddings: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for relevant repository context based on embeddings."""
        if not self.initialized or not self.index:
            return []
        
        try:
            results = self.index.query(
                vector=query_embeddings,
                top_k=top_k,
                filter={"type": "repository_file"},
                include_metadata=True
            )
            
            return [
                {
                    "file_path": match.metadata.get("file_path"),
                    "content": match.metadata.get("content"),
                    "repo_name": match.metadata.get("repo_name"),
                    "score": match.score
                }
                for match in results.matches
            ]
        except Exception as e:
            print(f"Failed to search repository context: {e}")
            return []
    
    def get_issue_history_context(self, issue_id: str) -> List[Dict[str, Any]]:
        """Get historical context for an issue."""
        if not self.initialized or not self.index:
            return []
        
        try:
            results = self.index.query(
                vector=[0] * 1536,  # Dummy vector for metadata-only query
                top_k=100,
                filter={"type": "issue"},
                include_metadata=True
            )
            
            # Filter and sort by relevance to the current issue
            similar_issues = []
            for match in results.matches:
                if match.metadata.get("issue_id") != issue_id:
                    similar_issues.append({
                        "issue_id": match.metadata.get("issue_id"),
                        "title": match.metadata.get("title"),
                        "body": match.metadata.get("body"),
                        "author": match.metadata.get("author"),
                        "score": match.score
                    })
            
            return similar_issues[:10]  # Return top 10 similar issues
        except Exception as e:
            print(f"Failed to get issue history context: {e}")
            return []
    
    def is_available(self) -> bool:
        """Check if vector service is available."""
        return self.initialized and self.index is not None 