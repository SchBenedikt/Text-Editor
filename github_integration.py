import requests
from flask import session
from urllib.parse import quote
from base64 import b64decode
from PyQt6.QtWidgets import QInputDialog, QMessageBox
import webbrowser
import threading
import os

def get_username_from_about_file():
    with open("about.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith("Username:"):
                return line.strip().split(":")[1].strip()
    return None

def start_webserver(app):
    def run_flask_app():
        app.run(host="127.0.0.1", port=5000)

    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()

    # Open web browser to localhost:5000
    url = "http://127.0.0.1:5000"
    webbrowser.open(url)

def open_project(self, project):
    username = get_username_from_about_file()
    if username:
        repo_url = f"https://api.github.com/repos/{username}/{project}/contents"
        try:
            response = requests.get(repo_url)
            response.raise_for_status()  # Check if the request was successful

            files = [file_info["name"] for file_info in response.json()]

            # Display the file names in a QMessageBox
            if files:
                selected_file, ok = QInputDialog.getItem(self, "Select File", "Select a file to open:", files, 0, False)
                if ok and selected_file:
                    # Fetch the content of the selected file
                    file_content_url = f"https://api.github.com/repos/{username}/{project}/contents/{quote(selected_file)}"
                    content_response = requests.get(file_content_url)
                    content_response.raise_for_status()

                    # Decode the base64-encoded content
                    content = b64decode(content_response.json()["content"]).decode("utf-8")

                    current_widget = self.tab_widget.currentWidget()
                    current_widget.setPlainText(content)
                    self.set_tab_title(current_widget, selected_file)
            else:
                QMessageBox.warning(self, "No Files", f"There are no files in {project}.")
        except requests.RequestException as e:
            QMessageBox.warning(self, "Error", f"Error fetching project files: {str(e)}")
    else:
        # Handle the case when username is not available
        pass

def load_projects():
    projects = []
    with open("projects.txt", "r") as file:
        for line in file:
            project = line.strip()
            if project:
                projects.append(project)
    return projects

def get_user_repositories(github_username, access_token):
    api_url = f"https://api.github.com/users/{github_username}/repos"
    headers = {"Authorization": f"token {access_token}"}

    try:
        response = requests.get(api_url, headers=headers)
        repositories = [repo['name'] for repo in response.json()]
        return repositories
    except requests.RequestException as e:
        print(f"Error getting GitHub repositories: {e}")
        return None

def get_user_repository(github_username, access_token):
    repositories = get_user_repositories(github_username, access_token)
    if repositories:
        repository_name, ok = QInputDialog.getItem(None, 'Select Repository', 'Choose a GitHub repository:', repositories, 0, False)
        if ok:
            return repository_name
    return None

def read_upload_data():
    with open('upload_data.txt', 'r') as file:
        lines = file.readlines()
        github_username = lines[0].strip()
        access_token = lines[1].strip()
        return github_username, access_token

def get_sha_from_github(github_filename, github_username, access_token, repo_name):
    api_url = f"https://api.github.com/repos/{github_username}/{repo_name}/contents/{github_filename}"
    headers = {"Authorization": f"token {access_token}"}

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        sha = response.json().get("sha")
        return sha
    else:
        print(f"Unable to get SHA from GitHub. Status code: {response.status_code}, Message: {response.text}")
        return None

def save_to_github(content, github_username, access_token, repo_name):
    # Show a dialog to input the desired file name for GitHub
    custom_github_filename, ok = QInputDialog.getText(None, 'GitHub File Name', 'Enter the desired file name for GitHub (with extension):')

    if ok and custom_github_filename:
        api_url = f"https://api.github.com/repos/{github_username}/{repo_name}/contents/{custom_github_filename}"
        headers = {"Authorization": f"token {access_token}"}

        data = {
            "message": "Upload file via schBenedikt's Text Editor",
            "content": codecs.encode(content.encode("utf-8"), "base64").decode("utf-8"),
            "sha": get_sha_from_github(custom_github_filename, github_username, access_token, repo_name)
        }

        response = requests.put(api_url, headers=headers, json=data)

        if response.status_code == 200:
            print(f"File '{custom_github_filename}' uploaded to GitHub successfully.")
        else:
            print(f"Unable to upload file to GitHub. Status code: {response.status_code}, Message: {response.text}")

def upload_to_github(content, github_filename, github_username, access_token, repo_name):
    # Extract only the file name from the full path
    github_filename = os.path.basename(github_filename)

    api_url = f"https://api.github.com/repos/{github_username}/{repo_name}/contents/{github_filename}"
    headers = {"Authorization": f"token {access_token}"}

    data = {
        "message": "Update file via script",
        "content": codecs.encode(content.encode("utf-8"), "base64").decode("utf-8"),
        "sha": get_sha_from_github(github_filename, github_username, access_token, repo_name)
    }

    response = requests.put(api_url, headers=headers, json=data)

    if response.status_code == 200:
        print(f"File '{github_filename}' uploaded to GitHub successfully.")
    else:
        print(f"Unable to upload file to GitHub. Status code: {response.status_code}, Message: {response.text}")

def load_github_credentials():
    # Read GitHub credentials from upload_data.txt
    try:
        with open('upload_data.txt', 'r') as file:
            lines = file.readlines()
            github_username = lines[0].strip()
            access_token = lines[1].strip()
            repo_name = lines[2].strip()
            return github_username, access_token, repo_name
    except FileNotFoundError:
        print("upload_data.txt not found.")
        return None, None, None
