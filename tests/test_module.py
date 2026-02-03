from pathlib import Path

import pytest
from click.testing import CliRunner

from archae.extractor import ArchiveExtractor


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_run_as_module() -> None:
    extract_path = Path(__file__).resolve().parent / "output" / "test_module"
    Path.mkdir(extract_path, parents=True, exist_ok=True)
    extractor = ArchiveExtractor(extract_dir=extract_path)
    extractor.handle_file(Path(__file__).resolve().parent / "samples" / "sample1.zip")
