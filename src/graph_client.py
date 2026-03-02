"""Client for Microsoft Graph API.

This module handles interactions with Microsoft Graph to fetch Teams,
channels, and other collaboration data. It requires a valid access token
from Azure AD authentication.
"""

import requests
from typing import List, Dict, Optional


class GraphClient:
    """Wrapper around Microsoft Graph API calls."""

    def __init__(self, access_token: str):
        """Initialize with an access token from Azure AD.
        
        Args:
            access_token: Bearer token from Azure AD auth flow
        """
        self.access_token = access_token
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    def get_teams(self) -> List[Dict]:
        """Fetch list of teams the user is a member of.
        
        Returns:
            List of team objects with id, displayName, description
        """
        try:
            resp = requests.get(
                f"{self.base_url}/me/joinedTeams",
                headers=self.headers,
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()
            teams = []
            for item in data.get("value", []):
                teams.append({
                    "id": item.get("id"),
                    "displayName": item.get("displayName"),
                    "description": item.get("description", "")
                })
            return teams
        except Exception as e:
            print(f"Error fetching teams: {e}")
            return []

    def get_channels(self, team_id: str) -> List[Dict]:
        """Fetch channels in a team.
        
        Args:
            team_id: Microsoft Teams team ID
            
        Returns:
            List of channel objects with id, displayName
        """
        try:
            resp = requests.get(
                f"{self.base_url}/teams/{team_id}/channels",
                headers=self.headers,
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()
            channels = []
            for item in data.get("value", []):
                channels.append({
                    "id": item.get("id"),
                    "displayName": item.get("displayName")
                })
            return channels
        except Exception as e:
            print(f"Error fetching channels for team {team_id}: {e}")
            return []

    def create_channel(self, team_id: str, channel_name: str, description: str = "") -> Optional[Dict]:
        """Create a new channel in a team.
        
        Args:
            team_id: Microsoft Teams team ID
            channel_name: Name of the channel
            description: Optional description
            
        Returns:
            Channel object if successful, None otherwise
        """
        try:
            payload = {
                "displayName": channel_name,
                "description": description
            }
            resp = requests.post(
                f"{self.base_url}/teams/{team_id}/channels",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"Error creating channel: {e}")
            return None
