import sys
import requests
# --- ADD THIS IMPORT ---
from requests.auth import HTTPBasicAuth
# -----------------------

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QFileDialog, QMessageBox, QTableWidget,
    QTableWidgetItem, QLabel, QFrame, QSizePolicy, QListWidgetItem,
    # --- ADD THESE IMPORTS ---
    QLineEdit, QFormLayout
    # -----------------------
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
# Matplotlib imports
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# --- Configuration ---
API_URL = "http://127.0.0.1:8000/api/datasets/"

class MatplotlibCanvas(FigureCanvas):
    """A custom Matplotlib widget for PyQt5"""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # We tight_layout to make it fit nicely
        fig.set_tight_layout(True) 
        super(MatplotlibCanvas, self).__init__(fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Chemical Equipment Parameter Visualizer')
        self.setGeometry(100, 100, 1200, 700)
        
        # --- Central Widget and Layout ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # --- 1. Left Panel (Controls & History) ---
        self.left_panel = QFrame()
        self.left_panel.setFrameShape(QFrame.StyledPanel)
        self.left_panel_layout = QVBoxLayout()

        # --- NEW: Auth Form ---
        self.auth_label = QLabel('Authentication')
        self.auth_label.setFont(QFont('Arial', 11, QFont.Bold))
        self.left_panel_layout.addWidget(self.auth_label)
        
        self.auth_form = QWidget()
        self.form_layout = QFormLayout(self.auth_form)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Your username")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.form_layout.addRow('Username:', self.username_input)
        self.form_layout.addRow('Password:', self.password_input)
        self.left_panel_layout.addWidget(self.auth_form)
        # ------------------------
        
        # --- NEW: Add a button to "Login & Fetch" ---
        self.fetch_btn = QPushButton('Login & Fetch History')
        self.fetch_btn.setFont(QFont('Arial', 12, QFont.Bold))
        self.fetch_btn.clicked.connect(self.fetch_history)
        self.left_panel_layout.addWidget(self.fetch_btn)
        # -----------------------------------------------

        # Upload Button
        self.upload_btn = QPushButton('Upload New Dataset (.csv)')
        self.upload_btn.setFont(QFont('Arial', 12, QFont.Bold))
        self.upload_btn.clicked.connect(self.upload_file)
        self.left_panel_layout.addWidget(self.upload_btn)
        
        # History List
        self.history_label = QLabel('Upload History (Last 5)')
        self.history_label.setFont(QFont('Arial', 11, QFont.Bold))
        self.left_panel_layout.addWidget(self.history_label)
        
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.on_history_item_clicked)
        self.left_panel_layout.addWidget(self.history_list)
        
        self.download_btn = QPushButton('Download Selected as PDF')
        self.download_btn.clicked.connect(self.download_pdf)
        self.left_panel_layout.addWidget(self.download_btn)
        
        self.left_panel.setLayout(self.left_panel_layout)
        self.main_layout.addWidget(self.left_panel, 1) # 1 part width

        # --- 2. Right Panel (Data Visualization) ---
        self.right_panel = QFrame()
        self.right_panel.setFrameShape(QFrame.StyledPanel)
        self.right_panel_layout = QVBoxLayout()
        
        self.analysis_label = QLabel('Analysis Dashboard')
        self.analysis_label.setFont(QFont('Arial', 16, QFont.Bold))
        self.analysis_label.setAlignment(Qt.AlignCenter)
        self.right_panel_layout.addWidget(self.analysis_label)
        
        # Data container
        self.data_container = QWidget()
        self.data_layout = QHBoxLayout(self.data_container)

        # 2a. Summary Table
        self.summary_table = QTableWidget()
        self.data_layout.addWidget(self.summary_table, 1)
        
        # 2b. Matplotlib Chart
        self.chart_canvas = MatplotlibCanvas(self)
        self.data_layout.addWidget(self.chart_canvas, 1)

        self.right_panel_layout.addWidget(self.data_container)
        self.right_panel.setLayout(self.right_panel_layout)
        self.main_layout.addWidget(self.right_panel, 3) # 3 parts width
        
        # --- Initial Load ---
        # We removed the automatic fetch_history() call here
    def download_pdf(self):
        auth = self.get_auth()
        if auth is None: return

        # 1. Get the currently selected dataset
        current_item = self.history_list.currentItem()
        if not current_item:
            self.show_message("Error", "Please select a dataset from the history list first.")
            return
            
        dataset = current_item.data(Qt.UserRole)
        dataset_id = dataset['id']
        dataset_name = dataset['name'].replace('.csv', '') # Clean up name

        # 2. Ask user where to save the file
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save PDF Report", 
            f"{dataset_name}_summary.pdf", # Default filename
            "PDF Files (*.pdf)"
        )
        
        if not file_path:
            return # User cancelled

        # 3. Fetch the PDF from the API
        try:
            url = f"{API_URL}{dataset_id}/download_pdf/"
            response = requests.get(url, auth=auth)
            response.raise_for_status() # Check for errors
            
            # 4. Write the received content (bytes) to the file
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            self.show_message("Success", f"Report saved successfully to:\n{file_path}")

        except requests.exceptions.HTTPError as e:
            self.show_message("Download Failed", f"HTTP Error: {e}")
        except Exception as e:
            self.show_message("Download Failed", f"An error occurred: {e}")
            
    def get_auth(self):
        """Helper to get auth credentials from inputs"""
        username = self.username_input.text()
        password = self.password_input.text()
        if not username or not password:
            self.show_message("Auth Error", "Please enter username and password.")
            return None
        return HTTPBasicAuth(username, password)

    def fetch_history(self):
        """Gets the list of last 5 datasets from the API"""
        auth = self.get_auth()
        if auth is None: return

        try:
            # --- MODIFIED: Add auth=auth ---
            response = requests.get(API_URL, auth=auth)
            # ---------------------------------
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            
            self.history_list.clear()
            datasets = response.json()
            
            if not datasets:
                self.show_message("Info", "No datasets found in history.")
                self.display_summary(None) # Clear the display
                return

            for dataset in datasets:
                # Store the full dataset JSON in the item
                item = QListWidgetItem(dataset['name'])
                item.setData(Qt.UserRole, dataset) # Store full data
                self.history_list.addItem(item)
            
            # Automatically display the most recent one
            self.display_summary(datasets[0])
            self.history_list.setCurrentRow(0)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401 or e.response.status_code == 403:
                self.show_message("Error", "Login failed. Check username/password.")
            else:
                self.show_message("Error", f"HTTP Error: {e}")
        except requests.exceptions.ConnectionError:
            self.show_message("Error", "Could not connect to backend. Is it running?")
        except Exception as e:
            self.show_message("Error", f"Failed to fetch history: {e}")

    def upload_file(self):
        """Opens a file dialog and uploads the selected CSV"""
        auth = self.get_auth()
        if auth is None: return

        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        
        if not file_path:
            return # User cancelled

        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path, f, 'text/csv')}
                # --- MODIFIED: Add auth=auth ---
                response = requests.post(API_URL, files=files, auth=auth)
                # ---------------------------------
                response.raise_for_status()
            
            self.show_message("Success", "File uploaded and analyzed successfully!")
            self.fetch_history() # Refresh history to show the new file
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401 or e.response.status_code == 403:
                self.show_message("Error", "Login failed. Check username/password.")
            else:
                self.show_message("Upload Failed", f"Error from server: {e.response.json().get('error', 'Unknown error')}")
        except Exception as e:
            self.show_message("Upload Failed", f"An error occurred: {e}")

    def on_history_item_clicked(self, item):
        """Displays data when a history item is clicked"""
        dataset = item.data(Qt.UserRole) # Retrieve the stored JSON
        self.display_summary(dataset)

    def display_summary(self, dataset):
        """Updates the right panel with data from a dataset"""
        # --- Clear charts if no dataset ---
        if not dataset or not dataset.get('summary'):
            self.analysis_label.setText("No analysis data available. Please log in.")
            self.summary_table.clear()
            self.summary_table.setRowCount(0)
            self.summary_table.setColumnCount(0)
            self.chart_canvas.axes.clear()
            self.chart_canvas.draw()
            return
        # ------------------------------------
        
        summary = dataset.get('summary')
            
        self.analysis_label.setText(f"Analysis for: {dataset.get('name', 'Untitled')}")

        # --- 1. Populate Summary Table ---
        self.summary_table.clear()
        self.summary_table.setRowCount(4) # Count + 3 averages
        self.summary_table.setColumnCount(2)
        self.summary_table.setHorizontalHeaderLabels(['Metric', 'Value'])
        
        self.summary_table.setItem(0, 0, QTableWidgetItem("Total Count"))
        self.summary_table.setItem(0, 1, QTableWidgetItem(str(summary['total_count'])))
        
        avg = summary['averages']
        self.summary_table.setItem(1, 0, QTableWidgetItem("Avg. Flowrate"))
        self.summary_table.setItem(1, 1, QTableWidgetItem(f"{avg.get('avg_flowrate', 0):.2f}"))
        
        self.summary_table.setItem(2, 0, QTableWidgetItem("Avg. Pressure"))
        self.summary_table.setItem(2, 1, QTableWidgetItem(f"{avg.get('avg_pressure', 0):.2f}"))
        
        self.summary_table.setItem(3, 0, QTableWidgetItem("Avg. Temperature"))
        self.summary_table.setItem(3, 1, QTableWidgetItem(f"{avg.get('avg_temperature', 0):.2f}"))
        
        self.summary_table.resizeColumnsToContents()

        # --- 2. Update Matplotlib Pie Chart ---
        type_dist = summary['type_distribution']
        labels = type_dist.keys()
        sizes = type_dist.values()
        
        self.chart_canvas.axes.clear() # Clear the previous plot
        self.chart_canvas.axes.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        self.chart_canvas.axes.set_title('Equipment Type Distribution')
        self.chart_canvas.axes.axis('equal') # Equal aspect ratio
        self.chart_canvas.draw() # Redraw the canvas

    def show_message(self, title, message):
        """Helper function to show a popup message box"""
        QMessageBox.information(self, title, message)

# --- Run the Application ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())