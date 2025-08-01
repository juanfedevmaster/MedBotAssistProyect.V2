"""
Tools for searching information in vectorized instructional documents
"""

# SQLite fix for Azure App Service BEFORE any other imports
try:
    import sqlite_fix
except ImportError:
    pass

import os
import json
from typing import List, Dict, Any, Optional, Tuple
from openai import OpenAI
import chromadb
from chromadb.config import Settings
from langchain.tools import tool
from app.core.config import settings
from app.services.permission_context import permission_context

class InstructiveSearchTools:
    """Tools for searching information in instructional documents using vectorization"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Initialize ChromaDB client with proper configuration
        try:
            import os
            # Ensure the directory exists
            os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
            
            # Initialize persistent client using settings path
            self.chroma_client = chromadb.PersistentClient(
                path=settings.VECTOR_DB_PATH,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            print(f"ChromaDB initialized successfully at: {settings.VECTOR_DB_PATH}")
            
        except Exception as e:
            print(f"Error: ChromaDB initialization failed: {e}")
            # Don't fall back to in-memory - we need persistence
            raise RuntimeError(f"Vector database initialization failed: {str(e)}")
        
        # Get or create collection
        try:
            self.collection = self.chroma_client.get_collection(name="medical_documents")
        except Exception:
            # If collection doesn't exist, create it
            try:
                self.collection = self.chroma_client.create_collection(
                    name="medical_documents",
                    metadata={"description": "Vectorized medical documents"}
                )
            except Exception as e:
                print(f"Warning: Could not create collection: {e}")
                self.collection = None
                
        # Comprehensive debug logging for InstructiveSearchTools
        try:
            if self.collection:
                all_collections = self.chroma_client.list_collections()
                print(f"DEBUG InstructiveSearchTools: All available collections: {[c.name for c in all_collections]}")
                
                collection_count = self.collection.count()
                print(f"DEBUG InstructiveSearchTools: Collection 'medical_documents' has {collection_count} documents")
                
                if collection_count > 0:
                    # Try to get a sample of documents to verify content exists
                    sample_docs = self.collection.get(limit=3, include=['documents', 'metadatas'])
                    if sample_docs and sample_docs.get('documents'):
                        print(f"DEBUG InstructiveSearchTools: Sample documents found: {len(sample_docs['documents'])}")
                        for i, doc in enumerate(sample_docs['documents'][:2]):  # Show first 2
                            metadata = sample_docs['metadatas'][i] if sample_docs.get('metadatas') else {}
                            print(f"DEBUG InstructiveSearchTools: Doc {i+1} - Filename: {metadata.get('filename', 'unknown')}, Content: {doc[:100]}...")
                    else:
                        print("DEBUG InstructiveSearchTools: No documents found in get() query despite count > 0")
                else:
                    print("DEBUG InstructiveSearchTools: Collection is empty (count = 0)")
            else:
                print("DEBUG InstructiveSearchTools: Collection is None - initialization failed")
                
        except Exception as debug_e:
            print(f"DEBUG InstructiveSearchTools: Debug logging failed: {debug_e}")
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generates embedding for a text using OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []
    
    def _format_search_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Formats ChromaDB search results"""
        formatted_results = []
        
        if not results or not results.get('documents'):
            return formatted_results
        
        documents = results['documents'][0] if results['documents'] else []
        metadatas = results['metadatas'][0] if results.get('metadatas') else []
        distances = results['distances'][0] if results.get('distances') else []
        
        for i, doc in enumerate(documents):
            metadata = metadatas[i] if i < len(metadatas) else {}
            distance = distances[i] if i < len(distances) else 1.0
            similarity = 1 - distance  # Convert distance to similarity
            
            formatted_results.append({
                'content': doc,
                'filename': metadata.get('filename', 'unknown'),
                'file_type': metadata.get('file_type', 'unknown'),
                'chunk_index': metadata.get('chunk_index', 0),
                'similarity_score': round(similarity, 3),
                'metadata': metadata
            })
        
        return formatted_results
    
    def search_instructive_information(
        self, 
        query: str, 
        max_results: int = 5,
        min_similarity: float = 0.2  # Lowered threshold to accommodate distance-based similarity
    ) -> Dict[str, Any]:
        """
        Searches for specific information in vectorized instructional documents
        
        Args:
            query: Question or search about instructional documents
            max_results: Maximum number of results
            min_similarity: Minimum required similarity (0-1)
        
        Returns:
            Dict with search results and generated response
        """
        # Validate permissions
        if not permission_context.has_permission('UseAgent'):
            return {
                'success': False,
                'error': 'You do not have permissions to use the agent',
                'results': []
            }
        
        try:
            # Verify that collection is available
            if not self.collection:
                print("DEBUG: Collection is None")
                return {
                    'success': False,
                    'error': 'Vectorized database not available',
                    'results': []
                }
            
            # Check collection count for debugging
            try:
                count = self.collection.count()
                print(f"DEBUG: Collection has {count} documents")
                if count == 0:
                    return {
                        'success': False,
                        'error': 'No documents found in vectorized database',
                        'results': []
                    }
            except Exception as e:
                print(f"DEBUG: Error getting collection count: {e}")
                return {
                    'success': False,
                    'error': f'Error accessing vectorized database: {str(e)}',
                    'results': []
                }
            
            # Generate embedding for the query
            query_embedding = self._generate_embedding(query)
            if not query_embedding:
                return {
                    'success': False,
                    'error': 'Could not generate embedding for the query',
                    'results': []
                }
            
            # Search in ChromaDB
            search_results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=max_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            formatted_results = self._format_search_results(search_results)
            
            # Filter by minimum similarity
            filtered_results = [
                result for result in formatted_results 
                if result['similarity_score'] >= min_similarity
            ]
            
            if not filtered_results:
                return {
                    'success': True,
                    'message': 'No relevant information found in the instructional documents for your query.',
                    'query': query,
                    'results': [],
                    'total_found': 0
                }
            
            # Generate contextual response using the results
            contextual_response = self._generate_contextual_response(query, filtered_results)
            
            return {
                'success': True,
                'query': query,
                'response': contextual_response,
                'results': filtered_results,
                'total_found': len(filtered_results),
                'sources': list(set([r['filename'] for r in filtered_results]))
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error searching instructional documents: {str(e)}',
                'results': []
            }
    
    def _generate_contextual_response(self, query: str, results: List[Dict[str, Any]]) -> str:
        """Generates a contextual response based on the found results"""
        try:
            # Combine content from the best results
            context_parts = []
            for result in results[:3]:  # Top 3 results
                context_parts.append(f"From {result['filename']}: {result['content']}")
            
            combined_context = "\n\n".join(context_parts)
            
            # Prompt to generate contextual response
            system_prompt = """You're a specialized medical assistant. Your task is to answer questions based exclusively on the information provided in the medical instruction documents.

INSTRUCTIONS:

1. Respond only with information found in the provided context.
2. If the information is not present in the context, state that you do not have that specific information.
3. Cite sources when relevant.
4. Maintain a professional and medical tone.
5. If there are procedures, list them clearly.
6. If there are contraindications or warnings, highlight them.

INSTRUCTIONAL CONTEXT:
{context}

QUESTION: {query}

Respond clearly, accurately, and professionally based solely on the information provided."""

            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": system_prompt.format(context=combined_context, query=query)
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Relevant information was found, but there was an error generating the response: {str(e)}"
    
    def get_available_instructives(self) -> Dict[str, Any]:
        """Gets list of available instructional documents in the database"""
        try:
            # Verify that collection is available
            if not self.collection:
                print("DEBUG: get_available_instructives - Collection is None")
                return {
                    'success': True,
                    'instructives': [],
                    'total_files': 0,
                    'message': 'Vectorized database not available'
                }
            
            # Check collection count
            try:
                count = self.collection.count()
                print(f"DEBUG: get_available_instructives - Collection has {count} documents")
                if count == 0:
                    return {
                        'success': True,
                        'instructives': [],
                        'total_files': 0,
                        'message': 'No documents in vectorized database'
                    }
            except Exception as e:
                print(f"DEBUG: get_available_instructives - Error getting count: {e}")
                return {
                    'success': True,
                    'instructives': [],
                    'total_files': 0,
                    'message': f'Error accessing database: {str(e)}'
                }
            
            # Get some documents to extract unique metadata
            sample_results = self.collection.query(
                query_embeddings=[self._generate_embedding("medical")],
                n_results=100,
                include=['metadatas']
            )
            
            print(f"DEBUG: get_available_instructives - Query returned: {sample_results}")
            
            if not sample_results or not sample_results.get('metadatas'):
                return {
                    'success': True,
                    'instructives': [],
                    'total_files': 0,
                    'message': 'No vectorized instructional documents available'
                }
            
            # Extract unique files
            files_info = {}
            for metadata in sample_results['metadatas'][0]:
                filename = metadata.get('filename', 'unknown')
                file_type = metadata.get('file_type', 'unknown')
                
                if filename not in files_info:
                    files_info[filename] = {
                        'filename': filename,
                        'file_type': file_type,
                        'chunks_count': 0
                    }
                files_info[filename]['chunks_count'] += 1
            
            instructives_list = list(files_info.values())
            
            return {
                'success': True,
                'instructives': instructives_list,
                'total_files': len(instructives_list),
                'message': f'Found {len(instructives_list)} available instructional documents'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error getting list of instructional documents: {str(e)}',
                'instructives': []
            }
    
    def search_by_filename(self, filename: str, query: str = "") -> Dict[str, Any]:
        """Searches for information in a specific file"""
        try:
            # If there's no specific query, search for all document content
            if not query:
                query = "document content"
            
            query_embedding = self._generate_embedding(query)
            if not query_embedding:
                return {
                    'success': False,
                    'error': 'Could not generate embedding for the query'
                }
            
            # Search with filename filter
            search_results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=20,
                include=['documents', 'metadatas', 'distances'],
                where={"filename": filename}
            )
            
            formatted_results = self._format_search_results(search_results)
            
            if not formatted_results:
                return {
                    'success': True,
                    'message': f'File "{filename}" not found in the vectorized database',
                    'results': []
                }
            
            return {
                'success': True,
                'filename': filename,
                'query': query,
                'results': formatted_results,
                'total_chunks': len(formatted_results)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error searching in specific file: {str(e)}',
                'results': []
            }

