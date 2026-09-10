from pathlib import Path

from alinka.docx import generate_document


def test_pyinstaller_places_docx_templates_outside_executable_name():
    spec_file = Path(__file__).parents[1] / "alinka.spec"

    assert "('alinka/docx/templates', 'docx/templates')" in spec_file.read_text()


def test_templates_base_path_uses_pyinstaller_bundle_directory(monkeypatch):
    monkeypatch.setattr(generate_document.sys, "frozen", True, raising=False)
    monkeypatch.setattr(generate_document.sys, "_MEIPASS", "C:/bundle", raising=False)

    assert generate_document.get_templates_base_path() == Path("C:/bundle") / "docx" / "templates"


def test_templates_base_path_uses_module_directory_outside_pyinstaller(monkeypatch):
    monkeypatch.delattr(generate_document.sys, "frozen", raising=False)

    assert (
        generate_document.get_templates_base_path() == Path(generate_document.__file__).resolve().parent / "templates"
    )


def test_templates_base_path_requires_pyinstaller_bundle_directory(monkeypatch):
    monkeypatch.setattr(generate_document.sys, "frozen", True, raising=False)
    monkeypatch.delattr(generate_document.sys, "_MEIPASS", raising=False)

    assert (
        generate_document.get_templates_base_path() == Path(generate_document.__file__).resolve().parent / "templates"
    )


def test_windows_build_uses_preinstalled_inno_setup():
    workflow_file = Path(__file__).parents[1] / ".github" / "workflows" / "_build-win.yml"
    workflow = workflow_file.read_text()

    assert "runs-on: windows-2025" in workflow
    assert "winget install" not in workflow
    assert "Test-Path -LiteralPath $iscc" in workflow
    assert "& $iscc /DAppVersion=" in workflow


def test_packaging_build_runs_for_relevant_pull_requests():
    workflow_file = Path(__file__).parents[1] / ".github" / "workflows" / "build-develop.yml"
    workflow = workflow_file.read_text()

    assert "pull_request:" in workflow
    assert "- alinka.spec" in workflow
    assert "- 'alinka/docx/**'" in workflow
