import uuid
from datetime import date, datetime, timedelta
from random import choice, randint, uniform

from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.user import User
from app.models.department import Department
from app.models.employee import Employee
from app.models.attendance import Attendance

Base.metadata.create_all(bind=engine)
db = SessionLocal()

try:
    admin_user = User(
        id=uuid.uuid4(),
        email="admin@ems.com",
        username="admin",
        hashed_password=hash_password("admin123"),
        full_name="System Admin",
        is_superuser=True,
    )
    db.add(admin_user)

    manager_user = User(
        id=uuid.uuid4(),
        email="manager@ems.com",
        username="manager",
        hashed_password=hash_password("manager123"),
        full_name="Jane Manager",
    )
    db.add(manager_user)
    db.flush()

    departments_data = [
        {"name": "Engineering", "description": "Software development and infrastructure"},
        {"name": "Marketing", "description": "Brand management and campaigns"},
        {"name": "Sales", "description": "Revenue generation and client acquisition"},
        {"name": "Human Resources", "description": "Recruitment and employee relations"},
        {"name": "Finance", "description": "Accounting and financial planning"},
        {"name": "Operations", "description": "Logistics and daily operations"},
    ]
    departments = []
    for dept in departments_data:
        d = Department(id=uuid.uuid4(), name=dept["name"], description=dept["description"])
        db.add(d)
        departments.append(d)
    db.flush()

    first_names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Hank", "Ivy", "Jack",
                   "Karen", "Leo", "Mona", "Nate", "Olivia", "Paul", "Quinn", "Rosa", "Sam", "Tina"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
                  "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson"]
    positions = ["Software Engineer", "Senior Developer", "DevOps Engineer", "Product Manager",
                 "Data Analyst", "UX Designer", "QA Engineer", "Tech Lead", "Scrum Master",
                 "Frontend Developer", "Backend Developer", "Full Stack Developer"]
    statuses = ["active", "active", "active", "active", "active", "active", "active", "inactive", "terminated"]

    employees = []
    for i in range(45):
        first = choice(first_names)
        last = choice(last_names)
        dept = choice(departments)
        emp = Employee(
            id=uuid.uuid4(),
            employee_id=f"EMP{i+1:03d}",
            department_id=dept.id,
            first_name=first,
            last_name=last,
            email=f"{first.lower()}.{last.lower()}@company.com",
            phone=f"+1-555-{randint(1000,9999)}",
            position=choice(positions),
            salary=round(uniform(45000, 150000), 2),
            date_of_birth=date(1970 + randint(0, 35), randint(1, 12), randint(1, 28)),
            date_of_hire=date(2015 + randint(0, 9), randint(1, 12), randint(1, 28)),
            address=f"{randint(100, 9999)} {choice(['Oak', 'Elm', 'Maple', 'Pine', 'Cedar'])} St",
            city=choice(["New York", "San Francisco", "Chicago", "Austin", "Seattle", "Boston"]),
            state=choice(["NY", "CA", "IL", "TX", "WA", "MA"]),
            zip_code=f"{randint(10000, 99999)}",
            status=choice(statuses),
        )
        db.add(emp)
        employees.append(emp)
    db.flush()

    departments[0].manager_id = employees[0].id
    departments[1].manager_id = employees[1].id
    departments[2].manager_id = employees[2].id

    today = date.today()
    for i in range(30):
        day = today - timedelta(days=i)
        if day.weekday() < 5:
            for emp in employees[:20]:
                check_in = datetime(day.year, day.month, day.day, randint(7, 9), randint(0, 59))
                check_out = datetime(day.year, day.month, day.day, randint(16, 19), randint(0, 59))
                att = Attendance(
                    id=uuid.uuid4(),
                    employee_id=emp.id,
                    date=day,
                    check_in=check_in,
                    check_out=check_out,
                    status=choice(["present", "present", "present", "late", "absent"]),
                )
                db.add(att)

    db.commit()
    print("Database seeded successfully with 45 employees, 6 departments, and attendance records.")

except Exception as e:
    db.rollback()
    print(f"Error seeding database: {e}")
    raise
finally:
    db.close()
