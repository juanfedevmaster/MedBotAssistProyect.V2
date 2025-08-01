"""
Tools for searching information in vectorized instructional documents using in-memory storage
"""

import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from langchain.tools import tool
from app.core.config import settings
from app.services.permission_context import permission_context

class InstructiveSearchTools:
    """Tools for searching information in instructional documents using in-memory vectorization"""
    
    def __init__(self, vectorization_manager=None):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.vectorization_manager = vectorization_manager
        print("InstructiveSearchTools initialized with in-memory vector storage")
        
    def set_vectorization_manager(self, vectorization_manager):
        """Set the vectorization manager instance."""
        self.vectorization_manager = vectorization_manager
        print(f"VectorizationManager set with {vectorization_manager.get_document_count()} documents")
    
    def _get_document_count(self) -> int:
        """Get the number of vectorized documents."""
        if not self.vectorization_manager:
            return 0
        return self.vectorization_manager.get_document_count()
    
    def _search_documents(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search for documents similar to the query."""
        if not self.vectorization_manager:
            print(f"DEBUG: No vectorization manager available")
            return []
        
        if self.vectorization_manager.get_document_count() == 0:
            print(f"DEBUG: No documents available in vectorization manager")
            return []
        
        try:
            # Generate embedding for the query
            response = self.openai_client.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL,
                input=[query]
            )
            
            query_embedding = response.data[0].embedding
            print(f"DEBUG: Generated query embedding with {len(query_embedding)} dimensions")
            
            # Search for similar documents
            results = self.vectorization_manager.search_similar(
                query_embedding=query_embedding,
                top_k=max_results
            )
            
            print(f"DEBUG: Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            print(f"ERROR: Error searching documents: {e}")
            return []

    def search_instructive_information(self, query: str, max_results: int = 5, min_similarity: float = 0.2) -> Dict[str, Any]:
        """Search for specific information in vectorized instructional documents."""
        # Validate permissions
        if not permission_context.has_permission('UseAgent'):
            return {
                'success': False,
                'error': 'You do not have permissions to use the agent',
                'results': []
            }
        
        try:
            if not self.vectorization_manager:
                return {
                    'success': False,
                    'error': 'Vectorized database not available',
                    'results': []
                }
            
            if self.vectorization_manager.get_document_count() == 0:
                return {
                    'success': False,
                    'error': 'No documents found in vectorized database',
                    'results': []
                }
            
            # Search for documents
            results = self._search_documents(query, max_results)
            
            # Filter by minimum similarity
            filtered_results = [
                result for result in results 
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
            
            # Generate contextual response
            context_parts = []
            sources = set()
            
            for result in filtered_results[:3]:  # Top 3 results
                content = result['content']
                filename = result['metadata'].get('filename', 'unknown')
                sources.add(filename)
                context_parts.append(f"From {filename}: {content}")
            
            combined_context = "\n\n".join(context_parts)
            
            # Generate response using OpenAI
            system_prompt = f"""You're a specialized medical assistant. Answer the question based exclusively on the information provided.

INSTRUCTIONAL CONTEXT:
{combined_context}

QUESTION: {query}

Respond clearly and professionally based solely on the information provided."""

            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": system_prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            contextual_response = response.choices[0].message.content.strip()
            
            return {
                'success': True,
                'query': query,
                'response': contextual_response,
                'results': filtered_results,
                'total_found': len(filtered_results),
                'sources': list(sources)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error searching instructional documents: {str(e)}',
                'results': []
            }

    def get_available_instructives(self) -> Dict[str, Any]:
        """Gets list of available instructional documents in the database"""
        try:
            if not self.vectorization_manager:
                return {
                    'success': True,
                    'instructives': [],
                    'total_files': 0,
                    'message': 'Vectorized database not available'
                }
            
            document_count = self.vectorization_manager.get_document_count()
            if document_count == 0:
                return {
                    'success': True,
                    'instructives': [],
                    'total_files': 0,
                    'message': 'No documents in vectorized database'
                }
            
            # Get unique files from documents
            files_info = {}
            for doc_id, doc in self.vectorization_manager.documents.items():
                filename = doc.metadata.get('filename', 'unknown')
                file_type = doc.metadata.get('file_type', 'unknown')
                
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
            if not self.vectorization_manager:
                return {
                    'success': False,
                    'error': 'Vectorization system not available'
                }
            
            if not query:
                query = "document content"
            
            # Search all documents and filter by filename
            results = self._search_documents(query, max_results=20)
            
            # Filter by filename
            filtered_results = [
                result for result in results 
                if result['metadata'].get('filename') == filename
            ]
            
            if not filtered_results:
                return {
                    'success': True,
                    'message': f'File "{filename}" not found in the vectorized database',
                    'results': []
                }
            
            return {
                'success': True,
                'filename': filename,
                'query': query,
                'results': filtered_results,
                'total_chunks': len(filtered_results)
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
        # Check if vectorization manager is available
        if not instructive_search_tools.vectorization_manager:
            return "No vectorized instructional documents available in the system."
        
        document_count = instructive_search_tools._get_document_count()
        if document_count == 0:
            return "No vectorized instructional documents available in the system."
        
        # Search for documents
        results = instructive_search_tools._search_documents(query, max_results=5)
        
        if not results:
            return "No relevant information found in the instructional documents for your query."
        
        # Generate contextual response
        context_parts = []
        sources = set()
        
        for result in results[:3]:  # Top 3 results
            content = result['content']
            filename = result['metadata'].get('filename', 'unknown')
            sources.add(filename)
            context_parts.append(f"From {filename}: {content}")
        
        combined_context = "\n\n".join(context_parts)
        
        # Generate response using OpenAI
        system_prompt = f"""You're a specialized medical assistant. Answer the question based exclusively on the information provided.

INSTRUCTIONAL CONTEXT:
{combined_context}

QUESTION: {query}

Respond clearly and professionally based solely on the information provided."""

        response = instructive_search_tools.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": system_prompt}],
            max_tokens=500,
            temperature=0.3
        )
        
        contextual_response = response.choices[0].message.content.strip()
        sources_str = ", ".join(sources)
        
        return f"""**Instructional Information:**

{contextual_response}

**Sources consulted:** {sources_str}
**Documents found:** {len(results)}"""
        
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
        # Check if vectorization manager is available
        if not instructive_search_tools.vectorization_manager:
            return "No vectorization system available."
        
        document_count = instructive_search_tools._get_document_count()
        if document_count == 0:
            return "No instructional documents have been vectorized yet."
        
        # Get unique files from documents
        files_info = {}
        for doc_id, doc in instructive_search_tools.vectorization_manager.documents.items():
            filename = doc.metadata.get('filename', 'unknown')
            file_type = doc.metadata.get('file_type', 'unknown')
            
            if filename not in files_info:
                files_info[filename] = {
                    'filename': filename,
                    'file_type': file_type,
                    'chunks_count': 0
                }
            files_info[filename]['chunks_count'] += 1
        
        if not files_info:
            return "No instructional documents found in the system."
        
        # Format the response
        response_lines = ["**Available Instructional Documents:**\n"]
        
        for file_info in files_info.values():
            response_lines.append(
                f"- **{file_info['filename']}** ({file_info['file_type']}) - {file_info['chunks_count']} chunks"
            )
        
        response_lines.append(f"\n**Total:** {len(files_info)} documents with {document_count} total chunks")
        
        return "\n".join(response_lines)
        
    except Exception as e:
        return f"Error getting list of instructional documents: {str(e)}"
