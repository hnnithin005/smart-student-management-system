from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import or_

from app.helpers import role_required
from app.models import Attendance, Department, Student, Subject, Teacher, User, db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
@role_required("admin")
def dashboard():
    stats = {
        "students": Student.query.count(),
        "teachers": Teacher.query.count(),
        "subjects": Subject.query.count(),
        "departments": Department.query.count(),
        "attendance_today": Attendance.query.filter_by(date=date.today()).count(),
    }
    recent_students = Student.query.order_by(Student.id.desc()).limit(5).all()
    departments = Department.query.order_by(Department.name).all()
    return render_template(
        "admin/dashboard.html",
        stats=stats,
        recent_students=recent_students,
        departments=departments,
    )


# ---- Departments ----
@admin_bp.route("/departments", methods=["GET", "POST"])
@role_required("admin")
def departments():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        code = request.form.get("code", "").strip().upper()
        if not name or not code:
            flash("Department name and code are required.", "error")
        elif Department.query.filter(
            or_(Department.name == name, Department.code == code)
        ).first():
            flash("Department name or code already exists.", "error")
        else:
            db.session.add(Department(name=name, code=code))
            db.session.commit()
            flash("Department added.", "success")
        return redirect(url_for("admin.departments"))

    items = Department.query.order_by(Department.name).all()
    return render_template("admin/departments.html", departments=items)


@admin_bp.route("/departments/<int:dept_id>/delete", methods=["POST"])
@role_required("admin")
def delete_department(dept_id):
    dept = Department.query.get_or_404(dept_id)
    if dept.students or dept.teachers or dept.subjects:
        flash("Cannot delete a department that has linked records.", "error")
    else:
        db.session.delete(dept)
        db.session.commit()
        flash("Department deleted.", "success")
    return redirect(url_for("admin.departments"))


# ---- Students (FR2) ----
@admin_bp.route("/students")
@role_required("admin")
def students():
    q = request.args.get("q", "").strip()
    query = Student.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Student.name.ilike(like),
                Student.student_code.ilike(like),
                Student.roll_number.ilike(like),
                Student.email.ilike(like),
            )
        )
    items = query.order_by(Student.name).all()
    departments = Department.query.order_by(Department.name).all()
    return render_template(
        "admin/students.html", students=items, departments=departments, q=q
    )


@admin_bp.route("/students/add", methods=["POST"])
@role_required("admin")
def add_student():
    student_code = request.form.get("student_code", "").strip()
    name = request.form.get("name", "").strip()
    roll_number = request.form.get("roll_number", "").strip().upper()
    semester = request.form.get("semester", type=int)
    email = request.form.get("email", "").strip().lower()
    phone = request.form.get("phone", "").strip()
    department_id = request.form.get("department_id", type=int)
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip() or "student123"

    if not all([student_code, name, roll_number, semester, email, phone, department_id, username]):
        flash("All student fields are required.", "error")
        return redirect(url_for("admin.students"))

    if User.query.filter_by(username=username).first():
        flash("Username already taken.", "error")
        return redirect(url_for("admin.students"))

    if Student.query.filter(
        or_(
            Student.student_code == student_code,
            Student.roll_number == roll_number,
            Student.email == email,
        )
    ).first():
        flash("Student ID, roll number, or email already exists.", "error")
        return redirect(url_for("admin.students"))

    user = User(username=username, role="student")
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    student = Student(
        student_code=student_code,
        name=name,
        roll_number=roll_number,
        semester=semester,
        email=email,
        phone=phone,
        department_id=department_id,
        user_id=user.id,
    )
    db.session.add(student)
    db.session.commit()
    flash(f"Student {name} added. Login: {username}", "success")
    return redirect(url_for("admin.students"))


@admin_bp.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
@role_required("admin")
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    departments = Department.query.order_by(Department.name).all()

    if request.method == "POST":
        student.name = request.form.get("name", "").strip()
        student.roll_number = request.form.get("roll_number", "").strip().upper()
        student.semester = request.form.get("semester", type=int)
        student.email = request.form.get("email", "").strip().lower()
        student.phone = request.form.get("phone", "").strip()
        student.department_id = request.form.get("department_id", type=int)
        student.student_code = request.form.get("student_code", "").strip()

        if not all(
            [
                student.name,
                student.roll_number,
                student.semester,
                student.email,
                student.phone,
                student.department_id,
                student.student_code,
            ]
        ):
            flash("All fields are required.", "error")
            return redirect(url_for("admin.edit_student", student_id=student.id))

        conflict = Student.query.filter(
            Student.id != student.id,
            or_(
                Student.student_code == student.student_code,
                Student.roll_number == student.roll_number,
                Student.email == student.email,
            ),
        ).first()
        if conflict:
            flash("Student ID, roll number, or email already used by another student.", "error")
            return redirect(url_for("admin.edit_student", student_id=student.id))

        db.session.commit()
        flash("Student updated.", "success")
        return redirect(url_for("admin.students"))

    return render_template(
        "admin/edit_student.html", student=student, departments=departments
    )


@admin_bp.route("/students/<int:student_id>/delete", methods=["POST"])
@role_required("admin")
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    user = student.user
    db.session.delete(student)
    if user:
        db.session.delete(user)
    db.session.commit()
    flash("Student deleted.", "success")
    return redirect(url_for("admin.students"))


# ---- Teachers (FR3) ----
@admin_bp.route("/teachers")
@role_required("admin")
def teachers():
    items = Teacher.query.order_by(Teacher.name).all()
    departments = Department.query.order_by(Department.name).all()
    return render_template("admin/teachers.html", teachers=items, departments=departments)


