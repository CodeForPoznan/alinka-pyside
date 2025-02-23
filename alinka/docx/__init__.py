from alinka.config import settings
from alinka.constants import DocumentsTypes
from alinka.db.queries import get_decision_data_from_db

from .generate_document import Documents
from .utils import convert_raw_documents_data


def generate_documents(record_id: str) -> None:
    list_of_documents_to_generate = [DocumentsTypes.ZARZADZANIE, DocumentsTypes.ZAWIADOMIENIE, DocumentsTypes.PROTOKOL]
    raw_documents_data = get_decision_data_from_db(record_id)
    document_data = convert_raw_documents_data(raw_documents_data)
    destination_path = settings.DOCUMENTS_PATH

    Documents(
        documents_types=[document_data.issue, *list_of_documents_to_generate],
        document_data=document_data.model_dump(),
        destination_path=destination_path,
    ).create()
