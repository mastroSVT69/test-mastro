"""A simple Flask web application for the migration tool."""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from src import excel_mapper, teams_migrator
from src.graph_client import GraphClient
from src.config import AZURE_AD_CONFIG

app = Flask(__name__)
app.secret_key = "dev-key"  # should be replaced by a real secret in production


@app.route('/')
def index():
    # landing page with upload and team/channel selection
    teams = teams_migrator.list_teams()
    return render_template(
        "index.html",
        teams=teams,
        client_id=AZURE_AD_CONFIG.get("client_id"),
        authority=AZURE_AD_CONFIG.get("authority"),
    )


@app.route('/api/teams')
def api_teams():
    """Get teams for authenticated user via Graph API.
    
    Expects token in Authorization header or query param.
    """
    token = None
    
    # try to get token from Authorization header
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]
    
    # fallback: check query params
    if not token:
        token = request.args.get('token')
    
    if not token:
        return jsonify({"error": "No token provided"}), 401
    
    try:
        client = GraphClient(token)
        teams = client.get_teams()
        return jsonify({
            "value": [
                {"id": t["id"], "displayName": t["displayName"]}
                for t in teams
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/channels')
def channels():
    """Get channels for a team.
    
    If a token is provided, fetch real channels from Graph API.
    Otherwise, return dummy channels.
    """
    team_id = request.args.get('team_id')
    token = request.args.get('token')
    
    if not team_id:
        return jsonify([]), 400
    
    if token:
        # real Graph API call
        try:
            client = GraphClient(token)
            channels_data = client.get_channels(team_id)
            return jsonify([c["displayName"] for c in channels_data])
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    else:
        # fallback to dummy data
        ch = teams_migrator.list_channels(team_id)
        return jsonify(ch)


@app.route('/advice', methods=['GET'])
def advice():
    # simple advice endpoint based on query params
    try:
        count = int(request.args.get('count', 0))
    except Exception:
        count = 0
    try:
        max_level = int(request.args.get('max_level', 0))
    except Exception:
        max_level = 0
    msgs = []
    if count > 100:
        msgs.append("Le fichier contient de nombreux dossiers ; envisagez de migrer par lots.")
    if max_level > 5:
        msgs.append("L'arborescence est profonde (niveau > 5), pensez à la simplifier.")
    return jsonify({"advice": "\n".join(msgs) if msgs else "Aucun conseil."})


@app.route("/upload", methods=["POST"])
def upload():
    if "mapping" not in request.files:
        flash("Aucun fichier sélectionné")
        return redirect(url_for("index"))
    file = request.files["mapping"]
    path = "/tmp/mapping.xlsx"
    file.save(path)
    try:
        rows = excel_mapper.load_mapping(path)
    except Exception as e:
        flash(f"Erreur lors de la lecture : {e}")
        rows = []
    teams = teams_migrator.list_teams()
    advice_text = teams_migrator.get_advice(rows)
    flash(f"Fichier chargé: {len(rows)} entrées")
    return render_template(
        "index.html",
        teams=teams,
        rows=rows,
        advice=advice_text,
        client_id=AZURE_AD_CONFIG.get("client_id"),
        authority=AZURE_AD_CONFIG.get("authority"),
    )


@app.route('/upload_from_sharepoint', methods=['POST'])
def upload_from_sharepoint():
    """Accept JSON containing base64‑encoded file content from a SharePoint picker.

    The expected payload is:
        {"filename":"mapping.xlsx","content_base64":"..."}
    """
    data = request.get_json(force=True, silent=True)
    if not data or 'content_base64' not in data:
        return 'Invalid payload', 400

    try:
        import base64
        content = base64.b64decode(data['content_base64'])
    except Exception as e:
        return f'Bad base64 data: {e}', 400

    path = '/tmp/mapping.xlsx'
    with open(path, 'wb') as f:
        f.write(content)

    try:
        rows = excel_mapper.load_mapping(path)
    except Exception as e:
        flash(f'Erreur lors de la lecture : {e}')
        rows = []

    teams = teams_migrator.list_teams()
    advice_text = teams_migrator.get_advice(rows)
    flash(f"Fichier chargé: {len(rows)} entrées")
    return render_template(
        "index.html",
        teams=teams,
        rows=rows,
        advice=advice_text,
        client_id=AZURE_AD_CONFIG.get("client_id"),
        authority=AZURE_AD_CONFIG.get("authority"),
    )



if __name__ == "__main__":
    # bind to 0.0.0.0 so the app is reachable from the host/container
    app.run(debug=True, host="0.0.0.0")
