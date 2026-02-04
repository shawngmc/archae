# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Calendar Versioning](https://calver.org/).

The **first number** of the version is the year.
The **second number** is incremented with each release, starting at 1 for each year.
The **third number** is for emergencies when we need to start branches for older releases.

## 2026.4

- Archivers: Removed PeaZip - CLI syntax is not well-documented, adds few formats
    - Loses ZStandard (.zst application/zstd) and Brotli (.br application/x-brotli)
- CLI: Clean 'No Warnings' message
- Fix: Fixed bug blocking unar due to lack of size analysis code
- Fix: Allow non-str options that failed in some circumstances
- Misc: Internal logic cleanup
- Metadata: Tracks archive files deleted
- Tests: Vastly improved unit test coverage for options

## 2026.3

- Fix version numbering
- Add delete-after-extraction
- Various fixes

## TODOs

- Programmatic list of warning prefixes
- Improve archive type detection
- Separate between extractable and non-extractable archive types - started, but needs a bit more refinement
- Detect password-protected archives
- Allow supplying archive passwords by hash
- Add custom magic to detect obscure archive formats
- Add Brotli: .br / application/x-brotli
- Add ZStandard: .zst / application/zstd
- Enforce archiver orderering (7z > unar, since 7z can analyze w/o extraction)
