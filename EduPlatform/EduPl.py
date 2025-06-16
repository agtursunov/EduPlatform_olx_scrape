from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime

class Role(Enum):
    ADMIN = 'Admin'
    TEACHER = 'Teacher'
    STUDENT = 'Student'
    PARENT = 'Parent'

class AbstractRole(ABC):
    def __init__(self, _id, full_name, _email, _password_hash):
        self._id = _id
        self.full_name = full_name
        self._email = _email
        self._password_hash = _password_hash
        self._created_at = datetime.now().isoformat()

    @abstractmethod
    def get_profile(self):
        pass

    @abstractmethod
    def update_profile(self, full_name=None, email=None, password_hash=None):
        pass

class User(AbstractRole):
    def __init__(self, _id, full_name, email, password_hash, role: Role):
        super().__init__(_id, full_name, email, password_hash)
        self.role = role
        self._notifications = []

    def add_notification(self, message, recipient_id, user_list):
        new_notification = Notification(
            id=len(self._notifications) + 1,
            message=message,
            sender_id=self._id,
            recipient_id=recipient_id
        )
        self._notifications.append(new_notification)
        new_notification.send(user_list)

    def view_notifications(self, only_unread=False):
        if only_unread:
            notifications_to_view = [n for n in self._notifications if not n.is_read]
        else:
            notifications_to_view = self._notifications
        for notification in notifications_to_view:
            notification.mark_as_read(notification.recipient_id)
            print(f"Xabar: {notification.message} (ID: {notification.id}), yuboruvchi: {notification.sender_id}")

    def delete_notification(self, id):
        if 0 <= id < len(self._notifications):
            del self._notifications[id]
            print(f"Xabar o'chirildi: ID {id}")

    def get_profile(self):
        return {
            "id": self._id,
            "name": self._full_name,
            "email": self._email,
            "role": self.role.value
        }

    def update_profile(self, full_name=None, email=None, password_hash=None):
        if full_name:
            self._full_name = full_name
        if email:
            self._email = email
        if password_hash:
            self._password_hash = password_hash

class Notification:
    def __init__(self, id, message, sender_id, recipient_id, created_at=None,  is_read=False):
        self.id = id
        self.message = message
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        if created_at:
            self.created_at = created_at
        else:
            self.created_at = datetime.now().isoformat()
        self.is_read = False

    def send(self, user_list):
        for user in user_list:
            if user._id == self.recipient_id:
                user._notifications.append(self)
                print(f"'{self.message}'- xabar {user.full_name} ga yuborildi")

    def mark_as_read(self, recipient_id):
        print(f"Xabar o'qilgan deb belgilandi: ID {self.id}, yuboruvchi: {self.sender_id}, qabul qiluvchi: {recipient_id}")
        if recipient_id == self.recipient_id:
            self.is_read = True
            print(f"Xabar o'qilgan deb belgilandi: ID {self.id}")

class Assignment:
    def __init__(self, id, title, description, deadline, subject, teacher_id, class_id):
        self.id = id
        self.title = title
        self.description = description
        self.deadline = deadline
        self.subject = subject
        self.teacher_id = teacher_id
        self.class_id = class_id
        self.submissions = {}  # {student_id: content}
        self.grades = {}       # {student_id: grade}

    def add_submission(self, student_id, content):
        self.submissions[student_id] = content
        print(f"O'quvchi {student_id} vazifa topshirdi.")

    def set_grade(self, student_id, grade):
        self.grades[student_id] = grade
        print(f"O'quvchi {student_id} ga baho qo'yildi: {grade}")

    def get_status(self):
        return {
            "id": self.id,
            "title": self.title,
            "deadline": self.deadline,
            "submitted": list(self.submissions.keys()),
            "graded": list(self.grades.keys())
        }

class Student(User):
    def __init__(self, _id, full_name, email, password_hash, grade):
        super().__init__(_id, full_name, email, password_hash, Role.STUDENT)
        self.grade = grade
        self.subjects = {}  # {subject: teacher_id}
        self.assignments = {}  # {assignment_id: status}
        self.grades = {}  # {subject: [grades]}

    def submit_assignment(self, assignment: Assignment, content):
        assignment.add_submission(self._id, content)
        self.assignments[assignment.id] = "Topshirdi"

    def view_grades(self, subject=None):
        if subject:
            return self.grades.get(subject, [])
        return self.grades

    def calculate_average_grade(self):
        total, count = 0, 0
        for grades in self.grades.values():
            total += sum(grades)
            count += len(grades)
        return total / count if count else 0

