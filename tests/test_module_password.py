from pathlib import Path

from archae.extractor import ArchiveExtractor
from archae.util.enum.warning_types import WarningTypes


def test_detect_all_password_skipped() -> None:
    extract_path = (
        Path(__file__).resolve().parent / "output" / "test_detect_all_password"
    )
    Path.mkdir(extract_path, parents=True, exist_ok=True)
    extractor = ArchiveExtractor(extract_dir=extract_path)
    extractor.handle_file(
        Path(__file__).resolve().parent / "samples" / "password-hello.zip"
    )
    warnings = extractor.get_warnings()
    assert any(
        WarningTypes.PASSWORD_PROTECTED_DETECTED == warning.warning_type
        for warning in warnings
    )
    assert any(
        WarningTypes.PASSWORD_PROTECTED_SKIPPED == warning.warning_type
        for warning in warnings
    )


def test_detect_partial_password() -> None:
    extract_path = (
        Path(__file__).resolve().parent / "output" / "test_detect_partial_password"
    )
    Path.mkdir(extract_path, parents=True, exist_ok=True)
    extractor = ArchiveExtractor(extract_dir=extract_path)
    extractor.handle_file(
        Path(__file__).resolve().parent / "samples" / "password-hello-partial.zip"
    )
    warnings = extractor.get_warnings()
    assert any(
        WarningTypes.PASSWORD_PROTECTED_DETECTED == warning.warning_type
        for warning in warnings
    )
    assert not any(
        WarningTypes.PASSWORD_PROTECTED_SKIPPED == warning.warning_type
        for warning in warnings
    )


def test_detect_no_password() -> None:
    extract_path = (
        Path(__file__).resolve().parent / "output" / "test_detect_no_password"
    )
    Path.mkdir(extract_path, parents=True, exist_ok=True)
    extractor = ArchiveExtractor(extract_dir=extract_path)
    extractor.handle_file(Path(__file__).resolve().parent / "samples" / "sample1.zip")
    warnings = extractor.get_warnings()
    assert not any(
        WarningTypes.PASSWORD_PROTECTED_DETECTED == warning.warning_type
        for warning in warnings
    )
    assert not any(
        WarningTypes.PASSWORD_PROTECTED_SKIPPED == warning.warning_type
        for warning in warnings
    )
