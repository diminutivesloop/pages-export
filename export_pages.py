#!/usr/bin/env python3
"""Export a Pages document to PDF and DOCX using Apple Pages via AppleScript.

Usage:
  python3 export_pages.py /path/to/file.pages [--out-dir /some/dir]

Requires macOS with the Pages app installed.
"""
import argparse
import os
import subprocess
import sys


def run_applescript(script: str) -> str:
    proc = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if proc.returncode != 0:
        msg = proc.stderr.strip() or proc.stdout.strip()
        raise RuntimeError(f"AppleScript failed: {msg}")
    return proc.stdout.strip()


def posix_escaped(path: str) -> str:
    return path.replace('"', '\\"')


def export_pages(pages_path: str, pdf_path: str, docx_path: str, formats: list) -> None:
    path = posix_escaped(os.path.abspath(pages_path))
    out_pdf = posix_escaped(os.path.abspath(pdf_path)) if pdf_path else None
    out_docx = posix_escaped(os.path.abspath(docx_path)) if docx_path else None

    name = os.path.basename(pages_path)
    try:
        docs_list = run_applescript('tell application "Pages" to get name of every document')
    except RuntimeError:
        docs_list = ""

    already_open = name in docs_list

    # Build export commands based on requested formats
    export_cmds = []
    if 'pdf' in formats and out_pdf:
        export_cmds.append(f'        export to POSIX file "{out_pdf}" as PDF')
    if 'docx' in formats and out_docx:
        export_cmds.append(f'        export to POSIX file "{out_docx}" as Microsoft Word')

    exports = '\n'.join(export_cmds)

    if already_open:
        applescript = f'''
tell application "Pages"
    set theDoc to document "{name}"
    delay 0.2
    tell theDoc
{exports}
    end tell
end tell
'''
    else:
        applescript = f'''
tell application "Pages"
    set theDoc to open POSIX file "{path}"
    delay 0.2
    tell theDoc
{exports}
    end tell
    close theDoc saving no
end tell
'''

    run_applescript(applescript)


def main():
    parser = argparse.ArgumentParser(description="Export a .pages file to PDF and DOCX using Pages.app")
    parser.add_argument("pages_file", nargs='?', default=None, help="Path to the .pages file (optional). If omitted the most recently modified .pages file in --search-dir is used.")
    parser.add_argument("--output", "-o", default=None, help="Output path: either a directory or a file path (with or without extension). If a directory is given, the input filename base is used.")
    parser.add_argument("--search-dir", "-d", default='.', help="Directory to search for the most-recent .pages file when no pages_file is provided (default: current directory)")
    parser.add_argument("--formats", "-f", nargs='*', default=['pdf', 'docx'], choices=['pdf', 'docx'], help="Export formats: pdf and/or docx (default: both)")
    args = parser.parse_args()

    if not sys.platform.startswith("darwin"):
        print("This script only runs on macOS.")
        sys.exit(2)

    pages_file = args.pages_file
    if pages_file is None:
        # find most recently modified .pages in search-dir (non-recursive)
        search_dir = os.path.abspath(args.search_dir)
        try:
            candidates = [os.path.join(search_dir, name) for name in os.listdir(search_dir) if name.endswith('.pages')]
        except FileNotFoundError:
            candidates = []

        if not candidates:
            print(f"No .pages files found in {search_dir}")
            sys.exit(2)

        # choose most recently modified
        pages_file = max(candidates, key=lambda p: os.path.getmtime(p))
        print(f"Auto-selected pages file: {pages_file}")

    if not os.path.exists(pages_file):
        print(f"Input file not found: {pages_file}")
        sys.exit(2)

    orig_base = os.path.splitext(os.path.basename(pages_file))[0]
    if args.output:
        out_path = args.output
        if os.path.isdir(out_path) or out_path.endswith(os.sep):
            out_dir = os.path.abspath(out_path)
            base = orig_base
        else:
            out_dir = os.path.dirname(os.path.abspath(out_path)) or os.getcwd()
            base = os.path.splitext(os.path.basename(out_path))[0]
    else:
        out_dir = os.path.dirname(os.path.abspath(pages_file)) or os.getcwd()
        base = orig_base

    os.makedirs(out_dir, exist_ok=True)

    print(f"Formats:", args.formats)
    pdf_path = os.path.join(out_dir, base + ".pdf") if 'pdf' in args.formats else None
    docx_path = os.path.join(out_dir, base + ".docx") if 'docx' in args.formats else None

    try:
        export_pages(pages_file, pdf_path, docx_path, args.formats)
    except Exception as e:
        print(f"Export failed: {e}")
        sys.exit(1)

    output_lines = ["Exported:"]
    if pdf_path:
        output_lines.append(f"  PDF: {pdf_path}")
    if docx_path:
        output_lines.append(f"  DOCX: {docx_path}")
    print("\n".join(output_lines))


if __name__ == '__main__':
    main()
