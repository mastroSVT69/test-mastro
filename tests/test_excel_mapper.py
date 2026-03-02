"""Basic tests for excel_mapper."""

import sys, os
# ensure src is on path for tests
# add workspace root so that `import src` works
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src import excel_mapper
from tools import convert_csv_to_xlsx


def test_load_mapping(tmp_path):
    # write a small CSV and convert it to XLSX via the helper tool
    csv_file = tmp_path / "mapping.csv"
    with open(csv_file, 'w', encoding='utf-8') as f:
        f.write("path,level,permissions\n")
        f.write("C:/dossier1,1,rwx\n")
    xlsx_file = tmp_path / "mapping.xlsx"
    convert_csv_to_xlsx(str(csv_file), str(xlsx_file))

    loaded = excel_mapper.load_mapping(str(xlsx_file))
    assert isinstance(loaded, list)
    assert loaded[0]["path"] == "C:/dossier1"
