Script de conversion CSV -> XLSX

Prérequis:
- Python 3
- installer `openpyxl` si nécessaire:

```bash
python -m pip install openpyxl
```

Exemples d'utilisation:

```bash
# conversion par défaut (fixtures)
python tools/convert_csv_to_xlsx.py

# conversion explicite
python tools/convert_csv_to_xlsx.py src/tests/fixtures/mapping.csv src/tests/fixtures/mapping.xlsx
```

Si tu préfères, tu peux aussi installer `pandas` et utiliser `pandas.read_csv(...).to_excel(...)`.
