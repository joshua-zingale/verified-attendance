from flask import Flask, render_template, request, redirect, url_for, flash, make_response
import random
import string
import csv
from io import StringIO
from datetime import datetime
from tinydb import TinyDB, Query

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here' # CHANGE THIS TO A STRONG, RANDOM KEY!

# Initialize TinyDB databases
# They will create 'codes_db.json' and 'attendance_db.json' files in your project directory
codes_db = TinyDB('codes_db.json')
attendance_db = TinyDB('attendance_db.json')

# We still need a global flag for attendance_open as it's a transient state
# You could store this in the DB too, but for simplicity here, we keep it in memory
# If your server restarts, attendance will default to closed.
attendance_open = False

@app.route('/')
def index():
    return redirect(url_for('student_page'))

@app.route('/instructor', methods=['GET', 'POST'])
def instructor_page():
    global attendance_open

    if request.method == 'POST':
        if 'start_attendance' in request.form:
            attendance_open = True
            flash('Attendance taking has started!', 'success')
        elif 'end_attendance' in request.form:
            attendance_open = False
            flash('Attendance taking has ended!', 'info')
        elif 'generate_codes' in request.form:
            num_codes = int(request.form.get('num_codes', 1))
            code_length = int(request.form.get('code_length', 6))
            generated_codes_count = 0
            for _ in range(num_codes):
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=code_length))
                # Ensure code is unique before inserting
                Code = Query()
                if not codes_db.search(Code.code == code):
                    codes_db.insert({'code': code, 'used': False})
                    generated_codes_count += 1
            flash(f'{generated_codes_count} new codes generated and added!', 'success')
        elif 'clear_codes' in request.form:
            codes_db.truncate() # Clears all codes
            flash('All codes cleared!', 'danger')
        elif 'clear_all_attendance' in request.form:
            attendance_db.truncate() # Clears all attendance records
            codes_db.truncate()      # Clears all codes
            attendance_open = False  # Reset attendance status
            flash('All attendance records, codes, and status reset!', 'danger')

    # Fetch current codes from DB for display
    current_codes_list = [d['code'] for d in codes_db.all()]
    current_codes_list.sort() # Sort for consistent display

    # Count submitted attendance for display
    submitted_attendance_count = len(attendance_db.all())

    return render_template('instructor.html',
                           attendance_open=attendance_open,
                           codes=current_codes_list,
                           submitted_attendance_count=submitted_attendance_count)

@app.route('/student', methods=['GET', 'POST'])
def student_page():
    global attendance_open

    message = None
    message_type = None
    Code = Query()
    Student = Query()

    if request.method == 'POST':
        if not attendance_open:
            message = "Attendance is not currently being taken."
            message_type = "danger"
        else:
            student_email = request.form['student_email'].strip().lower()
            student_id = request.form['student_id'].strip()
            first_name = request.form['first_name'].strip()
            last_name = request.form['last_name'].strip()
            submitted_code = request.form['code'].strip().upper()

            if not all([student_email, student_id, first_name, last_name, submitted_code]):
                message = "All fields are required."
                message_type = "danger"
            else:
                # Check if the code exists and is not used
                code_record = codes_db.search(Code.code == submitted_code)

                if not code_record:
                    message = "Invalid code. Please ensure you entered it correctly."
                    message_type = "danger"
                elif code_record[0]['used']: # Check if the code has been marked as used
                    message = "This code has already been used. Please get a new code."
                    message_type = "danger"
                else:
                    # Check if this student_id has already submitted with any code for this session
                    # For a truly unique submission per session per student, you might want a more complex check
                    # E.g., student_id AND timestamp within attendance_open period
                    # For now, we'll focus on the code being unique.
                    
                    # Prevent multiple submissions by the same student_id AND submitted_code
                    existing_submission = attendance_db.search(
                        (Student.student_id == student_id) &
                        (Student.code == submitted_code)
                    )

                    if existing_submission:
                        message = "You have already submitted attendance with this code."
                        message_type = "info"
                    else:
                        # Mark the code as used in the codes_db
                        codes_db.update({'used': True}, Code.code == submitted_code)

                        # Store attendance record
                        attendance_db.insert({
                            'email': student_email,
                            'student_id': student_id,
                            'first_name': first_name,
                            'last_name': last_name,
                            'code': submitted_code,
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                        message = "Attendance submitted successfully!"
                        message_type = "success"

    return render_template('student.html', attendance_open=attendance_open, message=message, message_type=message_type)

@app.route('/download_attendance')
def download_attendance():
    si = StringIO()
    cw = csv.writer(si)

    # Write header
    cw.writerow(['Timestamp', 'Student Email', 'Student ID', 'First Name', 'Last Name', 'Code Used'])

    # Write data from attendance_db
    for record in attendance_db.all():
        cw.writerow([
            record.get('timestamp', ''), # Use .get() for safety if a field might be missing
            record.get('email', ''),
            record.get('student_id', ''),
            record.get('first_name', ''),
            record.get('last_name', ''),
            record.get('code', '')
        ])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=attendance_records.csv"
    output.headers["Content-type"] = "text/csv"
    return output

if __name__ == '__main__':
    app.run(debug=True)