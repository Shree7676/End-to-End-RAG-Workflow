import pytest
import logging
from src.operations.ask import LLMAsker
from unittest.mock import Mock, patch

@pytest.fixture
def asker():
    with patch('src.operations.ask.chroma_db') as mock_chroma:
        mock_chroma.collection = Mock()
        asker = LLMAsker()
        asker.search_engine = Mock()
        return asker

def test_ask_successful_response(asker):
    asker.search_engine.search.return_value = ["file1.md"]
    asker.collection.get.return_value = {'documents': ["content1"]}
    with patch('src.operations.ask.execute_prompt') as mock_prompt:
        mock_prompt.return_value = {'response': "Answer text"}
        result = asker.ask("test query")
        assert result == "Answer text"
        mock_prompt.assert_called_once()

def test_ask_api_error(asker, caplog):
    asker.search_engine.search.return_value = ["file1.md"]
    asker.collection.get.return_value = {'documents': ["content1"]}
    with patch('src.operations.ask.execute_prompt') as mock_prompt:
        mock_prompt.side_effect = Exception("API failure")
        result = asker.ask("test query")
        assert "Error processing query: API failure" in result
        assert "Failed to query LLM" in caplog.text