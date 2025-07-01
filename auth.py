from flask import Flask, redirect, request, session, url_for
import requests
from authlib.integrations.flask_client import OAuth
import os
import sys
import threading
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev_key_change_in_production")

oauth = OAuth(app)
github = oauth.register(
    name="github",
    client_id=os.getenv("GITHUB_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
    access_token_url="https://github.com/login/oauth/access_token",
    access_token_params=None,
    authorize_url="https://github.com/login/oauth/authorize",
    authorize_params=None,
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "user:email"},
)

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


@app.before_request
def auto_login():
    """Automatically log the user in via stored token if session is empty."""
    if "access_token" not in session:
        token = load_stored_token()
        if token and validate_token(token):
            session["access_token"] = token
            username = get_username_from_token(token)
            if username:
                session["username"] = username


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


@app.route("/login")
def login():
    # Check if the user is already authenticated
    if "access_token" in session:
        # User is already authenticated, redirect to the index page
        return redirect(url_for("index"))

    # User is not authenticated, start the OAuth process
    # GitHub requires the redirect URI here to EXACTLY match the value stored in the OAuth-app settings.
    # Allow overriding via env (OAUTH_REDIRECT_URI); otherwise fall back to flask's external URL.
    redirect_uri = os.getenv("OAUTH_REDIRECT_URI", url_for("callback", _external=True))
    return github.authorize_redirect(redirect_uri)


@app.route("/callback")
def callback():
    # Check if the user is already authenticated
    if "access_token" in session:
        # User is already authenticated, redirect to the index page
        return redirect(url_for("index"))

    # Get the OAuth code from the request
    code = request.args.get("code")

    # Exchange the OAuth code for an access token
    access_token = get_access_token(code)

    # Save the access token in the session
    session["access_token"] = access_token

    # Persist token for future automatic logins
    if access_token:
        save_token(access_token)

    # Get the username from the GitHub API
    username = get_username()

    # Save the username in the session
    session["username"] = username

    # Save user information to the about.txt file
    save_user_info(username)

    # Redirect the user to the index page
    return redirect(url_for("index"))


def get_access_token(code):
    # Configure the access token request
    payload = {
        "client_id": os.getenv("GITHUB_CLIENT_ID"),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
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
        access_token = response.json()["access_token"]
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
                file.write(f"Name: {user_info['name']}\n")
                file.write(f"Email: {user_info['email']}\n")
                # Write other contact information as desired

# Überprüfen und Erstellen der Datei, falls nicht vorhanden
if not os.path.exists("projects.txt"):
    with open("projects.txt", "w"):
        pass

if not os.path.exists("about.txt"):
    with open("about.txt", "w"):
        pass
