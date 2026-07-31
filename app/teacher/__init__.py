from datetime import date, datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.helpers import current_teacher, role_required
from app.models import Attendance, Student, Subject, db

teacher_bp = Blueprint("teacher", __name__, url_prefix="/teacher")


@teacher_bp.route("/")
@role_required("teacher")
def dashboard():
    teacher = current_teacher()
    subjects = Subject.query.filter_by(teacher_id=teacher.id).order_by(Subject.code).all()
    today_count = (
        Attendance.query.filter_by(marked_by=teacher.id, date=date.today()).count()
        if teacher
        else 0
    )
    return render_template(
        "teacher/dashboard.html",
        teacher=teacher,
        subjects=subjects,
        today_count=today_count,
    )


@teacher_bp.route("/attendance")
@role_required("teacher")
def attendance():
    teacher = current_teacher()
    subjects = Subject.query.filter_by(teacher_id=teacher.id).order_by(Subject.code).all()
    subject_id = request.args.get("subject_id", type=int)
    selected_date = request.args.get("date") or date.today().isoformat()

    try:
        att_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
    except ValueError:
        att_date = date.today()
        selected_date = att_date.isoformat()

    selected_subject = None
    students = []
    existing = {}

    if subject_id:
        selected_subject = Subject.query.filter_by(
            id=subject_id, teacher_id=teacher.id
        ).first()
        if selected_subject:
            students = (
                Student.query.filter_by(
                    department_id=selected_subject.department_id,
                    semester=selected_subject.semester,
                )
                .order_by(Student.roll_number)
                .all()
            )
            records = Attendance.query.filter_by(
                subject_id=selected_subject.id, date=att_date
            ).all()
            existing = {r.student_id: r.status for r in records}

    return render_template(
        "teacher/attendance.html",
        teacher=teacher,
        subjects=subjects,
        selected_subject=selected_subject,
        students=students,
        existing=existing,
        selected_date=selected_date,
    )


@teacher_bp.route("/attendance/save", methods=["POST"])
@role_required("teacher")
def save_attendance():
    teacher = current_teacher()
    subject_id = request.form.get("subject_id", type=int)
    selected_date = request.form.get("date") or date.today().isoformat()

    subject = Subject.query.filter_by(id=subject_id, teacher_id=teacher.id).first()
    if not subject:
        flash("Invalid subject.", "error")
        return redirect(url_for("teacher.attendance"))

    try:
        att_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
    except ValueError:
        flash("Invalid date.", "error")
        return redirect(url_for("teacher.attendance", subject_id=subject_id))

    students = Student.query.filter_by(
        department_id=subject.department_id, semester=subject.semester
    ).all()

    for student in students:
        status = request.form.get(f"status_{student.id}", "absent")
        if status not in ("present", "absent"):
            status = "absent"

        record = Attendance.query.filter_by(
            student_id=student.id, subject_id=subject.id, date=att_date
        ).first()
        if record:
            record.status = status
            record.marked_by = teacher.id
        else:
            db.session.add(
                Attendance(
                    student_id=student.id,
                    subject_id=subject.id,
                    date=att_date,
                    status=status,
                    marked_by=teacher.id,
                )
            )

    db.session.commit()
    flash(f"Attendance saved for {subject.code} on {att_date.isoformat()}.", "success")
    return redirect(
        url_for("teacher.attendance", subject_id=subject.id, date=att_date.isoformat())
    )


@teacher_bp.route("/attendance/records")
@role_required("teacher")
def attendance_records():
    teacher = current_teacher()
    subjects = Subject.query.filter_by(teacher_id=teacher.id).order_by(Subject.code).all()
    subject_id = request.args.get("subject_id", type=int)

    records = []
    selected_subject = None
    if subject_id:
        selected_subject = Subject.query.filter_by(
            id=subject_id, teacher_id=teacher.id
        ).first()
        if selected_subject:
            records = (
                Attendance.query.filter_by(subject_id=selected_subject.id)
                .order_by(Attendance.date.desc(), Attendance.id.desc())
                .limit(200)
                .all()
            )

    return render_template(
        "teacher/attendance_records.html",
        subjects=subjects,
        selected_subject=selected_subject,
        records=records,
    )
