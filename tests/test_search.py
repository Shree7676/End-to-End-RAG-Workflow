import pytest
import logging
from src.operations.search import SearchEngine
from unittest.mock import Mock, patch

@pytest.fixture
def search_engine():
    with patch('src.operations.search.chroma_db') as mock_chroma:
        mock_chroma.collection = Mock()
        return SearchEngine()

def test_search_success(search_engine):
    with patch('src.operations.search.embed_texts') as mock_embed:
        mock_embed.return_value = [[0.1, 0.2]]
        search_engine.collection.query.return_value = {'ids': [["file1.md", "file2.md"]]}
        result = search_engine.search("test query", top_k=2)
        assert result == ["file1.md", "file2.md"]
        mock_embed.assert_called_once_with(["test query"], 'query')

def test_search_embedding_failure(search_engine, caplog):
    caplog.set_level(logging.ERROR)
    with patch('src.operations.search.embed_texts') as mock_embed:
        mock_embed.side_effect = Exception("Embedding error")
        result = search_engine.search("test query")
        assert result == []
        assert "Failed to generate query embedding" in caplog.text

def test_search_empty_results(search_engine):
    with patch('src.operations.search.embed_texts') as mock_embed:
        mock_embed.return_value = [[0.1, 0.2]]
        search_engine.collection.query.return_value = {'ids': [[]]}
        result = search_engine.search("test query")
        assert result == []