@admin_bp.route("/teachers/add", methods=["POST"])
@role_required("admin")
def add_teacher():
    teacher_code = request.form.get("teacher_code", "").strip()
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    department_id = request.form.get("department_id", type=int)
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip() or "teacher123"

    if not all([teacher_code, name, email, department_id, username]):
        flash("All teacher fields are required.", "error")
        return redirect(url_for("admin.teachers"))

    if User.query.filter_by(username=username).first():
        flash("Username already taken.", "error")
        return redirect(url_for("admin.teachers"))

    if Teacher.query.filter(
        or_(Teacher.teacher_code == teacher_code, Teacher.email == email)
    ).first():
        flash("Teacher ID or email already exists.", "error")
        return redirect(url_for("admin.teachers"))

    user = User(username=username, role="teacher")
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    teacher = Teacher(
        teacher_code=teacher_code,
        name=name,
        email=email,
        department_id=department_id,
        user_id=user.id,
    )
    db.session.add(teacher)
    db.session.commit()
    flash(f"Teacher {name} added. Login: {username}", "success")
    return redirect(url_for("admin.teachers"))


@admin_bp.route("/teachers/<int:teacher_id>/edit", methods=["GET", "POST"])
@role_required("admin")
def edit_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    departments = Department.query.order_by(Department.name).all()

    if request.method == "POST":
        teacher.teacher_code = request.form.get("teacher_code", "").strip()
        teacher.name = request.form.get("name", "").strip()
        teacher.email = request.form.get("email", "").strip().lower()
        teacher.department_id = request.form.get("department_id", type=int)

        if not all([teacher.teacher_code, teacher.name, teacher.email, teacher.department_id]):
            flash("All fields are required.", "error")
            return redirect(url_for("admin.edit_teacher", teacher_id=teacher.id))

        conflict = Teacher.query.filter(
            Teacher.id != teacher.id,
            or_(Teacher.teacher_code == teacher.teacher_code, Teacher.email == teacher.email),
        ).first()
        if conflict:
            flash("Teacher ID or email already used by another teacher.", "error")
            return redirect(url_for("admin.edit_teacher", teacher_id=teacher.id))

        db.session.commit()
        flash("Teacher updated.", "success")
        return redirect(url_for("admin.teachers"))

    return render_template(
        "admin/edit_teacher.html", teacher=teacher, departments=departments
    )


@admin_bp.route("/teachers/<int:teacher_id>/delete", methods=["POST"])
@role_required("admin")
def delete_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    for subject in teacher.subjects:
        subject.teacher_id = None
    user = teacher.user
    db.session.delete(teacher)
    if user:
        db.session.delete(user)
    db.session.commit()
    flash("Teacher deleted.", "success")
    return redirect(url_for("admin.teachers"))


# ---- Subjects (FR4) ----
@admin_bp.route("/subjects")
@role_required("admin")
def subjects():
    items = Subject.query.order_by(Subject.code).all()
    departments = Department.query.order_by(Department.name).all()
    teachers = Teacher.query.order_by(Teacher.name).all()
    return render_template(
        "admin/subjects.html",
        subjects=items,
        departments=departments,
        teachers=teachers,
    )


@admin_bp.route("/subjects/add", methods=["POST"])
@role_required("admin")
def add_subject():
    code = request.form.get("code", "").strip().upper()
    name = request.form.get("name", "").strip()
    semester = request.form.get("semester", type=int)
    department_id = request.form.get("department_id", type=int)
    teacher_id = request.form.get("teacher_id", type=int) or None

    if not all([code, name, semester, department_id]):
        flash("Subject code, name, semester, and department are required.", "error")
        return redirect(url_for("admin.subjects"))

    if Subject.query.filter_by(code=code).first():
        flash("Subject code already exists.", "error")
        return redirect(url_for("admin.subjects"))

    db.session.add(
        Subject(
            code=code,
            name=name,
            semester=semester,
            department_id=department_id,
            teacher_id=teacher_id,
        )
    )
    db.session.commit()
    flash("Subject added.", "success")
    return redirect(url_for("admin.subjects"))


@admin_bp.route("/subjects/<int:subject_id>/edit", methods=["GET", "POST"])
@role_required("admin")
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    departments = Department.query.order_by(Department.name).all()
    teachers = Teacher.query.order_by(Teacher.name).all()

    if request.method == "POST":
        subject.code = request.form.get("code", "").strip().upper()
        subject.name = request.form.get("name", "").strip()
        subject.semester = request.form.get("semester", type=int)
        subject.department_id = request.form.get("department_id", type=int)
        subject.teacher_id = request.form.get("teacher_id", type=int) or None

        if not all([subject.code, subject.name, subject.semester, subject.department_id]):
            flash("All required fields must be filled.", "error")
            return redirect(url_for("admin.edit_subject", subject_id=subject.id))

        conflict = Subject.query.filter(
            Subject.id != subject.id, Subject.code == subject.code
        ).first()
        if conflict:
            flash("Subject code already exists.", "error")
            return redirect(url_for("admin.edit_subject", subject_id=subject.id))

        db.session.commit()
        flash("Subject updated.", "success")
        return redirect(url_for("admin.subjects"))

    return render_template(
        "admin/edit_subject.html",
        subject=subject,
        departments=departments,
        teachers=teachers,
    )


@admin_bp.route("/subjects/<int:subject_id>/delete", methods=["POST"])
@role_required("admin")
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash("Subject deleted.", "success")
    return redirect(url_for("admin.subjects"))
