# 🎓 Smart Student Management System (Smart SMS)

A role-based campus management web application built with **Flask**, **SQLAlchemy**, and **SQLite**. It provides dedicated portals for **Admins**, **Teachers**, and **Students** to manage academic records, subjects, and daily attendance.

---

## ✨ Features

### 🔐 Authentication & Security
- Role-based access control (`admin`, `teacher`, `student`) via custom route decorators.
- Secure password hashing with **Werkzeug**.
- Session-based authentication with automatic 30-minute inactivity timeout.
- Custom `403 Forbidden` and `404 Not Found` error pages.

### 🛠️ Admin Portal (`/admin`)
- **Dashboard:** Live overview of total students, teachers, subjects, departments, and today's attendance count.
- **Department Management:** Create and delete academic departments (prevents deleting departments with linked records).
- **Student Management:** Full CRUD with automatic login account creation and search by name, student ID, Roll/USN, or email.
- **Teacher Management:** Full CRUD with department assignment and subject overview.
- **Subject Management:** Create, edit, and delete subjects by semester/department and assign them to teachers.

### 👩‍🏫 Teacher Portal (`/teacher`)
- **Dashboard:** View assigned subjects and attendance entries marked today.
- **Mark Attendance:** Select an assigned subject and date to record or update `Present` / `Absent` status for enrolled students.
- **Attendance Records:** Filter and review past attendance history per subject.

### 🎒 Student Portal (`/student`)
- **Dashboard:** Subject-wise attendance overview with visual percentage progress bars.
- **My Attendance:** Detailed day-wise attendance history per subject with color-coded status badges (`≥ 75%` good, `60–74%` warning, `< 60%` low).
- **Profile:** View personal and academic details (USN, department, semester, contact info).

---

## 📂 Project Structure

```text
smart-student-management-system/
├── app/
│   ├── __init__.py            # App factory, blueprint registration, DB seeding
│   ├── helpers.py             # Auth decorators & current user helpers
│   ├── models.py              # SQLAlchemy models (User, Department, Student, Teacher, Subject, Attendance)
│   ├── auth/                  # Login, logout, and role-based home redirect
│   ├── admin/                 # Admin dashboard & CRUD routes
│   ├── teacher/               # Attendance marking & history routes
│   ├── student/               # Student dashboard, attendance, & profile routes
│   ├── static/
│   │   ├── css/style.css      # Responsive custom styling
│   │   └── js/app.js          # Auto-dismissing flash notifications
│   └── templates/             # Jinja2 HTML templates (base, layout, admin, teacher, student)
├── instance/
│   └── ssms.db                # SQLite database (auto-generated on first run)
├── config.py                  # Flask & SQLAlchemy configuration
├── requirements.txt           # Python dependencies
└── run.py                     # Application entry point
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python, Flask 3, Flask-SQLAlchemy |
| **Database** | SQLite |
| **Frontend** | Jinja2 Templates, HTML5, CSS3, Vanilla JS |
| **Security** | Werkzeug Password Hashing, Flask Sessions |

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone [https://github.com/hnnithin005/smart-student-management-system.git](https://github.com/hnnithin005/smart-student-management-system.git)
cd smart-student-management-system
```

### 2. Create a Virtual Environment & Install Dependencies
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Run the Application
```bash
python run.py
```
On first launch, the app automatically creates the SQLite database at `instance/ssms.db` and seeds it with sample departments, subjects, and demo accounts.

Open your browser and go to: **`http://127.0.0.1:5000`**

---

## 🔑 Demo Accounts

| Role | Username | Password |
|---|---|---|
| **Admin** | `admin` | `admin123` |
| **Teacher** | `teacher1` | `teacher123` |
| **Student** | `student1` | `student123` |
| **Student 2** | `student2` | `student123` |

---

## 🔧 Environment Variables (Optional)

For production deployments, set a custom secret key instead of using the default development key:

```bash
# Linux / macOS
export SECRET_KEY="your-secure-random-secret-key"

# Windows (PowerShell)
$env:SECRET_KEY="your-secure-random-secret-key"
```
