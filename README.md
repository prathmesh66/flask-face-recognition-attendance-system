# Face Recognition Attendance System (Flask + OpenCV)

> **⚠️ Public Showcase Repository**  
> This repository contains a public showcase version of the project.  
> Certain sensitive/internal implementation details and advanced logic have been intentionally simplified or removed for security and project protection purposes.

# 🎥 Project Demo

> Click the thumbnail below to watch the full working demo of the project.

[![Face Recognition Attendance System](https://img.youtube.com/vi/UfwXV1CNXo4/maxresdefault.jpg)](https://youtu.be/UfwXV1CNXo4)

---

## Project Overview

A web-based attendance management system built using Flask and OpenCV LBPH face recognition for automated student attendance tracking and management.

---

## Tech Stack

- Python
- Flask
- OpenCV
- MySQL
- HTML/CSS/JavaScript

---

## Features

- User login & registration system
- Role-based access control (Admin/User)
- Student CRUD operations
- Student image capture & training
- Face recognition attendance marking
- Attendance export functionality
- Flask-WTF form validation
- MySQL database integration

---

## Project Setup

### 1) Clone Repository

```bash
git clone https://github.com/prathmesh66/flask-face-recognition-attendance-system.git
```

### 2) Create Virtual Environment

```bash
python -m venv venv
```

### 3) Activate Virtual Environment

For Windows PowerShell:

```bash
.\venv\Scripts\Activate
```

For CMD:

```bash
venv\Scripts\activate
```

### 4) Install Dependencies

```bash
pip install -r requirements.txt
```

### 5) Configure MySQL Database

Update `DB_CONFIG` inside `app.py`:

- host
- user
- password
- database
- port

### 6) Create Database Tables

```bash
python databaseTest.py
```

### 7) Run Application

```bash
python app.py
```

Open in browser:

```text
http://127.0.0.1:5000
```

---

## Usage

1. Register/Login to the system
2. Login as Admin
3. Add students and capture images
4. Train the face recognition model
5. Start face recognition attendance system
6. Export attendance records if needed

---

## Important Files

- `haarcascade_frontalface_default.xml` → OpenCV face detection cascade
- `clf.xml` → Trained face recognition model
- `id_mapping.pkl` → Student ID mapping
- `data_img/` → Stores training images

---

## Notes

- Ensure MySQL service is running before starting the application.
- Train the model before using face recognition attendance.
- Email functionality requires Flask-Mail configuration.

---

## Troubleshooting

### Model Not Trained

If attendance recognition fails, retrain the model from the application dashboard.

### Database Connection Error

- Ensure MySQL server is running
- Verify database credentials in `app.py`

### Missing Dependencies

```bash
pip install -r requirements.txt
```
