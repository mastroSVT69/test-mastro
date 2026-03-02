"""Placeholder logic for interacting with Microsoft Teams/SharePoint APIs.

These routines are stubs that should later call Microsoft Graph to enumerate
teams, channels and perform migrations.  For now they return fixed data so the
web frontend can be developed independently.
"""


def list_teams():
    """Return a list of available teams (dummy implementation)."""
    return ["Equipe A", "Equipe B"]


def list_channels(team_name: str):
    """Return a list of channels for a given team (dummy)."""
    # pretend each team has a general and one extra channel
    return ["Général", "Canal 1"]


def create_channel(team_name: str, channel_name: str):
    """Stub for creating a new channel under a team."""
    print(f"Creating channel {channel_name} in team {team_name}")
    return True


def get_advice(rows, team: str | None = None, channel: str | None = None) -> str:
    """Generate simple advice based on the worksheet rows and optional selection.

    The heuristics are trivial:
      * if >100 entries, suggest batch migration
      * if depth >5, warn about deep tree
      * if permissions contain 'everyone', flag wide access
      * if a team/channel was specified, offer contextual comment
    """
    messages = []
    count = len(rows) if rows is not None else 0
    if count > 100:
        messages.append("Le fichier contient de nombreux dossiers ; envisagez de migrer par lots.")
    max_level = 0
    for r in rows or []:
        try:
            lvl = int(r.get("level", 0) or 0)
        except Exception:
            lvl = 0
        max_level = max(max_level, lvl)
        perms = str(r.get("permissions", "")).lower()
        if "everyone" in perms or "tout le monde" in perms:
            messages.append("Certains dossiers ont des droits très larges ; vérifiez les permissions.")
            break
    if max_level > 5:
        messages.append("L'arborescence est profonde (niveau > 5), pensez à la simplifier.")

    if team:
        if channel:
            messages.append(f"Vous avez choisi l'équipe '{team}' et le canal '{channel}'.")
        else:
            messages.append(f"Vous avez choisi l'équipe '{team}', sélectionnez un canal.")
    return "\n".join(messages) if messages else "Aucun conseil particulier."


def migrate_folder(source_path: str, team: str, channel: str):
    """Perform the migration of a single folder (stub)."""
    print(f"Migrating {source_path} to {team}/{channel}")
