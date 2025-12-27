import logging
from typing import List, Dict, Any, Optional
import pinecone
from config import settings


class VectorService:
    """Service for vector storage and retrieval using Pinecone."""
    
    def __init__(self):
        self.index = None
        self.initialized = False
        self.logger = logging.getLogger(__name__)
        
        if settings.pinecone_api_key and settings.pinecone_environment:
            self._initialize_pinecone()
        else:
            self.logger.info("Pinecone not configured - vector service disabled")
    
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
                self.logger.info(f"Created Pinecone index: {settings.pinecone_index_name}")
            
            self.index = pinecone.Index(settings.pinecone_index_name)
            self.initialized = True
            self.logger.info("Pinecone vector service initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Pinecone: {e}")
            self.initialized = False
    
    async def store_issue_context(self, issue_id: str, issue_data: Dict[str, Any], embeddings: List[float]) -> bool:
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
            self.logger.info(f"Stored issue context for issue #{issue_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to store issue context: {e}")
            return False
    
    async def store_repository_context(self, repo_name: str, file_path: str, content: str, embeddings: List[float]) -> bool:
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
            self.logger.info(f"Stored repository context for {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to store repository context: {e}")
            return False
    
    async def search_similar_issues(self, query_embeddings: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
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
            
            similar_issues = [
                {
                    "issue_id": match.metadata.get("issue_id"),
                    "title": match.metadata.get("title"),
                    "body": match.metadata.get("body"),
                    "author": match.metadata.get("author"),
                    "score": match.score
                }
                for match in results.matches
            ]
            
            self.logger.info(f"Found {len(similar_issues)} similar issues")
            return similar_issues
            
        except Exception as e:
            self.logger.error(f"Failed to search similar issues: {e}")
            return []
    
    async def search_repository_context(self, query_embeddings: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
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
            
            context_results = [
                {
                    "file_path": match.metadata.get("file_path"),
                    "content": match.metadata.get("content"),
                    "repo_name": match.metadata.get("repo_name"),
                    "score": match.score
                }
                for match in results.matches
            ]
            
            self.logger.info(f"Found {len(context_results)} relevant repository files")
            return context_results
            
        except Exception as e:
            self.logger.error(f"Failed to search repository context: {e}")
            return []
    
    async def get_issue_history_context(self, issue_id: str) -> List[Dict[str, Any]]:
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
            
            self.logger.info(f"Found {len(similar_issues[:10])} historical context issues")
            return similar_issues[:10]  # Return top 10 similar issues
            
        except Exception as e:
            self.logger.error(f"Failed to get issue history context: {e}")
            return []
    
    def is_available(self) -> bool:
        """Check if vector service is available."""
        return self.initialized and self.index is not None
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get vector service status information."""
        return {
            "available": self.is_available(),
            "initialized": self.initialized,
            "index_name": settings.pinecone_index_name if self.initialized else None,
            "service_type": "pinecone"
        } 