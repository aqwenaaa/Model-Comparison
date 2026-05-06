import json
from pathlib import Path

source_path = Path(r"d:\DOWNLOAD\mcdm_analysis_complete.py")
output_path = Path(r"d:\SEMESTER 6\PBL\Model-Comparison\MCDM_Analysis.ipynb")

text = source_path.read_text(encoding='utf-8')

cells = []
current_lines = []
current_cell_type = 'code'

for line in text.splitlines(keepends=True):
    if line.startswith('# %%'):
        if current_lines:
            cells.append({
                'cell_type': current_cell_type,
                'metadata': {},
                'source': current_lines,
                'outputs': [] if current_cell_type == 'code' else None,
                'execution_count': None if current_cell_type == 'code' else None,
            })
        current_lines = []
        current_cell_type = 'code'
        continue
    current_lines.append(line)

if current_lines:
    cells.append({
        'cell_type': current_cell_type,
        'metadata': {},
        'source': current_lines,
        'outputs': [] if current_cell_type == 'code' else None,
        'execution_count': None if current_cell_type == 'code' else None,
    })

# Prepend a title markdown cell
markdown_cell = {
    'cell_type': 'markdown',
    'metadata': {},
    'source': [
        '# MCDM Analysis for AXA Insurance\n',
        'Converted from `mcdm_analysis_complete.py` into a Jupyter notebook.\n',
        'This notebook preserves the original script structure with separate analysis cells.\n'
    ]
}

notebook = {
    'cells': [markdown_cell] + cells,
    'metadata': {
        'kernelspec': {
            'display_name': 'Python 3',
            'language': 'python',
            'name': 'python3'
        },
        'language_info': {
            'name': 'python',
            'version': '3.14.3'
        }
    },
    'nbformat': 4,
    'nbformat_minor': 5
}

output_path.write_text(json.dumps(notebook, indent=1), encoding='utf-8')
print(f'Notebook saved to: {output_path}')
