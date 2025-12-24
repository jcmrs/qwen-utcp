import json
from pathlib import Path
import glob

# Check a single extraction to see what's inside
extraction_file = Path('.utcp-kb/raw-extractions/python-utcp/extraction_*.json')
files = glob.glob(str(extraction_file))
if files:
    with open(files[0], 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f'Repository: {data["repository"]}')
    print(f'File count in extraction: {data["file_count"]}')
    print(f'Number of extractions: {len(data["extractions"])}')
    if data['extractions']:
        print(f'First extraction keys: {list(data["extractions"][0].keys())}')
        print(f'First file path: {data["extractions"][0].get("file_path", "N/A")}')
        print(f'Has content: {"content" in data["extractions"][0]}')
        if 'content' in data['extractions'][0]:
            print(f'Content length: {len(data["extractions"][0]["content"])}')
            content_preview = data["extractions"][0]["content"][:100] if len(data["extractions"][0]["content"]) > 100 else data["extractions"][0]["content"]
            print(f'Sample content: {content_preview}...')
else:
    print('No extraction files found')