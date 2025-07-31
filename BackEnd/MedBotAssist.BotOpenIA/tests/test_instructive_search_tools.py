"""
Tests para las herramientas de búsqueda de instructivos
"""
import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.tools.instructive_search_tools import (
    InstructiveSearchTools,
    search_instructive_info,
    get_available_instructives_list
)
from app.services.permission_context import permission_context

class TestInstructiveSearchTools:
    """Test class for instructive search tools"""
    
    @pytest.fixture
    def search_tools(self):
        """Fixture to create InstructiveSearchTools instance"""
        return InstructiveSearchTools()
    
    @pytest.fixture
    def mock_permissions(self):
        """Mock permissions for testing"""
        permissions = {
            'UseAgent': True,
            'ViewPatients': True,
            'ManagePatients': False
        }
        permission_context.set(permissions)
        yield permissions
        permission_context.clear()
    
    def test_instructive_search_tools_initialization(self, search_tools):
        """Test that InstructiveSearchTools initializes correctly"""
        assert search_tools is not None
        assert search_tools.openai_client is not None
        assert search_tools.chroma_client is not None
        assert search_tools.collection is not None
    
    def test_generate_embedding(self, search_tools):
        """Test embedding generation"""
        text = "medical procedure"
        embedding = search_tools._generate_embedding(text)
        
        # OpenAI embeddings should return a list of floats
        if embedding:  # Only test if OpenAI is available
            assert isinstance(embedding, list)
            assert len(embedding) > 0
            assert all(isinstance(x, float) for x in embedding)
    
    def test_search_instructive_information_without_permissions(self, search_tools):
        """Test search without proper permissions"""
        # Clear permissions
        permission_context.clear()
        
        result = search_tools.search_instructive_information("test query")
        
        assert result['success'] is False
        assert 'permisos' in result['error'].lower()
    
    def test_search_instructive_information_with_permissions(self, search_tools, mock_permissions):
        """Test search with proper permissions"""
        result = search_tools.search_instructive_information("medical procedure")
        
        # Should succeed even if no results found
        assert 'success' in result
        assert 'query' in result
        assert result['query'] == "medical procedure"
    
    def test_get_available_instructives(self, search_tools, mock_permissions):
        """Test getting available instructives"""
        result = search_tools.get_available_instructives()
        
        assert result['success'] is True
        assert 'instructives' in result
        assert 'total_files' in result
        assert isinstance(result['instructives'], list)
        assert isinstance(result['total_files'], int)
    
    def test_search_by_filename(self, search_tools, mock_permissions):
        """Test searching by specific filename"""
        result = search_tools.search_by_filename("test_document.pdf", "content")
        
        assert result['success'] is True
        assert 'results' in result
    
    def test_format_search_results_empty(self, search_tools):
        """Test formatting empty search results"""
        empty_results = {'documents': [], 'metadatas': [], 'distances': []}
        formatted = search_tools._format_search_results(empty_results)
        
        assert formatted == []
    
    def test_format_search_results_with_data(self, search_tools):
        """Test formatting search results with data"""
        mock_results = {
            'documents': [['test document content']],
            'metadatas': [[{'filename': 'test.pdf', 'file_type': 'pdf', 'chunk_index': 0}]],
            'distances': [[0.2]]
        }
        
        formatted = search_tools._format_search_results(mock_results)
        
        assert len(formatted) == 1
        assert formatted[0]['content'] == 'test document content'
        assert formatted[0]['filename'] == 'test.pdf'
        assert formatted[0]['similarity_score'] == 0.8  # 1 - 0.2
    
    def test_search_instructive_info_function(self, mock_permissions):
        """Test the agent function for searching instructive info"""
        result = search_instructive_info("medical procedure")
        
        # Should return a string response
        assert isinstance(result, str)
        # Should contain either error message or information
        assert len(result) > 0
    
    def test_get_available_instructives_list_function(self, mock_permissions):
        """Test the agent function for getting instructives list"""
        result = get_available_instructives_list()
        
        # Should return a string response
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_search_instructive_info_function_without_permissions(self):
        """Test search function without permissions"""
        permission_context.clear()
        
        result = search_instructive_info("test query")
        
        assert isinstance(result, str)
        assert "❌ Error" in result
    
    def test_contextual_response_generation(self, search_tools):
        """Test contextual response generation"""
        mock_results = [
            {
                'content': 'Patient should take medication twice daily',
                'filename': 'medication_guide.pdf',
                'similarity_score': 0.9
            }
        ]
        
        try:
            response = search_tools._generate_contextual_response("How often should patient take medication?", mock_results)
            assert isinstance(response, str)
            assert len(response) > 0
        except Exception as e:
            # If OpenAI is not available, expect an error message
            assert "error" in str(e).lower() or "api" in str(e).lower()

if __name__ == "__main__":
    pytest.main([__file__])
