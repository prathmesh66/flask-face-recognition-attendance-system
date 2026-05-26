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

'''
# Public Showcase Version
# Certain sensitive/internal implementation details have been intentionally omitted for security and project protection purposes.
'''

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


'''
# Public Showcase Version
# Certain sensitive/internal implementation details have been intentionally omitted for security and project protection purposes.
'''
