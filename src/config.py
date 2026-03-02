"""Configuration for Azure AD authentication.

To enable authentication:
1. Create an App Registration in Azure AD
2. Set these values from your app registration portal
3. Set environment variables or update this file

See: https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app
"""

import os

# Azure AD configuration
# If you create a single-tenant app registration (most common for internal
# enterprise scenarios) you cannot use the "/common" authority endpoint; you
# must either specify your tenant ID or make the application multi-tenant in
# Azure.  The environment variables below give you both options.

# client ID for the Azure AD app (required).
DEFAULT_CLIENT_ID = "1e128539-1ae4-4592-8669-41718212dca1"  # demo/test value
client_id = os.getenv("AZURE_CLIENT_ID", DEFAULT_CLIENT_ID)

# a specific Azure AD tenant (GUID or "contoso.onmicrosoft.com").  If set we
# construct a tenant-specific authority URL.  Otherwise we fall back to
# AZURE_AUTHORITY or "/common" which only works for multi-tenant apps.
tenant_id = os.getenv("AZURE_TENANT_ID")
if tenant_id:
    authority = f"https://login.microsoftonline.com/{tenant_id}"
else:
    authority = os.getenv("AZURE_AUTHORITY", "https://login.microsoftonline.com/common")

AZURE_AD_CONFIG = {
    "client_id": client_id,
    "authority": authority,
    "scopes": ["user.read", "team.read.all", "channel.read.all"],
}

# For production, consider using Azure Key Vault or a secure secrets manager
# to store sensitive credentials instead of env vars or hardcoded values.

# For production, consider using Azure Key Vault or a secure secrets manager
# to store sensitive credentials instead of env vars or hardcoded values.