# Global instance to use in the agent
instructive_search_tools = InstructiveSearchTools()

# LangChain tools to use in the medical agent
@tool
def search_instructive_info(query: str) -> str:
    """
    Searches for information in vectorized medical instructional documents.
    
    Use this tool when the user asks about medical procedures,
    protocols, medication administration, or any specific information
    that may be in medical instructional documents.
    
    Args:
        query: The query about medical information (e.g., "insulin administration")
    
    Returns:
        Information found in medical instructional documents with cited sources
    """
    try:
        result = instructive_search_tools.search_instructive_information(
            query=query, 
            max_results=5
        )
        
        if not result['success']:
            return f"Error: {result.get('error', 'Unknown error')}"
        
        if result['total_found'] == 0:
            return "No relevant information found in the instructional documents for your query."
        
        response = result['response']
        sources = ", ".join(result['sources'])
        
        return f"""**Instructional Information:**

{response}

**Sources consulted:** {sources}
**Documents found:** {result['total_found']}"""
        
    except Exception as e:
        return f"Error searching instructional documents: {str(e)}"

@tool
def get_available_instructives_list() -> str:
    """
    Gets the list of available medical instructional documents in the system.
    
    Use this tool when the user asks what instructional documents
    or medical documents are available for consultation.
    
    Returns:
        List of available medical instructional documents with details
    """
    try:
        result = instructive_search_tools.get_available_instructives()
        
        if not result['success']:
            return f"Error: {result.get('error', 'Unknown error')}"
        
        if result['total_files'] == 0:
            return "No vectorized instructional documents available in the system."
        
        instructives_text = "**Available Instructional Documents:**\n\n"
        for doc in result['instructives']:
            instructives_text += f"• **{doc['filename']}** ({doc['file_type']}) - {doc['chunks_count']} sections\n"
        
        instructives_text += f"\n**Total:** {result['total_files']} instructional documents available"
        
        return instructives_text
        
    except Exception as e:
        return f"Error getting list of instructional documents: {str(e)}"
