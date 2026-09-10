from pathlib import Path


def test_pyinstaller_places_docx_templates_inside_docx_package():
    spec_file = Path(__file__).parents[1] / "alinka.spec"

    assert "('alinka/docx/templates', 'alinka/docx/templates')" in spec_file.read_text()
