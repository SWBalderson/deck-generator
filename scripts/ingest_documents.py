#!/usr/bin/env python3
"""
Ingest multiple document formats using Docling and pandas.
Supports: PDF, DOCX, PPTX, XLSX, CSV, JSON, MD, TXT, HTML
"""

import argparse
import json
import sys
from pathlib import Path


def ingest_file(file_path: Path, converter=None) -> dict:
    """Ingest a single file and return structured content."""
    from docling.document_converter import DocumentConverter
    import pandas as pd

    if converter is None:
        converter = DocumentConverter()
    suffix = file_path.suffix.lower()
    
    try:
        if suffix in ['.pdf', '.docx', '.pptx', '.html', '.xlsx']:
            doc = converter.convert(str(file_path)).document
            return {
                'filename': file_path.name,
                'type': suffix.lstrip('.'),
                'markdown': doc.export_to_markdown(),
                'text': doc.export_to_text(),
                'metadata': str(doc.metadata),
                'tables': []  # Extract tables if needed
            }
        
        elif suffix == '.csv':
            df = pd.read_csv(file_path)
            return {
                'filename': file_path.name,
                'type': 'csv',
                'data': df.to_dict('records'),
                'columns': df.columns.tolist(),
                'markdown': df.head(20).to_markdown(),
                'summary': {
                    'rows': len(df),
                    'columns': len(df.columns),
                    'numeric_columns': df.select_dtypes(include=['number']).columns.tolist()
                }
            }
        
        elif suffix == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return {
                'filename': file_path.name,
                'type': 'json',
                'data': data
            }
        
        elif suffix in ['.md', '.txt']:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {
                'filename': file_path.name,
                'type': suffix.lstrip('.'),
                'content': content,
                'length': len(content)
            }
        
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
    
    except Exception as e:
        raise RuntimeError(f"Error ingesting {file_path}: {e}") from e


def ingest_and_save(files: list, output: str) -> int:
    """Ingest files and write content.json. Callable from pipeline or CLI."""
    from docling.document_converter import DocumentConverter
    converter = DocumentConverter()

    contents = {}
    errors = []

    for file_path in files:
        path = Path(file_path)
        if not path.exists():
            errors.append(f"File not found: {file_path}")
            continue

        try:
            contents[file_path] = ingest_file(path, converter=converter)
            print(f"✓ Ingested: {file_path}")
        except Exception as e:
            msg = f"✗ Failed: {file_path} - {e}"
            print(msg, file=sys.stderr)
            raise RuntimeError(msg) from e

    output_dir = Path(output).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output, 'w', encoding='utf-8') as f:
        json.dump({
            'contents': contents,
            'errors': errors,
            'total_files': len(files),
            'successful': len(contents),
            'failed': len(errors)
        }, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved to: {output}")
    print(f"  Total: {len(files)} | Success: {len(contents)} | Failed: {len(errors)}")
    return 0 if not errors else 1


def main():
    parser = argparse.ArgumentParser(description='Ingest documents for presentation')
    parser.add_argument('--files', nargs='+', required=True, help='List of files to ingest')
    parser.add_argument('--output', required=True, help='Output JSON file path')
    args = parser.parse_args()
    return ingest_and_save(args.files, args.output)


if __name__ == '__main__':
    sys.exit(main())
