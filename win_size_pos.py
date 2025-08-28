from PySide6 import QtWidgets

# Unified apps window size a position

def set_win_size(window: QtWidgets.QWidget):
    # Obtain screen resolution
    screen = QtWidgets.QApplication.primaryScreen()
    screen_geometry = screen.availableGeometry()
    screen_width = screen_geometry.width()
    screen_height = screen_geometry.height()

    # Set window size to half of screen
    window_width = int(screen_width / 3 * 2)
    window_height = int(screen_height / 3 * 2)

    # Window position
    pos_x = int((screen_width - window_width) / 2)
    pos_y = int((screen_height - window_height) / 2)

    # Set size and position of the window
    window.setGeometry(pos_x, pos_y, window_width, window_height)
    #window.setFixedSize(window_width, window_height) # Fixed window size