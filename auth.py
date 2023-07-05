from flask import Flask, redirect, request, session, url_for
import requests
from authlib.integrations.flask_client import OAuth
import os
import sys
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt



app = Flask(__name__)
app.secret_key = "some_random_string"  # Replace with your secret key

oauth = OAuth(app)
github = oauth.register(
    name="github",
    client_id="217973d6a6bd9d3defb9",
    client_secret="861b796155a2e5a53ab17e68890e70bbeebadae6",
    access_token_url="https://github.com/login/oauth/access_token",
    access_token_params=None,
    authorize_url="https://github.com/login/oauth/authorize",
    authorize_params=None,
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "user:email"},
)

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
    return github.authorize_redirect(url_for("callback", _external=True))


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
        "client_id": "217973d6a6bd9d3defb9",
        "client_secret": "861b796155a2e5a53ab17e68890e70bbeebadae6",
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

if __name__ == "__main__":
    app_thread = threading.Thread(target=app.run, kwargs={"host": "localhost", "port": 5000})
    app_thread.daemon = True
    app_thread.start()
    window = TextEditor()
    window.show()
    app_pyqt = QApplication(sys.argv)
    sys.exit(app_pyqt.exec_())
