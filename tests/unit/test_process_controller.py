from unittest.mock import MagicMock

import pytest

from src.controllers.ProcessController import ProcessController

pytestmarker = pytest.mark.unit


@pytest.fixture
def process_controller():
    return ProcessController(project_id="4")


class TestProcessController:
    def test_get_chunks(self, process_controller, mocker):

        mock_tokenizer = MagicMock()
        mock_tokenizer.count_tokens.return_value = 20

        mock_chunker = MagicMock()

        mock_chunk = MagicMock()
        mock_chunk.text = "Attention is all you need"

        mock_chunk.meta = MagicMock()
        mock_chunk.meta.headings = ["Transformer"]
        mock_chunk.meta.doc_items = []

        mock_chunker.chunk.return_value = [mock_chunk]
        mock_chunker.contextualize.return_value = (
            "Transformer\nAttention is all you need"
        )

        mocker.patch("controllers.ProcessController.AutoTokenizer.from_pretrained")

        mocker.patch(
            "controllers.ProcessController.HuggingFaceTokenizer",
            return_value=mock_tokenizer,
        )

        mocker.patch(
            "controllers.ProcessController.HybridChunker", return_value=mock_chunker
        )

        result = controller.get_chunks(
            document=Mock(),
            chunk_size=512,
            chunk_overlap=50,
        )

        assert len(result) == 1
        assert result[0]["text"] == ("Transformer\nAttention is all you need")

        assert result[0]["metadata"]["chunk_index"] == 0
        assert result[0]["metadata"]["token_count"] == 20
