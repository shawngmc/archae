# Warnings

This page documents important warnings and considerations when using Archae.

## Warning Codes

When Archae encounters issues during operation, it logs warnings with specific codes. These codes help identify the root cause of extraction or processing issues, and can also help understand if the extraction result is suitable for your purposes. These are available via the 'WarningTypes' off the archae module.

### DELETION_FAILED

**Cause:** Failed to delete an archive file after extraction.

**Details:** The archive was successfully extracted and marked for deletion (due to `DELETE_ARCHIVES_AFTER_EXTRACTION` setting), but the deletion operation failed due to permission or filesystem errors.

**Resolution:** Check file permissions on the archive file. Ensure the process has write permissions to the parent directory.

### EXTRACTION_FAILED

**Cause:** Archive extraction failed.

**Details:** The extraction tool encountered an error while attempting to decompress the archive. This could be due to corruption, unsupported compression format, or insufficient system resources.

**Resolution:** Verify the archive is not corrupted. Check the system has sufficient disk space and memory. Try extracting manually with the underlying tool (e.g., `7z`, `unar`).

### MAX_ARCHIVE_SIZE_BYTES

**Cause:** Archive exceeds the maximum uncompressed archive size limit.

**Details:** The uncompressed size of the archive is greater than `MAX_ARCHIVE_SIZE_BYTES`. Extraction is skipped as a safety measure.

**Resolution:** Increase `MAX_ARCHIVE_SIZE_BYTES` if you trust the archive source.

### MAX_DEPTH

**Cause:** Maximum extraction depth has been reached.

**Details:** The archive contains nested archives and the nesting level has reached the `MAX_DEPTH` limit.

**Resolution:** Increase `MAX_DEPTH` if you want to extract deeper nested archives. Use caution as deep nesting can indicate an archive bomb.

### MAX_TOTAL_SIZE_BYTES

**Cause:** Total extracted size would exceed the maximum limit.

**Details:** The cumulative size of all extracted files (including previous extractions in this session) would exceed `MAX_TOTAL_SIZE_BYTES`.

**Resolution:** Increase `MAX_TOTAL_SIZE_BYTES` or process archives separately.

### MIN_ARCHIVE_RATIO

**Cause:** Compression ratio is too extreme, suggesting a potential zip bomb.

**Details:** The compression ratio (compressed size / uncompressed size) is below the `MIN_ARCHIVE_RATIO` threshold, indicating unusually high compression.

**Resolution:** Inspect the archive source. If trusted, increase `MIN_ARCHIVE_RATIO`. Be cautious with archives from untrusted sources.

### MIN_DISK_FREE_SPACE

**Cause:** Insufficient disk space would remain during/after extraction.

**Details:** Extracting the archive would leave less free disk space than the `MIN_DISK_FREE_SPACE` threshold requires.

**Resolution:** Free up disk space or increase the extraction partition capacity.

### MISSING_ARCHIVER

**Cause:** Required extraction tool is not installed.

**Details:** The system lacks support for a specific archive format because the required external tool (e.g., `7z`, `unar`) is not installed or not found in the system PATH.

**Resolution:** Install the missing tool and ensure it's on the path, or ignore if you are unconcerned about missing archive formats.

### NO_ARCHIVER

**Cause:** No suitable archiver found for the file.

**Details:** The file's format is not recognized by any installed extraction tool, even though file type detection suggests it might be an archive.

**Resolution:** Install an appropriate extraction tool or verify the file is actually a supported archive format. This should be rare.

### SIZE_RETRIEVAL_FAILED

**Cause:** Could not determine uncompressed archive size.

**Details:** The extraction tool does not support analyzing archive contents (e.g., `unar` cannot report size), or size retrieval failed for another reason.

**Resolution:** This is informational; extraction will continue without pre-flight size validation. Ensure sufficient disk space is available.

### SKIP_DELETE_EXTENSION

**Cause:** Archive not deleted due to its file extension.

**Details:** The archive has a file extension (e.g., `.exe`) in the skip-delete list and is protected from automatic deletion even when `DELETE_ARCHIVES_AFTER_EXTRACTION` is enabled.

**Resolution:** This is informational; these file types often are not pure archives and are significant in other ways.

### SKIP_DELETE_MIMETYPE

**Cause:** Archive not deleted due to its MIME type.

**Details:** The archive has a MIME type (e.g., `application/java-archive`) in the skip-delete list and is protected from automatic deletion.

**Resolution:** This is informational; these file types often are not pure archives and are significant in other ways.