class Grade:
    def __init__(self, id, student_id, subject, value, date, teacher_id):
        self.id = id
        self.student_id = student_id
        self.subject = subject
        self.value = value
        self.date = date  # ISO format
        self.teacher_id = teacher_id

    def update_grade(self, value):
        self.value = value
        print(f"Baho yangilandi: {self.value}")

    def get_grade_info(self):
        return {
            "grade_id": self.id,
            "student_id": self.student_id,
            "subject": self.subject,
            "value": self.value,
            "date": self.date,
            "teacher_id": self.teacher_id
        }

class Teacher(User):
    def __init__(self, _id, full_name, email, password_hash):
        super().__init__(_id, full_name, email, password_hash, Role.TEACHER)
        self.subjects = []
        self.classes = []
        self.assignments = {}  # {assignment_id: Assignment}

    def create_assignment(self, title, description, deadline, subject, class_id):
        assignment_id = len(self.assignments) + 1
        assignment = Assignment(assignment_id, title, description, deadline, subject, self._id, class_id)
        self.assignments[assignment_id] = assignment
        return assignment

    def grade_assignment(self, assignment: Assignment, student: Student, grade_value, grade_id):
        assignment.set_grade(student._id, grade_value)
        date = datetime.now().date().isoformat()
        grade = Grade(grade_id, student._id, assignment.subject, grade_value, date, self._id)
        
        
        if assignment.subject not in student.grades:
            student.grades[assignment.subject] = []
        student.grades[assignment.subject].append(grade_value)
        # student.grades.setdefault(assignment.subject, []).append(grade_value)
        print(f"{self.full_name} {student.full_name} ga baho qo'ydi: {grade_value}")
        return grade

    def view_student_progress(self, student_id):
        report = {}
        for assignment in self.assignments.values():
            if student_id in assignment.grades:
                report[assignment.title] = assignment.grades[student_id]
        return report

class Parent(User):
    def __init__(self, _id, full_name, email, password_hash):
        super().__init__(_id, full_name, email, password_hash, Role.PARENT)
        self.children = []  # list of student IDs

    def view_child_grades(self, child_id):
        for child in self.children:
            if child._id == child_id:
                pass

    def view_child_assignments(self, child_id):
        for child in self.children:
            if child._id == child_id:
                pass

    def receive_child_notification(self, child_id):
        for child in self.children:
            if child._id == child_id:
                pass

class Admin(User):
    def __init__(self, _id, full_name, email, password_hash):
        super().__init__(_id, full_name, email, password_hash, Role.ADMIN)
        self.permissions = []

    def add_user(self, user, user_list):
        user_list.append(user)

    def remove_user(self, user_id, user_list):
        user_list[:] = [u for u in user_list if u._id != user_id]

    def generate_report(self):
        return f"Tizim haqida malumot {datetime.now().isoformat()} holatida yaratilgan."

class Schedule:
    def __init__(self, id, class_id, day):
        self.id = id
        self.class_id = class_id
        self.day = day
        self.lessons = {}  # {time: {subject, teacher_id}}

    def add_lesson(self, time, subject, teacher_id):
        self.lessons[time] = {"subject": subject, "teacher_id": teacher_id}

    def view_schedule(self):
        print(f"""Jadval ID: {self.id},
                  Sinf ID: {self.class_id},
                  Darslar: {self.lessons}""")
            
        return self.lessons

    def remove_lesson(self, time):
        if time in self.lessons:
            del self.lessons[time]

def main():
    user_list = []

    admin = Admin(1, "Admin Akmal", "admin@mail.com", "admin123")
    teacher = Teacher(2, "O'qituvchi Olim", "olim@mail.com", "olim123")
    student = Student(3, "O'quvchi Aziz", "aziz@mail.com", "aziz123", grade="9-A")

    admin.add_user(teacher, user_list)
    admin.add_user(student, user_list)


    assignment1 = teacher.create_assignment(
        title="Algebra vazifasi",
        description="Masalalarni yechish",
        deadline="2025-06-15",
        subject="Algebra",
        class_id="9-A"
    )
    student.submit_assignment(assignment1, "Yechim: x = 5")
    teacher.grade_assignment(assignment1, student, grade_value=4, grade_id=1)

    assignment2 = teacher.create_assignment(
        title="Fizika vazifasi",
        description="Nisbiylik nazariyasi",
        deadline="2025-06-16",
        subject="Fizika",
        class_id="9-A"
    )
    student.submit_assignment(assignment2, "Yechim: E = mc*c")
    teacher.grade_assignment(assignment2, student, grade_value=5, grade_id=2)


    print(f"\nProgress hisobot: {teacher.view_student_progress(student_id=3)}")
    print(f"\nO'quvchi baholari: {student.view_grades()}")
    print(f"\nO'rtacha baho: {student.calculate_average_grade():.2f}")


    teacher.add_notification("\nFizika topshirig'ini tekshirib chiqdim!", recipient_id=3, user_list=user_list)
    student.view_notifications()

if __name__ == "__main__":
    main()