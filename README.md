# Chemical Equipment Parameter Visualizer (Hybrid App)

This is a **hybrid web and desktop application** built for an intern screening task.  
The project allows users to upload CSV files of chemical equipment data, view analyses and charts, and download PDF reports.  
It features a **common Django backend API** that serves both a **React.js web app** and a **PyQt5 desktop app**.

---

## Key Features

### Hybrid Application
A single backend API serves both a web app and a native desktop app.

### CSV Upload & Analysis
Users can upload CSV files. The backend uses **Pandas** to analyze the data, calculating:
- Averages (Flowrate, Pressure, Temperature)
- Total counts
- Equipment type distributions

### Data Visualization
- **Web:** Uses **Chart.js** to display a dynamic pie chart of equipment types.  
- **Desktop:** Uses **Matplotlib** to render the same pie chart in a native window.

###  History Management
The API stores and retrieves the **5 most recent dataset uploads**.

###  Authentication
The API is secured and requires **Basic Auth (username/password)** to access, which both clients implement.

### PDF Report Generation
Users can download a detailed **PDF summary** (with tables and charts) for any dataset in their history,  
generated on the fly by the backend using **ReportLab**.

---

## Tech Stack

| Layer | Technology | Purpose |
|:------|:------------|:--------|
| **Backend** | Python, Django, Django REST Framework | Common backend API |
| **Data Handling** | Pandas | Reading CSV & analytics |
| **Database** | SQLite | Store last 5 uploaded datasets |
| **Frontend (Web)** | React.js, Chart.js, Axios | Web interface, charts, API calls |
| **Frontend (Desktop)** | PyQt5, Matplotlib, Requests | Desktop interface, charts, API calls |
| **PDF** | ReportLab | PDF generation |
| **Auth** | DRF Basic Authentication | Securing the API |

---

## Setup & Installation

You will need **three separate terminals** to run this project.

---

### 1. Backend (Django)

First, set up and run the backend server.

```bash
# 1. Navigate to the backend folder
cd backend

# 2. Create and activate a Python virtual environment
# On macOS/Linux:
python3 -m venv venv
source venv/bin/activate

# On Windows:
# python -m venv venv
# .\venv\Scripts\activate

# 3. Install required libraries
pip install -r requirements.txt

# 4. Run database migrations to create tables
python manage.py migrate

# 5. Create your admin login
# (You will use this to log in to the apps)
python manage.py createsuperuser

# 6. Run the server!
python manage.py runserver
```

Your backend is now running on:
http://127.0.0.1:8000


## 2. Frontend (React)

In a new terminal, set up and run the React app.
```bash
# 1. Navigate to the React app folder
cd frontend-web/client

# 2. Install all node modules
npm install

# 3. Run the app!
npm start
```

Your web app is now running on:
http://localhost:3000



## 3. Frontend (Desktop)

In a third terminal, set up and run the PyQt5 app.
```bash
# 1. Navigate to the desktop folder
cd frontend-desktop

# 2. Create and activate a Python virtual environment
# On macOS/Linux:
python3 -m venv venv
source venv/bin/activate

# On Windows:
# python -m venv venv
# .\venv\Scripts\activate

# 3. Install required libraries
`pip install PyQt5 requests matplotlib`

# 4. Run the app!
python main.py
```


Your desktop app will launch in a new window.

## How to Use

1. Make sure **all three servers/apps** are running as described above.  
2. Open the **Web App** ([http://localhost:3000](http://localhost:3000)) or the **Desktop App**.  
3. Enter the **superuser credentials** you created during the backend setup.  
4. Click **"Login & Fetch History"**.  
5. Use the **"Upload"** button to upload the `sample_equipment_data.csv` file.  
6. The **charts and history** will update.  
7. You can now click:
   - **"Download PDF"** (on web), or  
   - **"Download Selected as PDF"** (on desktop)  
   to get your detailed report.
