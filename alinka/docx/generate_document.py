import os
import sys
from zipfile import ZipFile

from jinja2 import Environment, FileSystemLoader

from alinka.constants import DocumentsTypes
from alinka.schemas import DocumentData

def get_templates_base_path() -> str:
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "docx", "templates")
    return os.path.join(os.path.dirname(__file__), "templates")


loader = FileSystemLoader(get_templates_base_path())
environment = Environment(loader=loader)


class DocumentGenerator:
    """Handle single document generation"""

    def __init__(
        self, document_name: str, decision_type: DocumentsTypes, document_data: DocumentData, destination_path: str
    ):
        self.document_name = document_name
        self.document_type = decision_type.value
        self.document_data = document_data
        # Template always use forward slashes
        # see: https://github.com/pallets/jinja/pull/1579
        self.template = environment.get_template("/".join([self.document_type, "word", "document.xml"]))
        self.destination_path = os.path.join(destination_path, document_name)

    @property
    def files_path_parts(self):
        return [
            ["_rels", ".rels"],
            ["word", "_rels", "document.xml.rels"],
            ["word", "theme", "theme1.xml"],
            ["word", "endnotes.xml"],
            ["word", "fontTable.xml"],
            ["word", "numbering.xml"],
            ["word", "settings.xml"],
            ["word", "styles.xml"],
            ["word", "webSettings.xml"],
            ["[Content_Types].xml"],
        ]

    @property
    def footnotes_file_path(self) -> str:
        return "/".join([self.document_type, "word", "footnotes.xml"])

    def get_rendered_document(self):
        data = self.document_data.model_dump()
        return self.template.render(data)

    def _get_resource_bytes(self, template_name: str) -> bytes:
        # Read template content via Jinja loader regardless of filesystem location
        source, _, _ = environment.loader.get_source(environment, template_name)
        return source.encode("utf-8")

    def generate(self):
        with ZipFile(self.destination_path, "w") as document:
            # Write common static files from the packaged templates
            for path_parts in self.files_path_parts:
                file_arch_path = "/".join(path_parts)  # Jinja loader expects forward slashes
                common_template_name = "/".join(["commons", file_arch_path])
                document.writestr(zinfo_or_arcname=file_arch_path, data=self._get_resource_bytes(common_template_name))

            # Write footnotes file for the specific document type
            document.writestr(
                data=self._get_resource_bytes(self.footnotes_file_path),
                zinfo_or_arcname=os.path.join("word", "footnotes.xml"),
            )

            # Write rendered document.xml
            document.writestr(
                data=self.get_rendered_document(),
                zinfo_or_arcname=os.path.join("word", "document.xml"),
            )


class Documents:
    """Create multiple required documents, based on requested list of documents types and data for documents."""

    def __init__(self, documents_types: list[DocumentsTypes], document_data: dict, destination_path: str):
        self.documents_types = documents_types
        self.document_data = DocumentData(**document_data)
        self.destination_path = os.path.join(destination_path, self.dir_name)
        if not os.path.exists(self.destination_path):
            os.makedirs(self.destination_path)

    def create(self) -> None:
        for document_type in self.documents_types:
            DocumentGenerator(
                document_name=self.get_document_name(document_type),
                decision_type=document_type,
                document_data=self.document_data,
                destination_path=self.destination_path,
            ).generate()

    @property
    def __full_name_date(self) -> str:
        return f"{self.document_data.child.full_name}_{self.document_data.meeting_data.date}"

    @property
    def dir_name(self) -> str:
        """name of dir for current child eg "Erwin_Frankl_24_12_2010_spec"""
        return f"{self.__full_name_date}_{self.document_data.issue_short}"

    def get_document_name(self, document_type: DocumentsTypes) -> str:
        return f"{self.__full_name_date}_{document_type.value}.docx"
