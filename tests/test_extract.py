import logging
import pytest
from src.operations.extract import MarkdownExtractor
from unittest.mock import patch, Mock
from pathlib import Path

@pytest.fixture
def extractor(tmp_path):
    extractor = MarkdownExtractor()
    extractor.output_md_dir = str(tmp_path)  
    return extractor

def test_extract_pdf(extractor, tmp_path):
    with patch('src.operations.extract.convert_from_path') as mock_convert:
        mock_convert.return_value = [Mock()]  
        with patch('src.operations.extract.DocumentConverter') as mock_doc:
            mock_doc_instance = mock_doc.return_value
            mock_doc_instance.convert.return_value.document.export_to_markdown.return_value = "markdown"
            extractor.extract(str(tmp_path / "test.pdf"))
            assert (Path(tmp_path) / "test.md").exists()

def test_extract_unsupported_file(extractor, caplog):
    caplog.set_level(logging.WARNING)
    extractor.extract("test.txt")
    assert "Unsupported file type" in caplog.text