import sqlite3
import uuid
from datetime import datetime, timedelta

DB = "db_demo.sqlite"

conn = sqlite3.connect(DB)
c = conn.cursor()

# load schema
with open("init.sql", "r", encoding="utf-8") as f:
    c.executescript(f.read())

    # ensure a college exists
    c.execute("INSERT INTO colleges (name, code) VALUES (?,?)", ("Demo College", "DC01"))
    college_id = c.lastrowid

    # students
    students = [
        ("RC001", "Alice", "alice@example.com", "9990001111"),
            ("RC002", "Bob", "bob@example.com", "9990002222"),
                ("RC003", "Charlie", "charlie@example.com", "9990003333"),
                    ("RC004", "Diana", "diana@example.com", "9990004444"),
                    ]
                    for roll, name, email, phone in students:
                        c.execute(
                                "INSERT OR IGNORE INTO students (college_id, roll_no, name, email, phone) VALUES (?,?,?,?,?)",
                                        (college_id, roll, name, email, phone),
                                            )

                                            # create a hackathon
                                            event_id = str(uuid.uuid4())
                                            start = datetime.now().isoformat()
                                            end = (datetime.now() + timedelta(hours=24)).isoformat()
                                            c.execute(
                                                "INSERT OR IGNORE INTO hackathons (id, college_id, title, description, start_datetime, end_datetime, max_team_size) VALUES (?,?,?,?,?,?,?)",
                                                    (event_id, college_id, "Demo Hackathon", "24-hour demo hackathon", start, end, 4),
                                                    )

                                                    # register all students
                                                    c.execute("SELECT id FROM students WHERE college_id = ?", (college_id,))
                                                    student_ids = [r[0] for r in c.fetchall()]
                                                    for sid in student_ids:
                                                        try:
                                                                c.execute("INSERT INTO registrations (event_id, student_id) VALUES (?,?)", (event_id, sid))
                                                                    except sqlite3.IntegrityError:
                                                                            pass

                                                                            # attendance for first 3
                                                                            for sid in student_ids[:3]:
                                                                                c.execute(
                                                                                        "INSERT INTO attendance (event_id, student_id, checkin_time, method) VALUES (?,?,?,?)",
                                                                                                (event_id, sid, datetime.now().isoformat(), "qr"),
                                                                                                    )

                                                                                                    # simple feedback
                                                                                                    c.execute(
                                                                                                        "INSERT OR IGNORE INTO feedbacks (event_id, student_id, rating, comment) VALUES (?,?,?,?)",
                                                                                                            (event_id, student_ids[0], 5, "Great event"),
                                                                                                            )
                                                                                                            c.execute(
                                                                                                                "INSERT OR IGNORE INTO feedbacks (event_id, student_id, rating, comment) VALUES (?,?,?,?)",
                                                                                                                    (event_id, student_ids[1], 4, "Nice"),
                                                                                                                    )

                                                                                                                    conn.commit()
                                                                                                                    conn.close()
                                                                                                                    print("Seed completed. DB:", DB)
                                                                                                                    print("Sample hackathon id:", event_id)