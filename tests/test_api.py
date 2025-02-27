import pytest
from src import api
from unittest.mock import patch

def test_execute_prompt_success():
    with patch('src.api.requests.post') as mock_post:
        mock_post.return_value.json.return_value = {'response': "test answer"}
        result = api.execute_prompt("test prompt")
        assert result['response'] == "test answer"

def test_embed_texts_success():
    with patch('src.api.requests.post') as mock_post:
        mock_post.return_value.json.return_value = {'embeddings': [[0.1, 0.2]]}
        result = api.embed_texts(["test"], "query")
        assert result == [[0.1, 0.2]]