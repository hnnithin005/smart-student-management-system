import os

from flask import Flask, render_template

from config import Config
from app.models import Department, Subject, Student, Teacher, User, db


def create_app(config_class=Config):
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder="templates",
        static_folder="static",
    )
    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)
    # Prefer instance folder DB path relative to package parent
    db_path = os.path.join(os.path.dirname(app.root_path), "instance", "ssms.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path

    db.init_app(app)

    from app.auth import auth_bp
    from app.admin import admin_bp
    from app.teacher import teacher_bp
    from app.student import student_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)

    @app.errorhandler(403)
    def forbidden(_error):
        return render_template("error.html", code=403, message="Access denied."), 403

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("error.html", code=404, message="Page not found."), 404

    with app.app_context():
        db.create_all()
        seed_data()

    return app


def seed_data():
    if User.query.filter_by(role="admin").first():
        return

    admin = User(username="admin", role="admin")
    admin.set_password("admin123")
    db.session.add(admin)

    cse = Department(name="Computer Science & Engineering", code="CSE")
    ece = Department(name="Electronics & Communication", code="ECE")
    db.session.add_all([cse, ece])
    db.session.flush()

    t_user = User(username="teacher1", role="teacher")
    t_user.set_password("teacher123")
    db.session.add(t_user)
    db.session.flush()

    teacher = Teacher(
        teacher_code="T001",
        name="Dr. Ananya Rao",
        email="ananya.rao@college.edu",
        department_id=cse.id,
        user_id=t_user.id,
    )
    db.session.add(teacher)
    db.session.flush()

    s_user = User(username="student1", role="student")
    s_user.set_password("student123")
    db.session.add(s_user)
    db.session.flush()

    student = Student(
        student_code="S001",
        name="Rahul Sharma",
        roll_number="1CS21CS001",
        semester=4,
        email="rahul.sharma@college.edu",
        phone="9876543210",
        department_id=cse.id,
        user_id=s_user.id,
    )
    db.session.add(student)

    s2_user = User(username="student2", role="student")
    s2_user.set_password("student123")
    db.session.add(s2_user)
    db.session.flush()

    student2 = Student(
        student_code="S002",
        name="Priya Nair",
        roll_number="1CS21CS002",
        semester=4,
        email="priya.nair@college.edu",
        phone="9876543211",
        department_id=cse.id,
        user_id=s2_user.id,
    )
    db.session.add(student2)

    db.session.add_all(
        [
            Subject(
                code="CS401",
                name="Database Management Systems",
                semester=4,
                department_id=cse.id,
                teacher_id=teacher.id,
            ),
            Subject(
                code="CS402",
                name="Operating Systems",
                semester=4,
                department_id=cse.id,
                teacher_id=teacher.id,
            ),
        ]
    )

    db.session.commit()
