from flask import Flask, redirect, request, session, url_for, jsonify
import requests
from authlib.integrations.flask_client import OAuth  # noqa: F401 - Suppress linter error for import
import os
import sys
import threading
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
import webbrowser
from typing import Any, TYPE_CHECKING, cast, Optional
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Using fallback token file method.")

# GitHub OAuth credentials from environment variables
CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
OAUTH_REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI", "http://127.0.0.1:5000/callback")

# --- GitHub SDK import with graceful fallback for type checkers ---
try:
    from github import Github as _Github  # type: ignore
    from github import Auth as _Auth  # type: ignore
except ImportError:  # pragma: no cover
    class _FallbackGithub:  # minimal runtime stub
        def __init__(self, *args, **kwargs):
            pass
        class _User:  # noqa: D401
            login: str = "stub-user"
        def get_user(self):
            return self._User()
    class _FallbackAuth:  # minimal stub
        class Token:  # pylint: disable=too-few-public-methods
            def __init__(self, token: str):
                self.token = token
    _Github = _FallbackGithub  # type: ignore
    _Auth = _FallbackAuth  # type: ignore

Github = _Github  # type: ignore
Auth = _Auth  # type: ignore

# Global variables
github: Any | None = None
app: Any | None = None

def init_flask_app():
    global app
    app = Flask(__name__)
    # The secret key is still loaded from an environment variable for security.
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev_key_change_in_production")

    oauth = OAuth(app)  # noqa: E1101 - Suppress linter error for OAuth initialization
    github = oauth.register(
        name="github",
        # WARNING: Hardcoding secrets is a major security risk.
        # GitHub will likely find and revoke this secret if the repo is public.
        client_id="217973d6a6bd9d3defb9",
        client_secret="861b796155a2e5a53ab17e68890e70bbeebadae6",
        access_token_url="https://github.com/login/oauth/access_token",
        access_token_params=None,
        authorize_url="https://github.com/login/oauth/authorize",
        authorize_params=None,
        api_base_url="https://api.github.com/",
        client_kwargs={"scope": "user:email"},
    )  # type: ignore[attr-defined]

    @app.route("/")
    def index():
        # Check if the username is saved in the session
        username = session.get("username")
        if username:
            # Get the names of all projects
            projects = get_projects()
            
            # Save the projects to a local file
            save_projects(projects)

            # Display the username and project names
            return f"Hello {username}! You're now logged in. Projects: {', '.join(projects)}"
        else:
            # Username is not saved, redirect to the login page
            return redirect(url_for("login"))

    @app.route('/login')
    def login():
        # Check if the user is already authenticated
        if "access_token" in session:
            # User is already authenticated, redirect to the index page
            return redirect(url_for("index"))

        # User is not authenticated, start the OAuth process
        # The callback URL must exactly match the one in your GitHub OAuth App settings.
        # For this hardcoded setup, it should be: http://127.0.0.1:5000/callback
        # noqa: E1101 - Suppress linter error for authorize_redirect
        return cast(Any, github).authorize_redirect(url_for("callback", _external=True))

    @app.route('/callback')
    def callback():
        code = request.args.get('code')
        if not code:
            return jsonify({"error": "No code provided"}), 400

        # Exchange code for token
        token_response = requests.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": code,
                "redirect_uri": OAUTH_REDIRECT_URI
            },
            headers={"Accept": "application/json"}
        )

        token_data = token_response.json()
        access_token = token_data.get("access_token")
        if not access_token:
            return jsonify({"error": "Failed to get access token", "details": token_data.get("error_description", "Unknown error")}), 400

        # Save the token to a file for auto-login
        try:
            with open("github_token.txt", "w") as f:
                f.write(access_token)
        except Exception as e:
            print(f"Failed to save token: {e}")

        # Initialize GitHub client with the new token
        global github
        github = Github(auth=Auth.Token(access_token))

        # Get the username from the GitHub API
        username = get_username()

        # Save the username in the session
        session["username"] = username

        # Save user information to the about.txt file
        save_user_info(username)

        return "Authentication successful! You can close this window and return to the application."

    # Auto-login on every request
    app.before_request(auto_login)

    return app

