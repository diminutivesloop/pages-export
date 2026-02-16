# Pages export helper

Small script to export a macOS Pages document (`.pages`) to PDF and DOCX using Pages.app via AppleScript.

🤖 Built w/ substantial help from GitHub Copilot

## Requirements
- macOS with Pages.app installed
- Python 3

## Usage

Run with an explicit file:

```bash
python3 export_pages.py /path/to/document.pages
```
## Options
- `pages_file` (positional, optional): path to a `.pages` file. If omitted, the script searches `--search-dir` for the most-recent `.pages` file (non-recursive) and uses that.
- `-o, --output`: output directory or file base for exports.
- `-d, --search-dir`: directory to search when `pages_file` is omitted (default: current directory).
- `-f, --formats`: export formats (pdf and/or docx). Default: `pdf docx` (both).

## Examples

```bash
# Use input name, write into ./exports
python3 export_pages.py /full/path/to/resume.pages -o ./exports

# Specify output base name (creates ./exports/Resume.pdf and ./exports/Resume.docx)
python3 export_pages.py /full/path/to/resume.pages -o ./exports/Resume

# Omit the pages file: auto-select the most recently modified .pages in the search dir
python3 export_pages.py -o ./exports/AutoResume -d /path/to/dir
# prints: Auto-selected pages file: /path/to/dir/latest.pages

# Export only PDF
python3 export_pages.py /full/path/to/resume.pages -o ./exports/Resume -f pdf

# Export only DOCX
python3 export_pages.py /full/path/to/resume.pages -o ./exports/Resume -f docx

```

## Notes
- The script uses `osascript` to drive Pages.app; Pages will be launched if not already running.
- If a document was already open in Pages, the script will export it but will not close it after exporting; if the script opened the document itself it will close it.
- The script prints the auto-selected path when it chooses a `.pages` file automatically.
- If you want automatic exports on save, use a LaunchAgent, Automator Folder Action, or a file watcher — no modification to this script is required.