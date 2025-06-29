from flask import Flask, render_template, request, redirect

app = Flask(__name__)

class Person:
    def __init__(self, name, id):
        self.name = name
        self.id = id

class Student(Person):
    def __init__(self, name, student_id, email, status):
        super().__init__(name, student_id)
        self.email = email
        self.status = status

class Teacher(Person):
    def __init__(self, name, id, branch):
        super().__init__(name, id)
        self.branch = branch

class AttendanceManager:
    def __init__(self):
        self.students = []
        self.teacher = Teacher("Marek Rogalski", "T01", "Software Engineering")
        self.load_initial_data()

    def load_initial_data(self):
        initial_data = [
            ("Kaan", "101", "kaan@beylikduzu.edu.tr", "present"),
            ("Sevil", "102", "sevil@beylikduzu.edu.tr", "absent"),
            ("Guven", "103", "guven@beylikduzu.edu.tr", "present"),
            ("Sudenaz", "104", "sudenaz@beylikduzu.edu.tr", "absent"),
            ("Michael", "105", "michael@beylikduzu.edu.tr", "present"),
            ("Laura", "106", "laura@beylikduzu.edu.tr", "present"),
            ("Osimhen", "107", "osimhen@beylikduzu.edu.tr", "absent"),
            ("Arda", "108", "arda@beylikduzu.edu.tr", "present"),
            ("Mauro", "109", "mauro@beylikduzu.edu.tr", "absent"),
            ("Hakan", "110", "hakan@beylikduzu.edu.tr", "present"),
            ("Kataryna", "111", "kataryna@beylikduzu.edu.tr", "absent"),
            ("Satilmis", "112", "satilmis@beylikduzu.edu.tr", "present"),
            ("Pelin", "113", "pelin@beylikduzu.edu.tr", "present"),
            ("Lara", "114", "lara@beylikduzu.edu.tr", "absent"),
            ("Ilia", "115", "ilia@beylikduzu.edu.tr", "present"),
            ("Khabib", "116", "khabib@beylikduzu.edu.tr", "absent"),
            ("Achiva", "117", "achiva@beylikduzu.edu.tr", "present"),
            ("Muslera", "118", "muslera@beylikduzu.edu.tr", "absent"),
            ("Grosicki", "119", "grosicki@beylikduzu.edu.tr", "present"),
            ("Robert", "120", "robert@beylikduzu.edu.tr", "absent"),
            ("Mira", "121", "mira@beylikduzu.edu.tr", "present"),
            ("Gabriel", "122", "gabriel@beylikduzu.edu.tr", "present"),
            ("Arman", "123", "arman@beylikduzu.edu.tr", "absent")
        ]
        for name, sid, email, status in initial_data:
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
        return round((present / total) * 100, 2) if total > 0 else 0

    def count_same_first_name(self, name):
        return sum(1 for s in self.students if s.name.split()[0].lower() == name.lower())

attendance_manager = AttendanceManager()

@app.route("/", methods=["GET", "POST"])
def index():
    filter_status = request.args.get("filter", "all")
    filtered_students = attendance_manager.get_filtered_students(filter_status)
    attendance_percentage = attendance_manager.get_attendance_percentage()
    error = None
    show_last_name = False

    if request.method == "POST":
        name = request.form["name"].strip()
        last_name = request.form.get("last_name", "").strip()
        student_id = request.form["student_id"].strip()
        status = request.form["status"]

        if attendance_manager.student_exists(student_id):
            error = "This student ID already exists. Please enter a unique ID."
            show_last_name = True if attendance_manager.count_same_first_name(name) == 1 else False
            return render_template("index.html", attendance=filtered_students,
                                   attendance_percentage=attendance_percentage,
                                   current_filter=filter_status,
                                   teacher_info=(attendance_manager.teacher.name,
                                                 attendance_manager.teacher.id,
                                                 attendance_manager.teacher.branch),
                                   error=error,
                                   show_last_name=show_last_name,
                                   previous_name=name,
                                   previous_student_id=student_id,
                                   previous_status=status)

        same_name_count = attendance_manager.count_same_first_name(name)
        if same_name_count == 1 and last_name == "":
            error = "This name already exists. Please enter the surname."
            show_last_name = True
            return render_template("index.html", attendance=filtered_students,
                                   attendance_percentage=attendance_percentage,
                                   current_filter=filter_status,
                                   teacher_info=(attendance_manager.teacher.name,
                                                 attendance_manager.teacher.id,
                                                 attendance_manager.teacher.branch),
                                   error=error,
                                   show_last_name=show_last_name,
                                   previous_name=name,
                                   previous_student_id=student_id,
                                   previous_status=status)

        email = attendance_manager.generate_email(name, last_name if last_name else None)
        full_name = f"{name} {last_name}" if last_name else name
        attendance_manager.add_student(full_name, student_id, email, status)
        return redirect(f"/?filter={filter_status}")

    return render_template("index.html", attendance=[
                               (s.name, s.id, s.email, s.status) for s in filtered_students
                           ],
                           attendance_percentage=attendance_percentage,
                           current_filter=filter_status,
                           teacher_info=(attendance_manager.teacher.name,
                                         attendance_manager.teacher.id,
                                         attendance_manager.teacher.branch),
                           error=error,
                           show_last_name=show_last_name)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81)
