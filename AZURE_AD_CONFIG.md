# Configuration Microsoft 365 / Azure AD

## Objectif

Permettre aux utilisateurs de se connecter avec leur compte Microsoft et de récupérer leurs équipes Teams réelles via Microsoft Graph API.

## Prérequis

1. **App Registration dans Azure AD**
   - Accès au portail Azure (**https://portal.azure.com**)
   - Droits de créer une application

2. **Permissions Microsoft Graph**
   - `Team.Read.All`
   - `User.Read`
   - `Channel.Read.All` (optionnel, selon vos besoins)

## Étapes de configuration

### 1. Créer une App Registration

1. Allez sur **Azure Portal** → **Azure AD** → **App registrations**
2. Cliquez sur **New registration**
3. Remplissez les champs :
   - **Name** : `SharePoint Teams Migration Tool` (ou autre)
   - **Supported account types** : `Accounts in any organizational directory (Any Azure AD directory - Multitenant)`
   - **Redirect URI** : 
     - Type : `Web`
     - URI : `http://localhost:5000/` (pour développement local)
     - En production : `https://<your-domain>/`
4. Cliquez sur **Register**

### 2. Configurer les permissions

1. Allez dans votre app → **API permissions**
2. Cliquez sur **Add a permission**
3. Sélectionnez **Microsoft Graph**
4. Choisissez **Delegated permissions**
5. Recherchez et ajoutez :
   - `Team.Read.All`
   - `User.Read`
   - `Channel.Read.All`
6. Cliquez sur **Grant admin consent**

### 3. Récupérer les credentials

1. Allez dans votre app → **Overview**
2. Notez le **Application (client) ID** — c'est votre `AZURE_CLIENT_ID`

### 4. Configurer l'application

#### Option A : Variables d'environnement (recommandé)

```bash
export AZURE_CLIENT_ID="1e128539-1ae4-4592-8669-41718212dca1"
python -m src.webapp
```
> Note : ce Client ID correspond à l'application "SVTMigratorFiles" que vous avez créée. Vous pouvez le conserver tel quel pour les tests locaux, mais en production il vaudra mieux réutiliser la variable d'environnement plutôt que de laisser la valeur en dur.
#### Option B : Configuration directe

Modifiez `src/config.py` :

```python
AZURE_AD_CONFIG = {
    "client_id": "your-actual-client-id-here",
    "authority": "https://login.microsoftonline.com/common",
    "scopes": ["user.read", "team.read.all", "channel.read.all"],
}
```

### 5. Remplacer le template HTML

Le fichier `src/templates/index.html` doit être mis à jour pour inclure MSAL (Microsoft Authentication Library).

**Option 1 (rapide)** : Utiliser le template fourni avec MSAL intégré

```bash
cp src/templates/index_msal.html src/templates/index.html
```

Puis remplacez `YOUR_CLIENT_ID_HERE` dans le fichier HTML par votre vrai Client ID (ou utilisez une variable d'environnement).

**Option 2 (manuel)** : Ajouter MSAL manuellement au template actuel

Inclure dans le `<head>` :

```html
<script src="https://alcdn.msftauth.net/lib/1.4.17/js/msal.min.js"></script>
```

Et dans le `<body>`, avant les scripts existants, ajouter :

```html
<button onclick="loginWithMS()">Se connecter avec Microsoft</button>
<button onclick="logoutFromMS()" id="logoutBtn" style="display:none;">Déconnexion</button>

<script>
const msalConfig = {
    auth: {
        clientId: "<votre-client-id>",
        authority: "https://login.microsoftonline.com/common",
        redirectUri: window.location.origin + window.location.pathname
    }
};
const msalApp = new Msal.UserAgentApplication(msalConfig);
// ... (voir src/templates/index_msal.html pour l'implémentation complet)
</script>
```

## Points clés du code

### Backend (Flask)

- **`src/graph_client.py`** : Classe `GraphClient` pour appeler Microsoft Graph API
- **`src/webapp.py`** → endpoint `/api/teams` : Récupère les équipes de l'utilisateur via le token d'accès

### Frontend (JavaScript)

- **MSAL.js** : Gère l'authentification Azure AD côté client
- **Token bearer** : Envoyé à l'endpoint `/api/teams` et `/channels?team_id=...&token=...`
- **Dynamique** : Les menus déroulants se remplissent avec les vraies équipes/canaux

## Dépannage

### "No token provided" ou erreur 401

→ L'utilisateur n'est pas connecté ou le token est expiré.  
→ Vérifiez que MSAL a bien obtenu un token.

### "Graph API error: Authorization_RequestDenied"

→ Les permissions ne sont **pas accordées** en admin consent.  
→ Allez sur Azure Portal → votre app → API permissions → **Grant admin consent**

### "Client ID not found"

→ Vous avez mis `YOUR_CLIENT_ID_HERE` dans le template.  
→ Remplacez par votre vrai Client ID d'Azure AD.

### La page dit "mode démo" au lieu de récupérer les vraies équipes

→ Le token ne peut pas être obtenu (erreur réseau, config MSAL invalide).  
→ Vérifiez la console du navigateur (F12 → Console) pour voir les erreurs MSAL.

## Ressources utiles

- [Microsoft Graph Documentation](https://docs.microsoft.com/en-us/graph/overview)
- [MSAL.js Quickstart](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-v2-javascript)
- [Azure AD App Registration Guide](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)

## Prochaines étapes

Une fois l'authentification en place :

1. Tester le login et vérifier que les équipes s'affichent correctement
2. Implémente le bouton "Migrer" pour créer/mettre à jour les canaux
3. Ajouter la logique de migration des dossiers vers Teams
4. Déployer sur un serveur de production (Azure App Service, etc.)

---

Questions ? Consulte les logs Flask et la console du navigateur (F12) pour le debugging.
