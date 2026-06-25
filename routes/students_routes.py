from flask import *
from models import *
from db import db
from flask_bcrypt import Bcrypt
from utils.auth import login_required
from datetime import datetime
import re
student_bp = Blueprint("student", __name__)

bcrypt = Bcrypt()


# student register
@student_bp.route("/student-register", methods=["POST", "GET"])
def student_register():
    if request.method == "POST":
        try:
            form_stu_name = request.form.get("stu_name", "").strip()
            form_stu_age = datetime.strptime(request.form.get("stu_age", ""), "%Y-%m-%d").date()
            form_stu_email = request.form.get("stu_email", "").strip()
            raw_phone = request.form.get("stu_phone", "").strip()
            digits_only = re.sub(r"\D", "", raw_phone)
            form_stu_phone = digits_only[-10:]
            form_stu_address = request.form.get("stu_address", "").strip()
            form_stu_password = request.form.get("stu_password", "")

            # Validation checks
            if not all([form_stu_name, form_stu_age, form_stu_email, form_stu_phone, form_stu_password]):
                flash("❌ All fields are required. Please fill in all information.", "error")
                return render_template("students/register-student.html")

            # Check if email already exists
            existing_student = Student.query.filter_by(stu_email=form_stu_email).first()
            if existing_student:
                flash("⚠️ A student with this email already exists. Please use a different email.", "error")
                return render_template("students/register-student.html")

            # Check if phone already exists

            # Password strength minimum length
            if len(form_stu_password) < 6:
                flash("🔒 Password must be at least 6 characters long.", "error")
                return render_template("students/register-student.html")

            hashed_password = bcrypt.generate_password_hash(form_stu_password).decode("utf-8")

            stu_data = Student(
                stu_name=form_stu_name,
                stu_age=form_stu_age,
                stu_email=form_stu_email,
                stu_phone=form_stu_phone,
                stu_address=form_stu_address,
                stu_password=hashed_password,
                role="student"
            )
            db.session.add(stu_data)
            db.session.commit()
            flash(f"✅ Student '{form_stu_name}' has been successfully registered!", "success")
            return redirect(url_for("student.all_students_data"))

        except Exception as e:
            db.session.rollback()
            flash(f"❌ An unexpected error occurred: {str(e)}", "error")
            return render_template("students/register-student.html")

    else:
        return render_template("students/register-student.html")


@student_bp.route("/all-student")
@login_required
def all_students_data():
    try:
        get_students = Student.query.all()  # select * from student
        if not get_students:
            flash("ℹ️ No students found in the database. Add your first student!", "info")
        return render_template("students/all_students.html", students=get_students)
    except Exception as e:
        flash(f"❌ Error loading students: {str(e)}", "error")
        return render_template("students/all_students.html", students=[])


@student_bp.route("/student-details/<int:id>")
@login_required
def students_details(id):
    try:
        get_stu = Student.query.get(id)
        if not get_stu:
            flash("❌ Student not found. The student may have been deleted.", "error")
            return redirect(url_for("student.all_students_data"))
        return render_template("students/student-details.html", student=get_stu)
    except Exception as e:
        flash(f"❌ Error loading student details: {str(e)}", "error")
        return redirect(url_for("student.all_students_data"))


@student_bp.route("/student-delete/<int:id>")
@login_required
def students_delete(id):
    try:
        student = Student.query.get_or_404(id)
        student_name = student.stu_name
        db.session.delete(student)
        db.session.commit()
        flash(f"🗑️ Student '{student_name}' has been permanently deleted from the system.", "success")
        return redirect(url_for("student.all_students_data"))
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Cannot delete student: {str(e)}", "error")
        return redirect(url_for("student.all_students_data"))


@student_bp.route("/student-update/<int:id>", methods=["GET", "POST"])
@login_required
def students_update(id):
    try:
        student = Student.query.get_or_404(id)

        if request.method == "POST":
            try:
                new_name = request.form.get("stu_name", "").strip()
                new_age = request.form.get("stu_age", "")
                new_email = request.form.get("stu_email", "").strip()
                new_phone = request.form.get("stu_phone", "").strip()
                new_address = request.form.get("stu_address", "").strip()
                new_password = request.form.get("stu_password", "").strip()

                # Validation
                if not all([new_name, new_age, new_email, new_phone]):
                    flash("❌ Name, Age, Email, and Phone are required fields.", "error")
                    return render_template("students/update-student.html", student=student)

                # Check if email is taken by another student
                email_exists = Student.query.filter(Student.stu_email == new_email, Student.id != id).first()
                if email_exists:
                    flash("⚠️ Another student is already using this email. Please use a different email.", "error")
                    return render_template("students/update-student.html", student=student)

                # Check if phone is taken by another student
                phone_exists = Student.query.filter(Student.stu_phone == new_phone, Student.id != id).first()
                if phone_exists:
                    flash("⚠️ This mobile number is already registered to another student.", "error")
                    return render_template("students/update-student.html", student=student)

                # Update fields
                student.stu_name = new_name
                student.stu_age = datetime.strptime(new_age, "%Y-%m-%d").date()
                student.stu_email = new_email
                student.stu_phone = new_phone
                student.stu_address = new_address

                # Update password only if provided
                if new_password:
                    if len(new_password) < 6:
                        flash("🔒 Password must be at least 6 characters if you want to change it.", "error")
                        return render_template("students/update-student.html", student=student)
                    student.stu_password = bcrypt.generate_password_hash(new_password).decode("utf-8")
                    flash("🔐 Password has been updated.", "success")

                db.session.commit()
                flash(f"✅ Student '{new_name}' details have been successfully updated!", "success")
                return redirect(url_for("student.students_details", id=student.id))

            except Exception as e:
                db.session.rollback()
                flash(f"❌ Update failed: {str(e)}", "error")
                return render_template("students/update-student.html", student=student)

        return render_template("students/update-student.html", student=student)

    except Exception as e:
        flash(f"❌ Student not found or error occurred: {str(e)}", "error")
        return redirect(url_for("student.all_students_data"))