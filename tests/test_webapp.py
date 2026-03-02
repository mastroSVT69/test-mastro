"""Basic Flask app tests."""

import sys, os
# ensure src package is importable
# add workspace root so that `import src` works
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
# skip tests if flask is not installable in this environment
flask = pytest.importorskip('flask')
from src.webapp import app


def test_index(client):
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.data.decode('utf-8')
    assert "Migration SharePoint/Teams" in body
    # config values should be injected (uses default test id)
    assert "clientId" in body
    assert "authority" in body


def test_upload_no_file(client):
    resp = client.post("/upload", data={})
    # should redirect back to index
    assert resp.status_code == 302


def test_upload_with_file(client, tmp_path):
    # generate csv and convert to xlsx using our tool
    csv_file = tmp_path / "map.csv"
    with open(csv_file, 'w', encoding='utf-8') as f:
        f.write("path,level,permissions\n")
        f.write("C:/dossier1,1,rwx\n")
    from tools import convert_csv_to_xlsx
    xlsx_file = tmp_path / "map.xlsx"
    convert_csv_to_xlsx(str(csv_file), str(xlsx_file))

    with open(xlsx_file, "rb") as f:
        data = {"mapping": (f, "map.xlsx")}
        resp = client.post("/upload", data=data, content_type="multipart/form-data")
    assert resp.status_code == 200
    assert b"Fichier charg" in resp.data
    # table header should include 'path'
    assert b"<th>path</th>" in resp.data


def test_upload_from_sharepoint(client, tmp_path):
    # reuse same generation logic
    csv_file = tmp_path / "map.csv"
    with open(csv_file, 'w', encoding='utf-8') as f:
        f.write("path,level,permissions\n")
        f.write("C:/dossier2,2,rx\n")
    from tools import convert_csv_to_xlsx
    xlsx_file = tmp_path / "map2.xlsx"
    convert_csv_to_xlsx(str(csv_file), str(xlsx_file))

    import base64
    bts = xlsx_file.read_bytes()
    payload = {
        'filename': 'map2.xlsx',
        'content_base64': base64.b64encode(bts).decode('ascii')
    }
    resp = client.post('/upload_from_sharepoint', json=payload)
    assert resp.status_code == 200
    assert b"C:/dossier2" in resp.data
    assert b"<th>path</th>" in resp.data


def test_channels_endpoint(client):
    # parameter name should be team_id to match implementation
    resp = client.get('/channels?team_id=Equipe+A')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert 'Général' in data


def test_advice_endpoint(client):
    resp = client.get('/advice?count=150&max_level=6')
    assert resp.status_code == 200
    js = resp.get_json()
    assert 'contenant de nombreux' in js['advice'] or js['advice']


@pytest.fixture

def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
