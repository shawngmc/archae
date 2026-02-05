import shutil
from pathlib import Path

from archae.extractor import ArchiveExtractor
from archae.util.enum.warning_types import WarningTypes


def test_run_as_module() -> None:
    extract_path = Path(__file__).resolve().parent / "output" / "test_module"
    Path.mkdir(extract_path, parents=True, exist_ok=True)
    extractor = ArchiveExtractor(extract_dir=extract_path)
    extractor.handle_file(Path(__file__).resolve().parent / "samples" / "sample1.zip")


def test_module_max_depth_warn() -> None:
    extract_path = (
        Path(__file__).resolve().parent / "output" / "test_module_max_depth_warn"
    )
    Path.mkdir(extract_path, parents=True, exist_ok=True)
    extractor = ArchiveExtractor(extract_dir=extract_path)
    extractor.apply_options({"MAX_DEPTH": 2})
    extractor.handle_file(Path(__file__).resolve().parent / "samples" / "sample1.zip")
    warnings = extractor.get_warnings()
    assert any(WarningTypes.MAX_DEPTH == warning.warning_type for warning in warnings)


def test_module_max_depth_ok() -> None:
    extract_path = (
        Path(__file__).resolve().parent / "output" / "test_module_max_depth_ok"
    )
    Path.mkdir(extract_path, parents=True, exist_ok=True)
    extractor = ArchiveExtractor(extract_dir=extract_path)
    extractor.apply_options({"MAX_DEPTH": 5})
    extractor.handle_file(Path(__file__).resolve().parent / "samples" / "sample1.zip")
    warnings = extractor.get_warnings()
    assert not any(
        WarningTypes.MAX_DEPTH == warning.warning_type for warning in warnings
    )


def test_total_bytes_warn() -> None:
    extract_path = (
        Path(__file__).resolve().parent / "output" / "test_module_total_bytes_warn"
    )
    Path.mkdir(extract_path, parents=True, exist_ok=True)
    extractor = ArchiveExtractor(extract_dir=extract_path)
    extractor.apply_options({"MAX_TOTAL_SIZE_BYTES": 100})
    extractor.handle_file(Path(__file__).resolve().parent / "samples" / "sample1.zip")
    warnings = extractor.get_warnings()
    assert any(
        WarningTypes.MAX_TOTAL_SIZE_BYTES == warning.warning_type
        for warning in warnings
    )


def test_total_bytes_ok() -> None:
    extract_path = (
        Path(__file__).resolve().parent / "output" / "test_module_total_bytes_ok"
    )
    Path.mkdir(extract_path, parents=True, exist_ok=True)
    extractor = ArchiveExtractor(extract_dir=extract_path)
    extractor.apply_options({"MAX_TOTAL_SIZE_BYTES": "10G"})
    extractor.handle_file(Path(__file__).resolve().parent / "samples" / "sample1.zip")
    warnings = extractor.get_warnings()
    assert not any(
        WarningTypes.MAX_TOTAL_SIZE_BYTES == warning.warning_type
        for warning in warnings
    )


def test_compression_ratio_warn() -> None:
    extract_path = (
        Path(__file__).resolve().parent
        / "output"
        / "test_module_compression_ratio_warn"
    )
    Path.mkdir(extract_path, parents=True, exist_ok=True)
    extractor = ArchiveExtractor(extract_dir=extract_path)
    extractor.apply_options({"MIN_ARCHIVE_RATIO": 0.999})
    extractor.handle_file(Path(__file__).resolve().parent / "samples" / "sample1.zip")
    warnings = extractor.get_warnings()
    assert any(
        WarningTypes.MIN_ARCHIVE_RATIO == warning.warning_type for warning in warnings
    )


def test_compression_ratio_ok() -> None:
    extract_path = (
        Path(__file__).resolve().parent / "output" / "test_module_compression_ratio_ok"
    )
    Path.mkdir(extract_path, parents=True, exist_ok=True)
    extractor = ArchiveExtractor(extract_dir=extract_path)
    extractor.apply_options({"MIN_ARCHIVE_RATIO": 0.001})
    extractor.handle_file(Path(__file__).resolve().parent / "samples" / "sample1.zip")
    warnings = extractor.get_warnings()
    assert not any(
        WarningTypes.MIN_ARCHIVE_RATIO == warning.warning_type for warning in warnings
    )


