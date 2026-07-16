#!/usr/bin/env python3
"""
Convert a markdown daily run file to a styled PDF.
Usage: python3 md_to_pdf.py <input.md> <output.pdf>
"""
import sys
import os
import markdown
from weasyprint import HTML

CSS = """
@page {
    size: A4;
    margin: 2cm 1.5cm 2cm 1.5cm;
    @bottom-center {
        content: "Raymond Daily Run — Page " counter(page) " of " counter(pages);
        font-size: 8pt;
        color: #888;
    }
}

body {
    font-family: 'Helvetica Neue', 'Arial', 'Noto Sans', sans-serif;
    font-size: 9pt;
    line-height: 1.5;
    color: #1a1a1a;
    max-width: 100%;
}

h1 {
    font-size: 16pt;
    color: #0d3b14;
    border-bottom: 3px solid #0d3b14;
    padding-bottom: 6px;
    margin-top: 0;
    margin-bottom: 12px;
}

h2 {
    font-size: 12pt;
    color: #1a4d1a;
    border-bottom: 1px solid #b0c4b0;
    padding-bottom: 3px;
    margin-top: 18px;
    margin-bottom: 8px;
    page-break-after: avoid;
}

h3 {
    font-size: 10.5pt;
    color: #2d5a2d;
    margin-top: 12px;
    margin-bottom: 6px;
    page-break-after: avoid;
}

p {
    margin: 4px 0 6px 0;
}

strong {
    color: #0a2e0a;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 8px 0 12px 0;
    font-size: 7.8pt;
    page-break-inside: auto;
}

th {
    background-color: #0d3b14;
    color: white;
    padding: 5px 6px;
    text-align: left;
    border: 1px solid #0d3b14;
    font-weight: bold;
}

td {
    padding: 4px 6px;
    border: 1px solid #c8d8c8;
    vertical-align: top;
}

tr:nth-child(even) {
    background-color: #f4f8f4;
}

tr {
    page-break-inside: avoid;
}

code {
    font-family: 'Courier New', 'DejaVu Sans Mono', monospace;
    font-size: 8pt;
    background-color: #f0f0f0;
    padding: 1px 3px;
    border-radius: 2px;
}

pre {
    background-color: #f5f5f5;
    border: 1px solid #d0d0d0;
    padding: 8px;
    border-radius: 3px;
    font-size: 8pt;
    overflow-x: auto;
    white-space: pre-wrap;
    word-wrap: break-word;
    page-break-inside: avoid;
}

hr {
    border: none;
    border-top: 1px solid #ccc;
    margin: 12px 0;
}

/* Prevent section headers from being orphaned */
h2, h3 {
    page-break-after: avoid;
}
"""

def md_to_pdf(input_md, output_pdf):
    with open(input_md, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Convert markdown to HTML with extensions
    html_body = markdown.markdown(
        md_text,
        extensions=['tables', 'fenced_code', 'codehilite', 'toc', 'sane_lists']
    )

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <style>{CSS}</style>
</head>
<body>
{html_body}
</body>
</html>"""

    HTML(string=full_html).write_pdf(output_pdf)
    print(f"PDF written: {output_pdf}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 md_to_pdf.py <input.md> <output.pdf>")
        sys.exit(1)
    md_to_pdf(sys.argv[1], sys.argv[2])