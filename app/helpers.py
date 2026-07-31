from functools import wraps

from flask import abort, redirect, session, url_for

from app.models import Student, Teacher, User


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("auth.login"))
            if session.get("role") not in roles:
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


def current_teacher():
    user = current_user()
    if not user or user.role != "teacher":
        return None
    return Teacher.query.filter_by(user_id=user.id).first()


def current_student():
    user = current_user()
    if not user or user.role != "student":
        return None
    return Student.query.filter_by(user_id=user.id).first()
