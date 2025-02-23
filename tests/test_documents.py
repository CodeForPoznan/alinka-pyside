import pytest

from alinka.constants import DocumentsTypes
from alinka.docx.generate_document import DocumentGenerator
from alinka.schemas import DocumentData
from tests.fixtures import common_data

CONTENT = "content"


class TestDocumentGenerator:
    @pytest.mark.parametrize(
        "document_type",
        [
            DocumentsTypes.SPECJALNE,
            DocumentsTypes.INDYWIDUALNE,
            DocumentsTypes.INDYWIDUALNE_ROCZNE,
            DocumentsTypes.REWALIDACYJNE,
            DocumentsTypes.OPINIA,
        ],
    )
    def test_document_generator_files(self, document_type, tmp_path):
        file_name = "test_document_name.docx"
        destination_path = tmp_path
        document_data = DocumentData(**common_data)
        DocumentGenerator(file_name, document_type, document_data, destination_path).generate()

        assert sorted(tmp_path.glob(file_name))
