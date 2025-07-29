from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    make_response,
    current_app,
    session,
)
import random
import string
import csv
from io import StringIO
import time
from tinydb import Query
from flask import Blueprint

from .db import get_codes_db, get_attendance_db

bp = Blueprint("routes", __name__)

attendance_open = False


@bp.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == current_app.config["ADMIN_PASSWORD"]:
            session["logged_in"] = True
            flash("Logged in successfully!", "success")
            return redirect(url_for("routes.admin_page"))
        else:
            flash("Invalid password!", "danger")
    return render_template("admin_login.html")


@bp.route("/admin_logout")
def admin_logout():
    session.pop("logged_in", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("routes.admin_login"))


@bp.route("/admin", methods=["GET", "POST"])
def admin_page():
    global attendance_open

    codes_db = get_codes_db()
    attendance_db = get_attendance_db()

    if not session.get("logged_in"):
        return redirect(url_for("routes.admin_login"))

    if request.method == "POST":
        if "start_attendance" in request.form:
            attendance_open = True
            flash("Attendance taking has started!", "success")
        elif "end_attendance" in request.form:
            attendance_open = False
            flash("Attendance taking has ended!", "info")
        elif "generate_codes" in request.form:
            num_codes = int(request.form.get("num_codes", 1))
            code_length = int(request.form.get("code_length", 6))
            generated_codes_count = 0
            for _ in range(num_codes):
                code = "".join(
                    random.choices(
                        string.ascii_uppercase + string.digits, k=code_length
                    )
                )
                Code = Query()
                if not codes_db.search(Code.code == code):
                    codes_db.insert(
                        {"code": code, "used": False, "timestamp": time.time()}
                    )
                    generated_codes_count += 1
            flash(f"{generated_codes_count} new codes generated and added!", "success")
        elif "clear_codes" in request.form:
            codes_db.truncate()
            flash("All codes cleared!", "danger")
        elif "clear_all_attendance" in request.form:
            attendance_db.truncate()
            codes_db.truncate()
            attendance_open = False
            flash("All attendance records, codes, and status reset!", "danger")

        return redirect(url_for("routes.admin_page"))

    codes_list = codes_db.all()
    codes_list.sort(key=lambda x: x["timestamp"])

    attendance_list = attendance_db.all()
    attendance_list.sort(key=lambda x: x["first_name"])
    attendance_list.sort(key=lambda x: x["last_name"])

    return render_template(
        "admin.html",
        attendance_open=attendance_open,
        codes=codes_list,
        attendees=attendance_list,
        num_attendees=len(attendance_list),
    )


@bp.route("/", methods=["GET", "POST"])
def student_page():
    global attendance_open

    codes_db = get_codes_db()
    attendance_db = get_attendance_db()

    message = None
    message_type = None
    Code = Query()
    Student = Query()

    form_data = {
        "student_email": "",
        "student_id": "",
        "first_name": "",
        "last_name": "",
        "code": "",
    }

    if request.method == "POST":
        form_data["student_email"] = request.form["student_email"].strip().lower()
        form_data["student_id"] = request.form["student_id"].strip()
        form_data["first_name"] = request.form["first_name"].strip()
        form_data["last_name"] = request.form["last_name"].strip()
        form_data["code"] = request.form["code"].strip().upper()

        if not attendance_open:
            message = "Attendance is not currently being taken."
            message_type = "danger"
        else:
            student_email = request.form["student_email"].strip().lower()
            student_id = request.form["student_id"].strip()
            first_name = request.form["first_name"].strip()
            last_name = request.form["last_name"].strip()
            submitted_code = request.form["code"].strip().upper()

            if not all(
                [student_email, student_id, first_name, last_name, submitted_code]
            ):
                message = "All fields are required."
                message_type = "danger"
            else:
                # Check if the code exists and is not used
                code_record = codes_db.search(Code.code == submitted_code)

                if attendance_db.search(Student.student_id == student_id):
                    message = "The student with this ID has already been recorded."
                    message_type = "info"
                elif not code_record:
                    message = "Invalid code. Please ensure you entered it correctly."
                    message_type = "danger"
                elif code_record[0]["used"]:
                    message = "This code has already been used. Please get a new code."
                    message_type = "danger"
                else:
                    codes_db.update({"used": True}, Code.code == submitted_code)
                    attendance_db.insert(
                        {
                            "email": student_email,
                            "student_id": student_id,
                            "first_name": first_name,
                            "last_name": last_name,
                            "timestamp": time.time(),
                        }
                    )
                    message = f"Attendance submitted successfully for {student_email} with ID {student_id}!"
                    message_type = "success"

    return render_template(
        "student.html",
        attendance_open=attendance_open,
        message=message,
        message_type=message_type,
        form_data=form_data,
    )


@bp.route("/download_attendance")
def download_attendance():
    attendance_db = get_attendance_db()

    si = StringIO()
    cw = csv.writer(si)

    cw.writerow(["Timestamp", "Student Email", "Student ID", "First Name", "Last Name"])

    for record in attendance_db.all():
        cw.writerow(
            [
                record.get("timestamp", ""),
                record.get("email", ""),
                record.get("student_id", ""),
                record.get("first_name", ""),
                record.get("last_name", ""),
            ]
        )

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = (
        "attachment; filename=attendance_records.csv"
    )
    output.headers["Content-type"] = "text/csv"
    return output
