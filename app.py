from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, Response
from flask_mail import Mail, Message
from functools import wraps
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email
import pymysql
import cv2
import os
import glob
import numpy as np
from PIL import Image, ImageTk
import secrets
import datetime
import pandas as pd

app = Flask(__name__)

# Global variable to track recent recognitions and prevent duplicate attendance marking
recent_recognitions = {}
RECOGNITION_COOLDOWN = 30  # seconds
app.secret_key = "dev_secret_key"  # Required for session and flashing messages

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ps6685472@gmail.com'
app.config['MAIL_PASSWORD'] = 'slqc vmpa nagf axrc'    # Replace with your app password
app.config['MAIL_DEFAULT_SENDER'] = 'ps6685472@gmail.com'

mail = Mail(app)

# Database configuration
DB_CONFIG = {
    'user': 'root',
    'password': 'Tanmay',
    'host': 'localhost',
    'database': 'face_recognition',
    'port': 3306,
    'charset': 'utf8mb4'
}

# Placeholder for form object used in templates
form = None

# Form Classes
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Create Account')

class DeleteUserForm(FlaskForm):
    user_id = SelectField('User', coerce=int, validators=[DataRequired()])
    confirm_delete = BooleanField('I confirm that I want to delete this user permanently', validators=[DataRequired()])
    submit = SubmitField('Delete User')

