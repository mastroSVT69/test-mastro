"""Module to parse Excel files describing folder mappings and permissions.

The implementation uses openpyxl directly so that the project has minimal
dependencies and works even without pandas.
"""

from typing import List, Dict
import zipfile
import xml.etree.ElementTree as ET


def _cell_value(c_elem, ns):
    # `<c>` element may contain `<v>` (value) or `<is><t>` (inline string)
    v = c_elem.find('s:v', ns)
    if v is not None and v.text is not None:
        return v.text
    is_ = c_elem.find('s:is', ns)
    if is_ is not None:
        t = is_.find('s:t', ns)
        return t.text if t is not None else ''
    return ''


def load_mapping(file_path: str) -> List[Dict[str, str]]:
    """Charge un fichier .xlsx et renvoie une liste de dicts.

    Le fichier est lu avec la bibliothèque standard (``zipfile`` + XML)
    afin d'éviter une dépendance externe. Seule la première feuille est
    prise en compte.
    """
    # open zip and read worksheet xml
    with zipfile.ZipFile(file_path) as z:
        try:
            data = z.read('xl/worksheets/sheet1.xml')
        except KeyError:
            raise ValueError('Fichier xlsx invalide : feuille manquante')

    tree = ET.fromstring(data)
    ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

    rows = []
    for row in tree.findall('.//s:row', ns):
        vals = []
        for c in row.findall('s:c', ns):
            vals.append(_cell_value(c, ns))
        rows.append(vals)

    if not rows:
        raise ValueError('Fichier vide')

    header = [str(x).strip().lower() for x in rows[0]]
    expected = ['path', 'level', 'permissions']
    for col in expected:
        if col not in header:
            raise ValueError(f"Colonne attendue manquante: {col}")

    result: List[Dict[str, str]] = []
    for r in rows[1:]:
        if all(v == '' or v is None for v in r):
            continue
        entry = {header[i]: r[i] if i < len(r) else '' for i in range(len(header))}
        result.append(entry)
    return result
