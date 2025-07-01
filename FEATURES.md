# Feature List

A comprehensive overview of all features in the Text Editor project.

## Table of Contents

* [File Management](#file-management)
* [Editing & Formatting](#editing--formatting)
* [Document Layout & View Modes](#document-layout--view-modes)
* [Tab & Project Management](#tab--project-management)
* [Search & Navigation](#search--navigation)
* [Export & Print](#export--print)
* [AI Tools](#ai-tools)
* [GitHub Integration](#github-integration)
* [Developer & About Tools](#developer--about-tools)
* [Status & Metrics](#status--metrics)
* [Roadmap](#roadmap)

## File Management

* Open files (`.txt`, `.md`, `.py`, etc.) via **File → Open**.
* Save files locally with **File → Save** (Ctrl+S).
* Export documents as:
  * DOCX via **Save → Export as DOCX**.
  * TXT via **Save → Export as TXT**.

## Editing & Formatting

* Undo/Redo (**Edit → Undo/Redo**, Ctrl+Z / Ctrl+Y).
* **Text Styles**: Bold, Italic, Underline, Strikethrough, Superscript, Subscript.
* **Font**: Change font family and adjust font size.
* **Color**: Set text color and highlight (background color).
* **Clear Formatting** to remove all character styles.
* **Lists & Indentation**: Bullets, Numbering, Increase/Decrease indent.
* **Alignment**: Align Left, Center, Right, Justify.
* **Insert Table Placeholder** via **Insert → Insert Table**.
* **Find & Replace** dialog (Ctrl+H) and simple **Search Word** (Ctrl+F).

## Document Layout & View Modes

* **Read Mode**: View-only layout.
* **Draft Mode**: Simplified page layout.
* **Print Layout Mode**: Paginated view resembling printed output.
* **Print Document** via **Save → Print** (Ctrl+P).

## Tab & Project Management

* **Tabbed Interface** to work on multiple documents.
* **New Tab** (Ctrl+T) and **Close Tab** controls.
* **Open Empty Tab** by default on startup.
* **Projects Menu**:
  * **Login** to GitHub via OAuth.
  * List and open files from your GitHub repositories.

## Search & Navigation

* **Search Word** (Ctrl+F) for quick lookup.
* **Find & Replace** (Ctrl+H) for text modifications.
* **Status Bar** shows:
  * Word count.
  * Character count.
  * Current line number.
* **Info Dock** provides detailed stats on demand.

## Export & Print

* **Export as DOCX**: Generate `.docx` files with formatting.
* **Export as TXT**: Plain text export.
* **Print Documents** through system print dialog.

## AI Tools

* **Enable AI** toggle in **AI Tools** tab.
* **Autocorrect**: Spelling and grammar corrections.
* **Improve Writing**: Enhance style and clarity.
* **Summarize**: Generate concise summaries.
* **Translate**: Language translation for selected text.
* **Custom Prompt**: Craft your own AI prompts.
* **Model Selection**: Choose between `llama3`, `mistral`, `grok-2`, `llama3.1`.

## GitHub Integration

* **OAuth Login** to GitHub with secure token storage.
* **Auto-login** using saved token (`github_token.txt`).
* **View Repositories** and **Open Files** directly from GitHub.
* **Save & Upload** files back to GitHub repositories.
* **Manage Credentials** via dedicated settings dialog.
* **Persisted Sessions** for seamless workflow.

## Developer & About Tools

* **Contributors View** under **Infos → Developer** shows GitHub contributors.
* **About Dialog** under **Infos → About** displays current version and latest release info.
* Direct link to new releases on GitHub.

## Status & Metrics

* Real-time **Word** and **Character** counts.
* **Line Number** display for current cursor position.
* Optional **Info Dock** for expanded metrics.

## Roadmap

See [IMPROVEMENT_PLAN.md](IMPROVEMENT_PLAN.md) for upcoming features, refactoring efforts, and quality improvements. 