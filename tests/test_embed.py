import logging
import pytest
from src.operations.embed import EmbedService
from unittest.mock import Mock, patch
import os

@pytest.fixture
def embed_service(tmp_path):
    with patch('src.operations.embed.chroma_db') as mock_chroma:
        mock_chroma.collection = Mock()
        service = EmbedService()
        service.input_folder = tmp_path  # Use temporary directory
        return service

def test_embed_success(embed_service):
    with patch('src.operations.embed.embed_texts') as mock_embed:
        mock_embed.return_value = [[0.1, 0.2]]
        result = embed_service.embed("test text")
        assert result == [0.1, 0.2]

def test_store_files_success(embed_service, tmp_path):
    with patch('src.operations.embed.embed_texts') as mock_embed:
        mock_embed.return_value = [[0.1, 0.2]]
        file_path = tmp_path / "test.md"
        file_path.write_text("test content")
        embed_service.store_files([str(file_path)])
        embed_service.collection.add.assert_called_once()

def test_store_files_no_content(embed_service, tmp_path, caplog):
    caplog.set_level(logging.WARNING)
    file_path = tmp_path / "nonexistent.md"
    embed_service.store_files([str(file_path)])
    assert "File not found" in caplog.text
    embed_service.collection.add.assert_not_called()