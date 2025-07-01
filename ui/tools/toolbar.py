from PyQt6.QtWidgets import (QTabWidget, QWidget, QToolButton, QFontComboBox,
                             QHBoxLayout, QFrame)
from PyQt6.QtGui import QIcon, QKeySequence, QAction
from PyQt6.QtCore import QSize, Qt

def create_ribbon(editor):
    """Creates a compact, single-row ribbon toolbar similar to the user's screenshot."""
    ribbon = QTabWidget()
    ribbon.setMovable(False)

    # --- Helper to create buttons ---
    def create_button(text, icon_path, method):
        button = QToolButton()
        
        if icon_path:
            button.setToolTip(text)
            button.setIcon(QIcon(icon_path))
            button.setIconSize(QSize(18, 18))
            button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        else:
            button.setText(text)
            button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)

        button.clicked.connect(method)
        return button

    # Helper to add a separator
    def create_separator():
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        return separator

    # --- Home Tab ---
    home_tab = QWidget()
    home_layout = QHBoxLayout(home_tab)
    home_layout.setContentsMargins(5, 2, 5, 2)
    home_layout.setSpacing(3)

    # Font actions
    home_layout.addWidget(create_button("Bold", "images/bold.png", editor.bold_text))
    home_layout.addWidget(create_button("Italic", "images/italic.png", editor.italic_text))
    home_layout.addWidget(create_button("Underline", "images/underline.png", editor.underline_text))
    home_layout.addWidget(create_button("Strikethrough", None, editor.strikethrough_text))
    home_layout.addWidget(create_button("Superscript", None, editor.set_superscript))
    home_layout.addWidget(create_button("Subscript", None, editor.set_subscript))
    
    home_layout.addWidget(create_button("Increase Font", "images/increase_font.png", editor.increase_font_size))
    home_layout.addWidget(create_button("Decrease Font", "images/decrease_font.png", editor.decrease_font_size))
    
    font_combo = QFontComboBox()
    font_combo.currentFontChanged.connect(editor.change_font)
    home_layout.addWidget(font_combo)

    home_layout.addWidget(create_button("Text Color", "images/change_color.png", editor.change_text_color))
    home_layout.addWidget(create_button("Highlight", "images/change_bg_color.png", editor.highlight_text))
    home_layout.addWidget(create_button("Clear Format", None, editor.clear_formatting))
    
    home_layout.addWidget(create_separator())

    # Paragraph actions
    home_layout.addWidget(create_button("Align Left", None, editor.align_left))
    home_layout.addWidget(create_button("Center", None, editor.align_center))
    home_layout.addWidget(create_button("Align Right", None, editor.align_right))
    home_layout.addWidget(create_button("Justify", None, editor.align_justify))
    home_layout.addWidget(create_button("Bullets", None, editor.bullet_list))
    home_layout.addWidget(create_button("Numbering", None, editor.numbered_list))
    home_layout.addWidget(create_button("Indent", None, editor.increase_indent))
    home_layout.addWidget(create_button("Outdent", None, editor.decrease_indent))
    
    home_layout.addStretch()
    ribbon.addTab(home_tab, "Home")

    # --- Insert Tab ---
    insert_tab = QWidget()
    insert_layout = QHBoxLayout(insert_tab)
    insert_layout.setContentsMargins(5, 2, 5, 2)
    insert_layout.addWidget(create_button("Insert Table", None, editor.insert_table_placeholder))
    insert_layout.addStretch()
    ribbon.addTab(insert_tab, "Insert")

    # --- View Tab ---
    view_tab = QWidget()
    view_layout = QHBoxLayout(view_tab)
    view_layout.setContentsMargins(5, 2, 5, 2)
    view_layout.addWidget(create_button("Read Mode", None, editor.set_read_only_mode))
    view_layout.addWidget(create_button("Draft Mode", None, editor.set_draft_mode))
    view_layout.addWidget(create_button("Print Layout", None, editor.set_print_layout))
    view_layout.addStretch()
    ribbon.addTab(view_tab, "View")

    # Find and Replace Action
    find_replace_action = QAction("Find and Replace", editor)
    find_replace_action.setShortcut(QKeySequence("Ctrl+H"))
    find_replace_action.triggered.connect(editor.show_find_replace_dialog)
    editor.addAction(find_replace_action)

    # Styling to match the screenshot's flat look
    ribbon.setStyleSheet("""
        QTabWidget::pane {
            border: 1px solid #C0C0C0;
        }
        QTabBar::tab {
            background: #F0F0F0;
            border: 1px solid #C0C0C0;
            border-bottom: none;
            padding: 4px 10px;
            min-width: 60px;
        }
        QTabBar::tab:selected {
            background: #FFFFFF;
        }
        QTabBar::tab:!selected:hover {
            background: #E0E0E0;
        }
        QToolButton {
            border: 1px solid transparent;
            padding: 2px;
            margin: 0px;
        }
        QToolButton:hover {
            background-color: #E0E8F0;
            border: 1px solid #A0B0C0;
        }
        QToolButton[toolButtonStyle="0"] { /* IconOnly */
             padding: 4px;
        }
        QToolButton[toolButtonStyle="2"] { /* TextOnly */
             padding: 4px 6px;
        }
        QFrame[frameShape="5"] { /* VLine */
            margin: 2px 4px;
        }
    """)

    return ribbon 