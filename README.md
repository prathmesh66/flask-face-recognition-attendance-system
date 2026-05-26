# Face Recognition Attendance System (Flask + OpenCV)

A web-based attendance system that uses face recognition (OpenCV LBPH) to mark attendance and manage students.

## Features
- User login/registration (Flask + Flask-WTF)
- Role-based access (admin/user)
- Student CRUD + photo capture for training
- Face recognition API
- Attendance marking + export

# 🎥 Project Demo Videos

## Face Recognition Attendance System

[![Face Recognition Attendance System](https://img.youtube.com/vi/UfwXV1CNXo4/maxresdefault.jpg)](https://youtu.be/UfwXV1CNXo4)

## Project Setup
### 1) Install dependencies
```bash
pip install -r requirements.txt
```

### 2) Configure MySQL
Update `DB_CONFIG` in `app.py`:
- `host`, `user`, `password`, `database`, `port`

### 3) Create database tables
Run the DB setup script:
```bash
python databaseTest.py
```

### 4) Run the application
```bash
python app.py
```

Then open the app in your browser (usually `http://127.0.0.1:5000`).

## Usage
1. Register and verify email (if enabled)
2. Login as admin
3. Go to **Students** → add students + capture photos
4. Go to **Train Model** → train the recognizer (creates `clf.xml` and `id_mapping.pkl`)
5. Go to **Face Recognition** → upload/capture a face to mark attendance

## Notes
- `data_img/` stores training images.
- `clf.xml` and `id_mapping.pkl` are generated after training.

## Troubleshooting
- If face recognition says the model is not trained, run `/train` first.
- Ensure your MySQL service is running.
- For email sending, configure Flask-Mail credentials in `app.py`.
