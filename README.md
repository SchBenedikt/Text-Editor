# Text Editor

A modern text editor built with Python and PyQt6, featuring seamless integration with GitHub for version control and collaboration.

![image](https://github.com/user-attachments/assets/98dcd5af-6dae-4e01-b083-66c8709d1d62)

## ✨ Features

*   **File Operations**: Open, save, and export files as DOCX.
*   **Rich Text Formatting**: Bold, italic, underline, change font, and adjust font size.
*   **Tabbed Interface**: Work on multiple documents in separate tabs.
*   **GitHub Integration**:
    *   Authenticate with your GitHub account.
    *   View your repositories.
    *   (Coming soon) Save files directly to your GitHub repositories.

## 🚀 Getting Started

Follow these steps to set up your development environment.

### Prerequisites

*   Python 3.8+
*   `pip` and `git` installed.

### ⚙️ Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/SchBenedikt/Text-Editor.git
    cd Text-Editor
    ```

2.  **Run the setup script:**
    This script will install dependencies and guide you through creating a `.env` file for your GitHub credentials.
    ```bash
    python setup_dev.py
    ```

3.  **Create a GitHub OAuth App:**
    The setup script will prompt you for your GitHub OAuth credentials. You can create them here: [https://github.com/settings/applications/new](https://github.com/settings/applications/new)

    Use the following settings for your OAuth App:
    *   **Application name:** Text Editor Dev (or any name you prefer)
    *   **Homepage URL:** `http://localhost:5000`
    *   **Authorization callback URL:** `http://127.0.0.1:5000/callback`

    After creating the app, copy the "Client ID" and generate a "Client Secret". Paste these into the terminal when the setup script asks for them.

### ▶️ Running the Application

Once the setup is complete, you can run the text editor:
```bash
python main.py
```
If you encounter issues with QT plugins on Windows, you may need to add the PyQt6 Qt bin directory to your `PATH`. You can do this by running the following command in an administrator terminal:
```powershell
setx PATH "%PATH%;%LOCALAPPDATA%\Programs\Python\Python311\Lib\site-packages\PyQt6\Qt6\bin"
```
*(Adjust the Python version in the path if necessary)*

## 🗺️ Roadmap

We have an ambitious roadmap for the Text Editor. Our plans are outlined in the [IMPROVEMENT_PLAN.md](IMPROVEMENT_PLAN.md). Key highlights include:

*   **Refactoring:** Splitting the UI into more manageable modules.
*   **Features:** Implementing auto-save and improving GitHub integration.
*   **Quality:** Adding comprehensive logging and unit tests.

## 🤝 Contributing

Contributions are welcome! We have a lot of work to do and would appreciate your help.

*   Check out our [IMPROVEMENT_PLAN.md](IMPROVEMENT_PLAN.md) to see what we're working on.
*   Feel free to open an [issue](https://github.com/SchBenedikt/Text-Editor/issues) for bug reports or feature requests.
*   Submit a [pull request](https://github.com/SchBenedikt/Text-Editor/pulls) with your changes.

## 📄 License

This project is licensed under the terms of the [LICENSE](LICENSE) file.
