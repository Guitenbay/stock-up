from pathlib import Path


def test_readme_documents_core_commands():
    text = Path("README.md").read_text(encoding="utf-8")
    assert "stock-up init" in text
    assert "stock-up tick" in text
    assert "stock-up daily" in text
    assert "wolf_swing" in text
    assert "hai_long" in text
