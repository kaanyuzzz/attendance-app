from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# -------------------------------
# 🧱 Object-Oriented Base Classes
# -------------------------------

class Person:
    def __init__(self, name, id):
        self.name = name
        self.id = id

    def get_info(self):
        return f"{self.name} (ID: {self.id})"

    def perform_role(self):
        return "Generic person in the system."

class Student(Person):
    def __init__(self, name, student_id, email, status):
        super().__init__(name, student_id)
        self.email = email
        self.status = status

    def get_info(self):
        return f"Student: {self.name}, ID: {self.id}, Status: {self.status}"

    def perform_role(self):
        return f"{self.name} is attending classes ({self.status})."

class Teacher(Person):
    def __init__(self, name, id, branch):
        super().__init__(name, id)
        self.branch = branch

    def get_info(self):
        return f"Teacher: {self.name}, ID: {self.id}, Branch: {self.branch}"

    def perform_role(self):
        return f"{self.name} is teaching {self.branch}."

# -------------------------------
# 🔄 Attendance Manager
# -------------------------------

class AttendanceManager:
    def __init__(self):
        self.students = []
        self.teacher = Teacher("Marek Rogalski", "T01", "Software Engineering")
        self.load_students()

    def load_students(self):
        data = [
            ("Kaan", "101", "kaan@beylikduzu.edu.tr", "present"),
            ("Sevil", "102", "sevil@beylikduzu.edu.tr", "absent"),
            ("Guven", "103", "guven@beylikduzu.edu.tr", "present"),
            ("Lara", "104", "lara@beylikduzu.edu.tr", "absent"),
            ("Michael", "105", "michael@beylikduzu.edu.tr", "present")
        ]
        for name, sid, email, status in data:
            self.students.append(Student(name, sid, email, status))

    def add_student(self, name, student_id, email, status):
        self.students.append(Student(name, student_id, email, status))

    def student_exists(self, student_id):
        return any(s.id == student_id for s in self.students)

    def email_exists(self, email):
        return any(s.email == email for s in self.students)

    def generate_email(self, name, last_name=None):
        base = name.lower()
        if last_name:
            base += "." + last_name.lower()
        email = f"{base}@beylikduzu.edu.tr"
        count = 1
        unique_email = email
        while self.email_exists(unique_email):
            unique_email = f"{base}{count}@beylikduzu.edu.tr"
            count += 1
        return unique_email

    def get_filtered_students(self, filter_status):
        if filter_status == "present":
            return [s for s in self.students if s.status == "present"]
        elif filter_status == "absent":
            return [s for s in self.students if s.status == "absent"]
        return self.students

    def get_attendance_percentage(self):
        total = len(self.students)
        present = len([s for s in self.students if s.status == "present"])
        return round((present / total) * 100, 2) if total else 0

    def count_same_first_name(self, name):
        return sum(1 for s in self.students if s.name.split()[0].lower() == name.lower())

# -------------------------------
# 🧠 Flask Route
# -------------------------------

attendance_manager = AttendanceManager()

@app.route("/", methods=["GET", "POST"])
def index():
    filter_status = request.args.get("filter", "all")
    students = attendance_manager.get_filtered_students(filter_status)
    percentage = attendance_manager.get_attendance_percentage()
    error = None
    show_last_name = False

    if request.method == "POST":
        name = request.form["name"].strip()
        last_name = request.form.get("last_name", "").strip()
        student_id = request.form["student_id"].strip()
        status = request.form["status"]

        if attendance_manager.student_exists(student_id):
            error = "This student ID already exists."
            show_last_name = attendance_manager.count_same_first_name(name) == 1
            return render_template("index.html", attendance=students,
                                   attendance_percentage=percentage,
                                   current_filter=filter_status,
                                   teacher_info_string=attendance_manager.teacher.get_info(),
                                   error=error, show_last_name=show_last_name,
                                   previous_name=name, previous_student_id=student_id,
                                   previous_status=status)

        if attendance_manager.count_same_first_name(name) == 1 and not last_name:
            error = "Same name exists. Please enter a surname."
            show_last_name = True
            return render_template("index.html", attendance=students,
                                   attendance_percentage=percentage,
                                   current_filter=filter_status,
                                   teacher_info_string=attendance_manager.teacher.get_info(),
                                   error=error, show_last_name=show_last_name,
                                   previous_name=name, previous_student_id=student_id,
                                   previous_status=status)

        email = attendance_manager.generate_email(name, last_name if last_name else None)
        full_name = f"{name} {last_name}" if last_name else name
        attendance_manager.add_student(full_name, student_id, email, status)
        return redirect(f"/?filter={filter_status}")

    return render_template("index.html",
                           attendance=[(s.name, s.id, s.email, s.status) for s in students],
                           attendance_percentage=percentage,
                           current_filter=filter_status,
                           teacher_info_string=attendance_manager.teacher.get_info(),
                           error=error,
                           show_last_name=show_last_name)

# -------------------------------
# 🔌 Replit/GitHub Port Binding
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81)
s