def test_uncompressed_max_warn() -> None:
    extract_path = (
        Path(__file__).resolve().parent / "output" / "test_uncompressed_max_warn"
    )
    Path.mkdir(extract_path, parents=True, exist_ok=True)
    extractor = ArchiveExtractor(extract_dir=extract_path)
    extractor.apply_options({"MAX_ARCHIVE_SIZE_BYTES": 10})
    extractor.handle_file(Path(__file__).resolve().parent / "samples" / "sample1.zip")
    warnings = extractor.get_warnings()
    assert any(
        WarningTypes.MAX_ARCHIVE_SIZE_BYTES == warning.warning_type
        for warning in warnings
    )


def test_uncompressed_max_ok() -> None:
    extract_path = (
        Path(__file__).resolve().parent / "output" / "test_uncompressed_max_ok"
    )
    Path.mkdir(extract_path, parents=True, exist_ok=True)
    extractor = ArchiveExtractor(extract_dir=extract_path)
    extractor.apply_options({"MAX_ARCHIVE_SIZE_BYTES": "10G"})
    extractor.handle_file(Path(__file__).resolve().parent / "samples" / "sample1.zip")
    warnings = extractor.get_warnings()
    assert not any(
        WarningTypes.MAX_ARCHIVE_SIZE_BYTES == warning.warning_type
        for warning in warnings
    )


def test_disk_free_warn() -> None:
    extract_path = Path(__file__).resolve().parent / "output" / "test_disk_free_warn"
    Path.mkdir(extract_path, parents=True, exist_ok=True)
    extractor = ArchiveExtractor(extract_dir=extract_path)
    extractor.apply_options({"MIN_DISK_FREE_SPACE": "10P"})
    extractor.handle_file(Path(__file__).resolve().parent / "samples" / "sample1.zip")
    warnings = extractor.get_warnings()
    assert any(
        WarningTypes.MIN_DISK_FREE_SPACE == warning.warning_type for warning in warnings
    )


def test_disk_free_ok() -> None:
    extract_path = Path(__file__).resolve().parent / "output" / "test_disk_free_ok"
    Path.mkdir(extract_path, parents=True, exist_ok=True)
    extractor = ArchiveExtractor(extract_dir=extract_path)
    extractor.apply_options({"MIN_DISK_FREE_SPACE": 10})
    extractor.handle_file(Path(__file__).resolve().parent / "samples" / "sample1.zip")
    warnings = extractor.get_warnings()
    assert not any(
        WarningTypes.MIN_DISK_FREE_SPACE == warning.warning_type for warning in warnings
    )


def test_delete() -> None:
    extract_path = Path(__file__).resolve().parent / "output" / "test_delete"
    Path.mkdir(extract_path, parents=True, exist_ok=True)
    extractor = ArchiveExtractor(extract_dir=extract_path)
    extractor.apply_options({"DELETE_ARCHIVES_AFTER_EXTRACTION": "True"})
    temp_zip_path = extract_path / "sample1.zip"
    shutil.copy(
        Path(__file__).resolve().parent / "samples" / "sample1.zip", temp_zip_path
    )
    extractor.handle_file(temp_zip_path)
    assert not Path(temp_zip_path).exists()


def test_no_delete() -> None:
    extract_path = Path(__file__).resolve().parent / "output" / "test_no_delete"
    Path.mkdir(extract_path, parents=True, exist_ok=True)
    extractor = ArchiveExtractor(extract_dir=extract_path)
    extractor.apply_options({"DELETE_ARCHIVES_AFTER_EXTRACTION": "False"})
    temp_zip_path = extract_path / "sample1.zip"
    shutil.copy(
        Path(__file__).resolve().parent / "samples" / "sample1.zip", temp_zip_path
    )
    extractor.handle_file(temp_zip_path)
    assert Path(temp_zip_path).exists()
