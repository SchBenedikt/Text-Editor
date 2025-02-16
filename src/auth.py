from flask import Flask, redirect, request, session, url_for
import requests
from authlib.integrations.flask_client import OAuth
import os
import sys
import threading
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt



app = Flask(__name__)
app.secret_key = "some_random_string" 

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
    username = session.get("username")
    if username:
        projects = get_projects()
        
        save_projects(projects)

        return f"Hello {username}! You're now logged in. Projects: {', '.join(projects)}"
    else:
        return redirect(url_for("login"))


@app.route("/login")
def login():
    if "access_token" in session:
        return redirect(url_for("index"))

    return github.authorize_redirect(url_for("callback", _external=True))


@app.route("/callback")
def callback():
    if "access_token" in session:
        return redirect(url_for("index"))

    code = request.args.get("code")

    access_token = get_access_token(code)

    session["access_token"] = access_token

    username = get_username()

    session["username"] = username

    save_user_info(username)

    return redirect(url_for("index"))



def get_access_token(code):
    payload = {
        "client_id": "217973d6a6bd9d3defb9",
        "client_secret": "861b796155a2e5a53ab17e68890e70bbeebadae6",
        "code": code,
    }

    headers = {
        "Accept": "application/json",
    }

    response = requests.post(
        "https://github.com/login/oauth/access_token", json=payload, headers=headers
    )

    if response.status_code == 200:
        access_token = response.json()["access_token"]
        return access_token

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
    with open("user-data/projects.txt", "w") as file:
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
            with open("user-data/about.txt", "w") as file:
                file.write(f"Username: {username}\n")
                file.write(f"Name: {user_info['name']}\n")
                file.write(f"Email: {user_info['email']}\n")

if not os.path.exists("user-data/projects.txt"):
    with open("user-data/projects.txt", "w"):
        pass

if not os.path.exists("user-data/about.txt"):
    with open("user-data/about.txt", "w"):
        pass

if __name__ == "__main__":
    app_thread = threading.Thread(target=app.run, kwargs={"host": "localhost", "port": 5000})
    app_thread.daemon = True
    app_thread.start()
    window = TextEditor()
    window.show()
    app_pyqt = QApplication(sys.argv)
    sys.exit(app_pyqt.exec_())
