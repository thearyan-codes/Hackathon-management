from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from typing import Optional, List
from datetime import datetime
import uuid

DB = "db_demo.sqlite"

app = FastAPI(title="Hackathon Management API")

# Allow CORS for testing
app.add_middleware(
    CORSMiddleware,
        allow_origins=["*"],
            allow_methods=["*"],
                allow_headers=["*"],
                )

                # DB helper
                def get_db():
                    conn = sqlite3.connect(DB)
                        conn.row_factory = sqlite3.Row
                            try:
                                    yield conn
                                        finally:
                                                conn.close()

                                                # Pydantic models
                                                class HackathonCreate(BaseModel):
                                                    college_id: int
                                                        title: str
                                                            description: Optional[str] = ""
                                                                start_datetime: Optional[str] = None
                                                                    end_datetime: Optional[str] = None
                                                                        max_team_size: Optional[int] = 4

                                                                        class TeamCreate(BaseModel):
                                                                            event_id: str
                                                                                name: str
                                                                                    leader_student_id: int
                                                                                        member_student_ids: Optional[List[int]] = []

                                                                                        class RegisterBody(BaseModel):
                                                                                            event_id: str
                                                                                                student_id: int
                                                                                                    team_id: Optional[int] = None

                                                                                                    class AttendanceBody(BaseModel):
                                                                                                        event_id: str
                                                                                                            student_id: int
                                                                                                                method: Optional[str] = "manual"

                                                                                                                # endpoints
                                                                                                                @app.get("/ping")
                                                                                                                def ping():
                                                                                                                    return {"status": "ok"}

                                                                                                                    @app.post("/api/hackathons")
                                                                                                                    def create_hackathon(h: HackathonCreate, db=Depends(get_db)):
                                                                                                                        event_id = str(uuid.uuid4())
                                                                                                                            db.execute(
                                                                                                                                    "INSERT INTO hackathons (id, college_id, title, description, start_datetime, end_datetime, max_team_size) VALUES (?,?,?,?,?,?,?)",
                                                                                                                                            (event_id, h.college_id, h.title, h.description, h.start_datetime, h.end_datetime, h.max_team_size),
                                                                                                                                                )
                                                                                                                                                    db.commit()
                                                                                                                                                        return {"id": event_id, "title": h.title}

                                                                                                                                                        @app.get("/api/hackathons")
                                                                                                                                                        def list_hackathons(db=Depends(get_db)):
                                                                                                                                                            cur = db.execute("SELECT * FROM hackathons")
                                                                                                                                                                rows = [dict(r) for r in cur.fetchall()]
                                                                                                                                                                    return rows

                                                                                                                                                                    @app.post("/api/teams")
                                                                                                                                                                    def create_team(t: TeamCreate, db=Depends(get_db)):
                                                                                                                                                                        cur = db.execute("SELECT id, max_team_size FROM hackathons WHERE id = ?", (t.event_id,))
                                                                                                                                                                            row = cur.fetchone()
                                                                                                                                                                                if not row:
                                                                                                                                                                                        raise HTTPException(status_code=404, detail="Hackathon not found")
                                                                                                                                                                                            max_size = row["max_team_size"] or 4
                                                                                                                                                                                                if len(t.member_student_ids) + 1 > max_size:
                                                                                                                                                                                                        raise HTTPException(status_code=400, detail="Team exceeds max_team_size")
                                                                                                                                                                                                            cur = db.execute(
                                                                                                                                                                                                                    "INSERT INTO teams (event_id, name, leader_student_id) VALUES (?,?,?)",
                                                                                                                                                                                                                            (t.event_id, t.name, t.leader_student_id),
                                                                                                                                                                                                                                )
                                                                                                                                                                                                                                    team_id = cur.lastrowid
                                                                                                                                                                                                                                        members = [t.leader_student_id] + (t.member_student_ids or [])
                                                                                                                                                                                                                                            for sid in members:
                                                                                                                                                                                                                                                    try:
                                                                                                                                                                                                                                                                db.execute("INSERT INTO team_members (team_id, student_id) VALUES (?,?)", (team_id, sid))
                                                                                                                                                                                                                                                                            db.execute("INSERT OR IGNORE INTO registrations (event_id, student_id, team_id) VALUES (?,?,?)", (t.event_id, sid, team_id))
                                                                                                                                                                                                                                                                                    except sqlite3.IntegrityError:
                                                                                                                                                                                                                                                                                                pass
                                                                                                                                                                                                                                                                                                    db.commit()
                                                                                                                                                                                                                                                                                                        return {"team_id": team_id, "name": t.name}

                                                                                                                                                                                                                                                                                                        @app.post("/api/register")
                                                                                                                                                                                                                                                                                                        def register(r: RegisterBody, db=Depends(get_db)):
                                                                                                                                                                                                                                                                                                            cur = db.execute("SELECT id FROM hackathons WHERE id = ?", (r.event_id,))
                                                                                                                                                                                                                                                                                                                if not cur.fetchone():
                                                                                                                                                                                                                                                                                                                        raise HTTPException(status_code=404, detail="Hackathon not found")
                                                                                                                                                                                                                                                                                                                            try:
                                                                                                                                                                                                                                                                                                                                    db.execute("INSERT INTO registrations (event_id, student_id, team_id) VALUES (?,?,?)", (r.event_id, r.student_id, r.team_id))
                                                                                                                                                                                                                                                                                                                                            db.commit()
                                                                                                                                                                                                                                                                                                                                                except sqlite3.IntegrityError:
                                                                                                                                                                                                                                                                                                                                                        raise HTTPException(status_code=409, detail="Already registered")
                                                                                                                                                                                                                                                                                                                                                            return {"status": "registered"}

                                                                                                                                                                                                                                                                                                                                                            @app.post("/api/attendance")
                                                                                                                                                                                                                                                                                                                                                            def mark_attendance(a: AttendanceBody, db=Depends(get_db)):
                                                                                                                                                                                                                                                                                                                                                                db.execute("INSERT INTO attendance (event_id, student_id, checkin_time, method) VALUES (?,?,?,?)", (a.event_id, a.student_id, datetime.utcnow().isoformat(), a.method))
                                                                                                                                                                                                                                                                                                                                                                    db.commit()
                                                                                                                                                                                                                                                                                                                                                                        return {"status": "checked_in"}

                                                                                                                                                                                                                                                                                                                                                                        @app.get("/api/reports/{event_id}/attendance")
                                                                                                                                                                                                                                                                                                                                                                        def attendance_report(event_id: str, db=Depends(get_db)):
                                                                                                                                                                                                                                                                                                                                                                            cur = db.execute("SELECT COUNT(*) as total_reg FROM registrations WHERE event_id = ?", (event_id,))
                                                                                                                                                                                                                                                                                                                                                                                total_reg = cur.fetchone()["total_reg"]
                                                                                                                                                                                                                                                                                                                                                                                    cur = db.execute("SELECT COUNT(DISTINCT student_id) as total_present FROM attendance WHERE event_id = ?", (event_id,))
                                                                                                                                                                                                                                                                                                                                                                                        total_present = cur.fetchone()["total_present"]
                                                                                                                                                                                                                                                                                                                                                                                            pct = 0.0
                                                                                                                                                                                                                                                                                                                                                                                                if total_reg and total_reg > 0:
                                                                                                                                                                                                                                                                                                                                                                                                        pct = round((total_present / total_reg) * 100.0, 2)
                                                                                                                                                                                                                                                                                                                                                                                                            return {"event_id": event_id, "total_registered": total_reg, "total_present": total_present, "attendance_pct": pct}

                                                                                                                                                                                                                                                                                                                                                                                                            @app.get("/api/reports/top-active")
                                                                                                                                                                                                                                                                                                                                                                                                            def top_active(db=Depends(get_db), limit: int = 3):
                                                                                                                                                                                                                                                                                                                                                                                                                cur = db.execute("SELECT s.id, s.name, COUNT(DISTINCT a.event_id) as events_attended FROM students s JOIN attendance a ON a.student_id = s.id GROUP BY s.id ORDER BY events_attended DESC LIMIT ?", (limit,))
                                                                                                                                                                                                                                                                                                                                                                                                                    rows = [dict(r) for r in cur.fetchall()]
                                                                                                                                                                                                                                                                                                                                                                                                                        return rows