# Function to start Flask server in a separate thread
def start_flask_server():
    if app is None:
        init_flask_app()
    threading.Thread(target=lambda: cast(Any, app).run(port=5000, use_reloader=False), daemon=True).start()

# Function to attempt auto-login with saved token
def attempt_auto_login():
    global github
    try:
        if os.path.exists("github_token.txt"):
            with open("github_token.txt", "r") as f:
                access_token = f.read().strip()
                if access_token:
                    github = Github(auth=Auth.Token(access_token))
                    # Verify the token is valid by trying to get user info
                    cast(Any, github).get_user().login
                    print("Auto-login successful.")
                    return True
    except Exception as e:
        print(f"Auto-login failed: {e}")
        github = None
    return False

# Function to trigger OAuth flow if auto-login fails
def login_to_github():
    if attempt_auto_login():
        return github
    
    start_flask_server()
    webbrowser.open("http://127.0.0.1:5000/login")
    print("Opened browser for GitHub login. Complete the authentication and the app will connect.")
    return None  # The callback will set the global github object

def get_access_token(code):
    # Configure the access token request
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
    }

    headers = {
        "Accept": "application/json",
    }

    # Send the access token request
    response = requests.post(
        "https://github.com/login/oauth/access_token", json=payload, headers=headers
    )

    # Extract the access token from the response
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        return access_token

    # Return None in case of an error
    return None

def get_username():
    access_token = session.get("access_token")

    if access_token:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        response = requests.get("https://api.github.com/user", headers=headers)

        if response.status_code == 200:
            username = response.json()["login"]
            return username
    return None

def get_projects():
    access_token = session.get("access_token")

    if access_token:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        response = requests.get("https://api.github.com/user/repos", headers=headers)

        if response.status_code == 200:
            projects = [project["name"] for project in response.json()]
            return projects
    return []

def save_projects(projects):
    with open("projects.txt", "w") as file:
        file.write("\n".join(projects))

def save_user_info(username):
    access_token = session.get("access_token")

    if access_token:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        response = requests.get("https://api.github.com/user", headers=headers)

        if response.status_code == 200:
            user_info = response.json()
            with open("about.txt", "w") as file:
                file.write(f"Username: {username}\n")
                file.write(f"Name: {user_info.get('name')}\n")
                file.write(f"Email: {user_info.get('email')}\n")
                # Write other contact information as desired

# Überprüfen und Erstellen der Datei, falls nicht vorhanden
if not os.path.exists("projects.txt"):
    with open("projects.txt", "w"):
        pass

if not os.path.exists("about.txt"):
    with open("about.txt", "w"):
        pass

TOKEN_FILE = "github_token.txt"

def load_stored_token():
    """Return the stored access token if it exists, else None."""
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                token = f.read().strip()
                return token or None
        except (IOError, OSError):
            return None
    return None

def save_token(token: str):
    """Persist the GitHub access token for future automatic logins."""
    try:
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write(token)
    except (IOError, OSError):
        # Failing to save the token should not break the app
        pass

def validate_token(token: str) -> bool:
    """Check if the provided token is still valid by querying the GitHub API."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    try:
        response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False

def get_username_from_token(token: str):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    response = requests.get("https://api.github.com/user", headers=headers)
    if response.status_code == 200:
        return response.json().get("login")
    return None

def auto_login():
    """Automatically log the user in via stored token if session is empty."""
    if "access_token" not in session:
        token = load_stored_token()
        if token and validate_token(token):
            session["access_token"] = token
            username = get_username_from_token(token)
            if username:
                session["username"] = username

if __name__ == "__main__":
    app_thread = threading.Thread(target=cast(Any, app).run, kwargs={"host": "localhost", "port": 5000})
    app_thread.daemon = True
    app_thread.start()
    window = TextEditor()
    window.show()
    app_pyqt = QApplication(sys.argv)
    sys.exit(app_pyqt.exec())