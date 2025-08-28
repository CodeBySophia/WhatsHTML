from PySide6 import QtWidgets, QtGui

VERSION = "v_0.1"
CREATOR = "SophiaCode - codebysophia@gmail.com"
ICON_PATH = "icon.ico"
FEEDBACK_TEXT = """In case of any questions or bugs feel free to email me on <b>codebysophia@gmail.com</b> ,
describe your requirement in detail and attach a screenshot if possible. 
Thanks are welcome too :), you can also suggest new features.</p>"""

# Window style
def apply_fusion_style():
    # Set Fusion style
    QtWidgets.QApplication.setStyle("Fusion")

    # Change color palette to light theme
    palette = QtGui.QPalette()
    # Window background and text colors
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(255, 255, 255))  # White window background
    palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(0, 0, 0))    # Black text color
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(245, 245, 245))    # Light gray text field background
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(255, 255, 220)) # Tooltip background
    palette.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor(0, 0, 0))      # Tooltip text
    palette.setColor(QtGui.QPalette.Text, QtGui.QColor(0, 0, 0))            # Text color
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(240, 240, 240))    # Button background
    palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(0, 0, 0))      # Button text color
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(0, 120, 215))   # Highlight color (blue)
    palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(255, 255, 255)) # Highlighted text

    QtWidgets.QApplication.setPalette(palette)

    icon = QtGui.QIcon(ICON_PATH)
    QtWidgets.QApplication.setWindowIcon(icon)

QLINE_STYLE = """
QLineEdit {
    color: black;
    background-color: #f5f5f5;
}
QLineEdit::placeholder {
    color: black;
}
"""

QTEXT_STYLE = """
QTextEdit {
    color: black;
    background-color: #f5f5f5;
}
QTextEdit::placeholder {
    color: black;
}
"""

# Button styles
# In-app buttons
FN_BUTTON_STYLE = """
QPushButton {
    background-color: #ff0000;      /* Background color */
    color: black;                   /* Font color */
    font-weight: bold;              /* Bold font */
    font-size: 14px;                /* Font size */
    border-radius: 10px;            /* Round edges */
    padding: 5px;                   /* Inner padding */
}
QPushButton:hover {
    background-color: #45a049;      /* Color when mouse hover over */
}
QPushButton:pressed {
    background-color: #ffa500;      /* Color when pressed */
}
"""

# Button to run other apps
APP_BUTTON_STYLE = """
QPushButton {
    background-color: #ff0000;      /* Background color */
    color: white;                   /* Font color */
    font-weight: bold;              /* Bold font */
    font-size: 14px;                /* Font size */
    border-radius: 10px;            /* Round edges */
    padding: 5px;                   /* Inner padding */
}
QPushButton:hover {
    background-color: #45a049;      /* Color when mouse hover over */
}
QPushButton:pressed {
    background-color: #ffa500;      /* Color when pressed */
}
"""