import os
from pathlib import Path

from alinka.docx import generate_document


def test_pyinstaller_places_docx_templates_outside_executable_name():
    spec_file = Path(__file__).parents[1] / "alinka.spec"

    assert "('alinka/docx/templates', 'docx/templates')" in spec_file.read_text()


def test_templates_base_path_uses_pyinstaller_bundle_directory(monkeypatch):
    monkeypatch.setattr(generate_document.sys, "frozen", True, raising=False)
    monkeypatch.setattr(generate_document.sys, "_MEIPASS", "C:/bundle", raising=False)

    assert generate_document.get_templates_base_path() == os.path.join("C:/bundle", "docx", "templates")


def test_windows_build_installs_inno_setup_from_winget():
    workflow_file = Path(__file__).parents[1] / ".github" / "workflows" / "_build-win.yml"

    assert "winget install --id JRSoftware.InnoSetup" in workflow_file.read_text()