# Access Control Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            # Check if this is an API request
            if request.path.startswith('/api/'):
                return jsonify({"error": "Authentication required"}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            # Check if this is an API request
            if request.path.startswith('/api/'):
                return jsonify({"error": "Admin privileges required"}), 403
            flash("Access denied: Admin privileges required.")
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_user():
    user = None
    user_role = session.get('role', 'user')
    if session.get('logged_in'):
        user = {
            'username': session.get('username', 'Admin'),
            'role': user_role
        }
    return dict(current_user=user, user_role=user_role)

@app.route('/home')
def home():
    return render_template('homepage.html')

# Database helper functions
def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

# Student Management Functions
def get_students():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM student")
    students = cursor.fetchall()
    conn.close()

    # Convert non-serializable objects to strings
    for student in students:
        for key, value in student.items():
            if isinstance(value, (datetime.date, datetime.datetime)):
                student[key] = value.isoformat()

    return students

def add_student():
    try:
        data = request.form

        # Debug: Log received data
        print(f"Received form data: {dict(data)}")

        # Validate required fields
        required_fields = ['student_id', 'name', 'roll_no', 'department', 'year', 'semester', 'division', 'gender', 'dob', 'email', 'address']
        for field in required_fields:
            field_value = data.get(field, '').strip()
            if not field_value:
                print(f"Missing required field: {field}")
                return jsonify({"error": f"{field.replace('_', ' ').title()} is required"}), 400

        # Validate email format
        import re
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, data.get('email', '').strip()):
            return jsonify({"error": "Invalid email format"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if student already exists
        cursor.execute("SELECT * FROM student WHERE Student_id = %s", (data['student_id'].strip(),))
        existing_student = cursor.fetchone()

        # Prepare data with proper field mapping
        student_data = {
            'student_id': data['student_id'].strip(),
            'name': data['name'].strip(),
            'roll_no': data['roll_no'].strip(),
            'department': data['department'].strip(),
            'year': data['year'].strip(),
            'semester': data['semester'].strip(),
            'division': data['division'].strip(),
            'gender': data['gender'].strip(),
            'dob': data['dob'].strip(),
            'email': data['email'].strip(),
            'phone': data.get('mobile', data.get('phone', '')).strip(),  # Handle both 'mobile' and 'phone'
            'address': data['address'].strip(),
            'course': data.get('course', '').strip(),  # Optional field
            'teacher_name': data.get('teacher_name', '').strip()  # Optional field
        }

        print(f"Prepared student data: {student_data}")

        if existing_student:
            # Update existing student
            cursor.execute("""
                UPDATE student SET Name=%s, Roll_No=%s, Department=%s, Year=%s, Semester=%s,
                Division=%s, Gender=%s, DOB=%s, Email=%s, Phone=%s, Address=%s, Photo=%s
                WHERE Student_id=%s
            """, (
                student_data['name'], student_data['roll_no'], student_data['department'],
                student_data['year'], student_data['semester'], student_data['division'],
                student_data['gender'], student_data['dob'], student_data['email'],
                student_data['phone'], student_data['address'], 'Yes', student_data['student_id']
            ))
        else:
            # Insert new student
            cursor.execute("""
                INSERT INTO student (Student_id, Name, Roll_No, Department, Year, Semester, Division, Gender, DOB, Email, Phone, Address, Photo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                student_data['student_id'], student_data['name'], student_data['roll_no'],
                student_data['department'], student_data['year'], student_data['semester'],
                student_data['division'], student_data['gender'], student_data['dob'],
                student_data['email'], student_data['phone'], student_data['address'], 'Yes'
            ))

        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Student saved successfully", "student_id": student_data['student_id']})
    except Exception as e:
        print(f"Add student error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def get_student(student_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM student WHERE Student_id = %s", (student_id,))
        student = cursor.fetchone()
        conn.close()
        if student:
            return jsonify(student)
        else:
            return jsonify({"error": "Student not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def update_student(student_id):
    try:
        data = request.form
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE student SET Name=%s, Roll_No=%s, Department=%s, Year=%s, Semester=%s,
            Division=%s, Gender=%s, DOB=%s, Email=%s, Phone=%s, Address=%s, Photo=%s
            WHERE Student_id=%s
        """, (
            data['name'], data['roll_no'], data['department'], data['year'], data['semester'],
            data['division'], data['gender'], data['dob'], data['email'],
            data.get('mobile', data.get('phone', '')), data['address'], 'Yes', student_id
        ))

        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Student updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def delete_student(student_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Delete associated photos first
        image_pattern = f"data_img/student.{student_id}.*.jpg"
        deleted_photos = 0
        for image_file in glob.glob(image_pattern):
            try:
                os.remove(image_file)
                deleted_photos += 1
            except:
                pass

        # Delete from database
        cursor.execute("DELETE FROM student WHERE Student_id = %s", (student_id,))
        conn.commit()
        conn.close()

        return jsonify({"status": "success", "message": f"Student deleted successfully. {deleted_photos} photos removed."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def process_capture_photo(student_id):
    try:
        # Check if student exists
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM student WHERE Student_id = %s", (student_id,))
        student = cursor.fetchone()
        conn.close()

        if not student:
            return jsonify({"error": "Student not found"}), 404

        # For web interface, receive base64 image
        image_data = request.form.get('image')
        if image_data:
            try:
                # Decode base64 image
                import base64
                from PIL import Image
                import io

                # Handle different base64 formats
                if ',' in image_data:
                    image_data = image_data.split(',')[1]  # Remove data:image/jpeg;base64, prefix

                image_bytes = base64.b64decode(image_data)

                # Ensure data_img directory exists with proper permissions
                data_img_dir = "data_img"
                if not os.path.exists(data_img_dir):
                    os.makedirs(data_img_dir, exist_ok=True)

                # Find next available image number
                existing_images = glob.glob(os.path.join(data_img_dir, f"student.{student_id}.*.jpg"))
                img_id = len(existing_images) + 1

                file_path = os.path.join(data_img_dir, f"student.{student_id}.{img_id}.jpg")

                # Convert to PIL Image and save
                image = Image.open(io.BytesIO(image_bytes))

                # Convert to RGB if necessary, then to grayscale
                if image.mode != 'RGB':
                    image = image.convert('RGB')

                image = image.convert('L')  # Convert to grayscale
                image = image.resize((200, 200), Image.Resampling.LANCZOS)
                image.save(file_path, 'JPEG', quality=95)

                # Verify file was created
                if os.path.exists(file_path):
                    return jsonify({
                        "status": "success",
                        "message": f"Image {img_id} captured successfully",
                        "image_path": file_path,
                        "image_id": img_id
                    })
                else:
                    return jsonify({"error": "Failed to save image file"}), 500

            except Exception as img_error:
                print(f"Image processing error: {img_error}")
                return jsonify({"error": f"Image processing failed: {str(img_error)}"}), 500
        else:
            return jsonify({"error": "No image data provided"}), 400

    except Exception as e:
        print(f"Photo capture error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return render_template('homepage.html')

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        conn = get_db_connection()

        # Get total students count
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM student")
        total_students = cursor.fetchone()[0]

        # Get today's attendance count
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) FROM stdattendance WHERE DATE(std_date) = %s AND std_attendance = 'Present'", (today,))
        today_attendance = cursor.fetchone()[0]

        # Get total attendance records
        cursor.execute("SELECT COUNT(*) FROM stdattendance")
        total_attendance = cursor.fetchone()[0]

        conn.close()

        # Check if trained model exists
        clf_exists = os.path.exists("clf.xml")

    except Exception as e:
        print(f"Database error: {e}")
        total_students = 0
        today_attendance = 0
        total_attendance = 0
        clf_exists = False

    user_role = session.get('role', 'user')
    return render_template('dashboard.html', total_students=total_students, today_attendance=today_attendance, total_attendance=total_attendance, clf_exists=clf_exists, user_role=user_role)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        try:
            # Verify credentials against the database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM regteach WHERE email = %s AND password = %s",
                          (email, password))
            user = cursor.fetchone()
            conn.close()

            if user:
                # Check if email is verified
                if not user[9]:  # verified column (index 9 in regteach table)
                    flash("Please verify your email address before logging in.")
                    return redirect(url_for('login'))

                session['logged_in'] = True
                session['role'] = user[11]  # role column (index 11 in regteach table)
                session['username'] = user[4]  # username column (index 4 in regteach table)
                session['user_id'] = user[0]  # id column
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid email or password.")
                return redirect(url_for('login'))

        except Exception as e:
            flash(f"Login failed: {str(e)}")
            return redirect(url_for('login'))

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Generate verification token
        token = secrets.token_urlsafe(32)

        try:
            # Save user to database with unverified status
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check if user already exists
            cursor.execute("SELECT * FROM regteach WHERE email = %s", (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash("Email already registered. Please use a different email.")
                conn.close()
                return redirect(url_for('register'))

            # Insert new user
            cursor.execute("""
                INSERT INTO regteach (username, email, password, role, verified, verification_token)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (username, email, password, 'user', False, token))

            conn.commit()
            conn.close()

            # Send verification email
            verification_url = url_for('verify_email', token=token, _external=True)
            msg = Message('Verify Your Email - Face Recognition System',
                         recipients=[email])
            msg.body = f'''Hi {username},

Thank you for registering with the Face Recognition Attendance System!

Please click the link below to verify your email address:
{verification_url}

If you did not create this account, please ignore this email.

Best regards,
Face Recognition System Team
'''
            mail.send(msg)

            flash("Registration successful! Please check your email to verify your account.")
            return redirect(url_for('login'))

        except Exception as e:
            flash(f"Registration failed: {str(e)}")
            return redirect(url_for('register'))

    return render_template('register.html', form=form)

@app.route('/verify_email/<token>')
def verify_email(token):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Find user with this verification token
        cursor.execute("SELECT * FROM regteach WHERE verification_token = %s AND verified = %s",
                      (token, False))
        user = cursor.fetchone()

        if user:
            # Mark user as verified
            cursor.execute("UPDATE regteach SET verified = %s, verification_token = %s WHERE id = %s",
                          (True, None, user[0]))
            conn.commit()
            conn.close()

            flash("Email verified successfully! You can now log in.")
            return redirect(url_for('login'))
        else:
            conn.close()
            flash("Invalid or expired verification link.")
            return redirect(url_for('login'))

    except Exception as e:
        flash(f"Verification failed: {str(e)}")
        return redirect(url_for('login'))

@app.route('/face_recognition')
@login_required
def face_recognition():
    return render_template('face_recognition.html')

@app.route('/attendance')
@login_required
def attendance():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        user_role = session.get('role', 'user')

        if user_role == 'admin':
            # Admin sees all attendance records
            cursor.execute("SELECT * FROM stdattendance ORDER BY std_date DESC, std_time DESC")
        else:
            # Regular users see only their own attendance records
            # Note: In a real system, you'd need to link users to students
            # For now, showing all records for regular users too (can be modified later)
            cursor.execute("SELECT * FROM stdattendance ORDER BY std_date DESC, std_time DESC")

        records = cursor.fetchall()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")
        records = []
        user_role = session.get('role', 'user')

    return render_template('attendance.html', records=records, user_role=user_role)

@app.route('/reports')
@login_required
def reports():
    return render_template('reports.html')

@app.route('/student')
@login_required
@admin_required
def student():
    return render_template('student.html')

@app.route('/train')
@login_required
@admin_required
def train():
    try:
        # Count images in data_img directory
        data_dir = "data_img"
        image_count = 0
        if os.path.exists(data_dir):
            image_count = len([f for f in os.listdir(data_dir) if f.endswith('.jpg')])

        # Check if trained model exists
        clf_exists = os.path.exists("clf.xml")

    except Exception as e:
        print(f"Error checking training data: {e}")
        image_count = 0
        clf_exists = False

    return render_template('train.html', image_count=image_count, clf_exists=clf_exists)

@app.route('/delete_user', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_user():
    form = DeleteUserForm()
    if form.validate_on_submit():
        # Placeholder: In production, delete user from database
        flash("User deleted successfully.")
        return redirect(url_for('dashboard'))
    return render_template('delete_user.html', form=form)

# ==================== API Routes for Student Management ====================

@app.route('/api/students', methods=['GET'])
@login_required
def api_get_students():
    try:
        students = get_students()
        return jsonify({"students": students})
    except Exception as e:
        print(f"API students error: {e}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/api/students', methods=['POST'])
@login_required
@admin_required
def api_add_student():
    return add_student()

@app.route('/api/students/<student_id>', methods=['GET'])
@login_required
def api_get_student(student_id):
    return get_student(student_id)

@app.route('/api/students/<student_id>', methods=['PUT'])
@login_required
@admin_required
def api_update_student(student_id):
    return update_student(student_id)

@app.route('/api/students/<student_id>', methods=['DELETE'])
@login_required
@admin_required
def api_delete_student(student_id):
    return delete_student(student_id)

@app.route('/capture_photo/<student_id>')
@login_required
@admin_required
def capture_photo(student_id):
    return render_template('capture_photo.html', student_id=student_id)

@app.route('/api/capture_photo/<student_id>', methods=['POST'])
@login_required
@admin_required
def api_capture_photo(student_id):
    return process_capture_photo(student_id)

# ==================== Face Recognition API ====================

@app.route('/api/recognize_face', methods=['POST'])
@login_required
def api_recognize_face():
    try:
        # Check if model exists
        if not os.path.exists("clf.xml"):
            return jsonify({"error": "Model not trained. Please train the model first."}), 400

        # Get image from request
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"}), 400

        image_file = request.files['image']

        # Convert to OpenCV format
        image_bytes = image_file.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({"recognized": False, "message": "Invalid image format"})

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply histogram equalization for better recognition
        gray = cv2.equalizeHist(gray)

        # Load face cascade
        face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

        # Detect faces with improved parameters
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.05,  # More sensitive detection
            minNeighbors=2,    # Less restrictive
            minSize=(20, 20)   # Smaller minimum face size
        )

        if len(faces) == 0:
            return jsonify({"recognized": False, "message": "No face detected"})

        # Load trained model
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read("clf.xml")

        # Load ID mapping
        id_map = {}
        try:
            import pickle
            with open("id_mapping.pkl", "rb") as f:
                id_map = pickle.load(f)
        except:
            return jsonify({"error": "ID mapping file not found"}), 500

        # Reverse mapping (int_id -> string_id)
        reverse_map = {v: k for k, v in id_map.items()}

        # Process each face
        for (x, y, w, h) in faces:
            # Ensure face ROI is within image bounds
            x, y, w, h = max(0, x), max(0, y), min(w, gray.shape[1]-x), min(h, gray.shape[0]-y)

            face_roi = gray[y:y+h, x:x+w]

            # Skip if face ROI is too small
            if face_roi.shape[0] < 50 or face_roi.shape[1] < 50:
                continue

            face_roi = cv2.resize(face_roi, (200, 200))

            # Predict
            id_pred, confidence = recognizer.predict(face_roi)

            # Convert distance to confidence percentage
            confidence = int((100 * (1 - confidence / 300)))

            print(f"Face detected - ID: {id_pred}, Confidence: {confidence}%")

            # Lower confidence threshold for better recognition
            if confidence > 60:  # Changed from 77% to 60%
                string_id = reverse_map.get(id_pred)

                if string_id:
                    # Check if this student was recently recognized (prevent duplicate attendance)
                    current_time = datetime.datetime.now().timestamp()
                    if string_id in recent_recognitions:
                        last_recognition = recent_recognitions[string_id]
                        if current_time - last_recognition < RECOGNITION_COOLDOWN:
                            print(f"Skipping duplicate recognition for student {string_id} - too soon")
                            return jsonify({"recognized": False, "message": "Student already recognized recently"})

                    # Update recent recognition time
                    recent_recognitions[string_id] = current_time

                    # Get student details
                    conn = get_db_connection()
                    cursor = conn.cursor(pymysql.cursors.DictCursor)
                    cursor.execute("SELECT * FROM student WHERE Student_id = %s", (string_id,))
                    student = cursor.fetchone()
                    conn.close()

                    if student:
                        # Mark attendance
                        mark_attendance(string_id, student['Roll_No'], student['Name'])

                        return jsonify({
                            "recognized": True,
                            "student": {
                                "id": string_id,
                                "name": student['Name'],
                                "roll_no": student['Roll_No'],
                                "department": student['Department']
                            },
                            "confidence": confidence,
                            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })

        return jsonify({"recognized": False, "message": "Face not recognized"})

    except Exception as e:
        print(f"Recognition error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def mark_attendance(student_id, roll_no, name):
    """Mark attendance for recognized student"""
    try:
        # Use consistent date format with dashboard and stats API
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.datetime.now().strftime('%H:%M:%S')

        print(f"Marking attendance for student {student_id} ({name}) on {today} at {current_time}")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if already marked today
        cursor.execute("""
            SELECT * FROM stdattendance
            WHERE std_id = %s AND DATE(std_date) = %s
        """, (student_id, today))

        existing_record = cursor.fetchone()

        if existing_record:
            # Already marked, update time
            cursor.execute("""
                UPDATE stdattendance
                SET std_time = %s, std_attendance = 'Present'
                WHERE std_id = %s AND DATE(std_date) = %s
            """, (current_time, student_id, today))
            print(f"Updated existing attendance record for student {student_id}")
        else:
            # New attendance record
            cursor.execute("""
                INSERT INTO stdattendance (std_id, std_roll_no, std_name, std_time, std_date, std_attendance)
                VALUES (%s, %s, %s, %s, %s, 'Present')
            """, (student_id, roll_no, name, current_time, today))
            print(f"Created new attendance record for student {student_id}")

        conn.commit()
        conn.close()
        print(f"Attendance marked successfully for student {student_id}")

    except Exception as e:
        print(f"Attendance marking error: {e}")
        import traceback
        traceback.print_exc()

@app.route('/api/mark_attendance', methods=['POST'])
@login_required
def api_mark_attendance():
    try:
        data = request.form
        student_id = data.get('student_id')
        roll_no = data.get('roll_no')
        name = data.get('name')

        if not student_id or not roll_no or not name:
            return jsonify({"error": "Missing required fields: student_id, roll_no, name"}), 400

        # Mark attendance
        mark_attendance(student_id, roll_no, name)

        return jsonify({"message": "Attendance marked successfully"})

    except Exception as e:
        print(f"Attendance marking error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/export_attendance/<format>')
@login_required
def api_export_attendance(format):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM stdattendance ORDER BY std_date DESC, std_time DESC")
        records = cursor.fetchall()
        conn.close()

        if format.lower() == 'csv':
            # Create CSV response
            import csv
            import io

            output = io.StringIO()
            writer = csv.writer(output)

            # Write header
            writer.writerow(['ID', 'Student ID', 'Roll No', 'Name', 'Date', 'Time', 'Status'])

            # Write data
            for record in records:
                writer.writerow([
                    record['id'],
                    record['std_id'],
                    record['std_roll_no'],
                    record['std_name'],
                    record['std_date'],
                    record['std_time'],
                    record['std_attendance']
                ])

            output.seek(0)
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=attendance_export.csv'}
            )

        elif format.lower() == 'excel':
            # Create Excel response
            try:
                import pandas as pd
                from io import BytesIO

                # Convert records to DataFrame
                df_data = []
                for record in records:
                    df_data.append({
                        'ID': record['id'],
                        'Student ID': record['std_id'],
                        'Roll No': record['std_roll_no'],
                        'Name': record['std_name'],
                        'Date': record['std_date'],
                        'Time': record['std_time'],
                        'Status': record['std_attendance']
                    })

                df = pd.DataFrame(df_data)

                # Create Excel file
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Attendance', index=False)

                output.seek(0)
                return Response(
                    output.getvalue(),
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    headers={'Content-Disposition': 'attachment; filename=attendance_export.xlsx'}
                )
            except ImportError:
                return jsonify({"error": "Excel export requires pandas and openpyxl. Install with: pip install pandas openpyxl"}), 500

        else:
            return jsonify({"error": "Unsupported format. Use 'csv' or 'excel'"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/attendance_stats')
@login_required
def api_attendance_stats():
    try:
        # Use the same date format and query approach as dashboard
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get today's present count
        cursor.execute("SELECT COUNT(*) FROM stdattendance WHERE DATE(std_date) = %s AND std_attendance = 'Present'", (today,))
        present_result = cursor.fetchone()
        present_today = present_result[0] if present_result else 0

        # Get today's total scans
        cursor.execute("SELECT COUNT(*) FROM stdattendance WHERE DATE(std_date) = %s", (today,))
        total_result = cursor.fetchone()
        total_today = total_result[0] if total_result else 0

        conn.close()

        return jsonify({
            "present_today": present_today,
            "total_today": total_today
        })

    except Exception as e:
        print(f"Attendance stats error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ==================== Model Training API ====================

@app.route('/api/train_model', methods=['POST'])
@login_required
@admin_required
def api_train_model():
    try:
        data_dir = "data_img"
        if not os.path.exists(data_dir):
            return jsonify({"error": "Data directory 'data_img' not found!"}), 400

        path = [os.path.join(data_dir, file) for file in os.listdir(data_dir)]

        if len(path) == 0:
            return jsonify({"error": "No images found in 'data_img'. Please generate dataset first!"}), 400

        faces = []
        ids = []
        id_map = {}  # Map string IDs to integer IDs
        current_int_id = 0

        for image in path:
            img = Image.open(image).convert('L')  # convert in gray scale
            imageNp = np.array(img, 'uint8')
            filename = os.path.split(image)[1]
            parts = filename.split('.')

            if len(parts) >= 3:
                string_id = parts[1]  # Get the student ID part

                # Map string ID to integer ID if not already mapped
                if string_id not in id_map:
                    id_map[string_id] = current_int_id
                    current_int_id += 1

                int_id = id_map[string_id]

                faces.append(imageNp)
                ids.append(int_id)

        if len(faces) == 0:
            return jsonify({"error": "No valid images found for training!"}), 400

        ids = np.array(ids)

        # Save the ID mapping for later use in recognition
        import pickle
        with open("id_mapping.pkl", "wb") as f:
            pickle.dump(id_map, f)

        # Train Classifier
        clf = cv2.face.LBPHFaceRecognizer_create()
        clf.train(faces, ids)
        clf.write("clf.xml")

        return jsonify({
            "message": f"Training Dataset Completed!\nProcessed {len(faces)} images from {len(id_map)} students."
        })

    except Exception as e:
        print(f"Training error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
