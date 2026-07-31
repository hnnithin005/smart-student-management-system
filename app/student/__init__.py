from collections import defaultdict

from flask import Blueprint, render_template

from app.helpers import current_student, role_required
from app.models import Attendance, Subject

student_bp = Blueprint("student", __name__, url_prefix="/student")


@student_bp.route("/")
@role_required("student")
def dashboard():
    student = current_student()
    subjects = Subject.query.filter_by(
        department_id=student.department_id, semester=student.semester
    ).order_by(Subject.code).all()

    summary = []
    for subject in subjects:
        records = Attendance.query.filter_by(
            student_id=student.id, subject_id=subject.id
        ).all()
        total = len(records)
        present = sum(1 for r in records if r.status == "present")
        pct = round((present / total) * 100, 1) if total else None
        summary.append(
            {
                "subject": subject,
                "total": total,
                "present": present,
                "absent": total - present,
                "percentage": pct,
            }
        )

    return render_template(
        "student/dashboard.html", student=student, summary=summary
    )


@student_bp.route("/attendance")
@role_required("student")
def attendance():
    student = current_student()
    records = (
        Attendance.query.filter_by(student_id=student.id)
        .order_by(Attendance.date.desc())
        .all()
    )

    by_subject = defaultdict(list)
    for record in records:
        by_subject[record.subject].append(record)

    subject_stats = []
    for subject, items in by_subject.items():
        total = len(items)
        present = sum(1 for r in items if r.status == "present")
        subject_stats.append(
            {
                "subject": subject,
                "records": items,
                "total": total,
                "present": present,
                "percentage": round((present / total) * 100, 1) if total else 0,
            }
        )

    subject_stats.sort(key=lambda x: x["subject"].code)
    return render_template(
        "student/attendance.html",
        student=student,
        subject_stats=subject_stats,
        all_records=records,
    )


@student_bp.route("/profile")
@role_required("student")
def profile():
    student = current_student()
    return render_template("student/profile.html", student=student)
