# MultiSlice Cine Reorder (MuSCiRe)

A small Python utility for reordering multi-slice cardiac cine DICOM series. It scans files in an input folder, groups readable DICOMs by `SeriesInstanceUID`, and assigns sequential `InstanceNumber` values to series that have multiple slice locations and multiple trigger times.

> **Important:** This tool changes DICOM metadata and copies files into an output folder. Validate its output with your imaging workflow before relying on it. Keep the original data unchanged and use a separate output folder.

## What it does

- Reads files directly inside the selected input folder (it does not recursively scan subfolders).
- Groups readable files by DICOM `SeriesInstanceUID`.
- Detects a multi-slice cine series when it can read more than one `SliceLocation` and more than one `TriggerTime` among the series' files.
- Sorts detected cine files by `SliceLocation`, then `TriggerTime`, and saves them with `InstanceNumber` values starting at 1.
- Copies other readable DICOM files to the output folder without changing their contents.
- Skips files that cannot be read as DICOM, without reporting each skipped file.

The sort is ascending for both values. Files with identical slice and trigger-time values have no explicit tie-breaker. The script preserves each source filename. Use an output folder that does not contain source files with colliding names, and avoid using the same folder for input and output.

## Requirements

### Basic system requirements

- Windows, macOS, or Linux with a supported Python 3 installation (Python 3.9 or newer is a reasonable starting point; the script has not been tested across platforms).
- Enough free disk space in the output location for a copy of the readable input DICOM files.
- Read access to the input folder and write access to the output folder.
- DICOM data with the tags needed for cine detection and sorting: `SeriesInstanceUID`, `SliceLocation`, and `TriggerTime`.

There are no specific CPU or GPU requirements. Runtime and storage needs depend on the number and size of the DICOM files.

### Python dependency

- [`pydicom`](https://pydicom.github.io/)

## Install and run

1. Install Python 3 if it is not already available.
2. Open a terminal in this repository and install the dependency:

   ```bash
   python -m pip install pydicom
   ```

3. Run the script:

   ```bash
   python MuSCiRe.py
   ```

4. Enter the input folder path, then the output folder path when prompted.

On some systems, the Python command may be `python3` instead of `python`.

## Example

```text
Input folder: /data/dicom_input
Output folder: /data/dicom_reordered
Reordered: Short Axis Cine
Done.
Output folder: /data/dicom_reordered
```

The example output is illustrative; the reported series description depends on the data.

## Turn it into a desktop GUI app

The current program is a command-line script, not a GUI. A straightforward way to add a native desktop interface is Python's built-in `tkinter` library:

1. Move the processing logic into a function such as `reorder(input_folder, output_folder)` so it can be called without interactive `input()` prompts.
2. Build a small `tkinter` window with input and output folder pickers, a **Start** button, progress/status text, and a completion or error message.
3. Run the DICOM scan in a background thread so the window remains responsive. Send progress updates back to the UI thread safely.
4. Validate that the input exists, the output is writable, and input and output do not resolve to the same folder. Report skipped or failed files instead of silently hiding all errors.
5. Package the application for each target operating system with [PyInstaller](https://pyinstaller.org/), for example:

   ```bash
   python -m pip install pyinstaller
   pyinstaller --onefile --windowed --name CineReorder gui.py
   ```

   `gui.py` here represents the future GUI entry point. Build and test a separate package on each operating system you intend to support; PyInstaller does not generally cross-compile desktop bundles between operating systems. Verify that the packaged application includes `pydicom` and any platform-specific Tcl/Tk runtime it needs.

Before distributing the GUI, add clear validation and error reporting, a progress indicator, and tests using representative DICOM data. The current script uses broad exception handling and does not recursively scan directories, prevent input/output overlap, or resolve filename collisions.

## Limitations and data handling

- Only files at the top level of the input directory are considered.
- A file is treated as part of a series only if it can be read and has `SeriesInstanceUID`.
- The cine check requires every file in a series to expose usable `SliceLocation` and `TriggerTime` values; if a value is missing or invalid, that series is copied without reordering.
- The script copies files rather than deleting or modifying the originals. Reordered series are written by `pydicom`; other readable files are copied as-is.
- Output filenames are the original basenames. If different inputs share a basename, they can overwrite each other in the output directory.
- Unreadable files are silently ignored, so the script's `Done.` message does not guarantee every input file was processed.
- Review DICOM metadata and ordering in the destination viewer or downstream pipeline. This utility is not a substitute for clinical validation.

## Repository contents

```text
.
├── README.md
└── MuSCiRe.py
```

## License

No license is currently provided in this repository. Add a license file before redistributing the code.
