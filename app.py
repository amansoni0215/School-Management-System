import json
from abc import ABC, abstractmethod
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

# ───────────────────────── Data layer (same JSON file as before) ─────────────────────────
DB = Path("school_data.json")


def load():
    data = {}
    if DB.exists():
        try:
            data = json.loads(DB.read_text() or "{}")
        except json.JSONDecodeError:
            data = {}
    data.setdefault("student", [])
    data.setdefault("teachers", [])
    return data


def save(data):
    DB.write_text(json.dumps(data, indent=4))


# ───────────────────────── Domain classes (your OOP structure) ─────────────────────────
class Persons(ABC):
    @abstractmethod
    def get_roles(self): ...

    @abstractmethod
    def register(self, data, **kw): ...

    @staticmethod
    def validate_email(email):
        return "@" in email and "." in email


class Student(Persons):
    def get_roles(self):
        return "student"

    def register(self, data, name, age, email, roll_no):
        if not name.strip() or not roll_no.strip():
            return False, "Name and roll number are required."
        if not self.validate_email(email):
            return False, "That email address looks invalid."
        if any(s["roll_no"] == roll_no for s in data["student"]):
            return False, f"Roll number {roll_no} is already registered."
        data["student"].append(
            {"name": name.strip(), "age": age, "email": email, "roll_no": roll_no, "grades": {}}
        )
        save(data)
        return True, f"{name} is registered."

    def add_grade(self, data, roll_no, subject, marks):
        if not subject.strip():
            return False, "Enter a subject."
        for s in data["student"]:
            if s["roll_no"] == roll_no:
                s["grades"][subject.strip()] = marks
                save(data)
                return True, f"Saved {subject} · {marks:g} marks."
        return False, "Student not found."

    @staticmethod
    def average(student):
        g = student["grades"]
        return sum(g.values()) / len(g) if g else 0.0


class Teacher(Persons):
    def get_roles(self):
        return "teacher"

    def register(self, data, name, age, email, subject, emp_id):
        if not name.strip() or not emp_id.strip():
            return False, "Name and employee ID are required."
        if not self.validate_email(email):
            return False, "That email address looks invalid."
        if any(t["emp_id"] == emp_id for t in data["teachers"]):
            return False, f"Employee ID {emp_id} is already registered."
        data["teachers"].append(
            {"name": name.strip(), "age": age, "email": email, "subject": subject, "emp_id": emp_id, "grades": {}}
        )
        save(data)
        return True, f"{name} is registered."


stud, tech = Student(), Teacher()

# ───────────────────────── Themes ─────────────────────────
THEMES = {
    "Executive Navy": dict(bg1="#0b1730", bg2="#070f20", glow="#1c3f7a", side="#070f20", card_a="#1d3b73", card_b="#12264a",
        slab="#183261", edge="#060d1c", text="#eef2fa", muted="#9fb0cf", accent="#f2b84b", accent_edge="#a97a1c",
        hover="#ffca6b", ink="#2a1c00", danger="#ff7a7a", danger_edge="#b03a3a", field="#09132a", field_border="#2c4a85",
        track="#09132a", shade="rgba(0,0,0,.45)", hi="rgba(255,255,255,.10)"),
    "Ivory Light": dict(bg1="#eef1f8", bg2="#e4e9f4", glow="#ffffff", side="#ffffff", card_a="#ffffff", card_b="#f1f4fb",
        slab="#e3e8f5", edge="#c3cbe0", text="#1c2540", muted="#5b6785", accent="#3b5bdb", accent_edge="#263fa8",
        hover="#4c6ef5", ink="#ffffff", danger="#e8590c", danger_edge="#a63e06", field="#ffffff", field_border="#b8c2dd",
        track="#dde3f2", shade="rgba(40,60,110,.22)", hi="rgba(255,255,255,.9)"),
    "Graphite Emerald": dict(bg1="#151a1c", bg2="#0d1112", glow="#1f3a33", side="#0d1112", card_a="#2a363a", card_b="#1c2427",
        slab="#263035", edge="#080b0c", text="#eef3f1", muted="#9aaba6", accent="#2ecc8f", accent_edge="#1b8a60",
        hover="#4fe0a6", ink="#04231a", danger="#ff8a65", danger_edge="#b34a2a", field="#0d1112", field_border="#33464b",
        track="#0d1112", shade="rgba(0,0,0,.5)", hi="rgba(255,255,255,.08)"),
    "Royal Plum": dict(bg1="#1a1030", bg2="#110a22", glow="#4a2a8a", side="#110a22", card_a="#3b2670", card_b="#271a4d",
        slab="#33215f", edge="#0e0720", text="#f4effc", muted="#b4a6d4", accent="#ff8fa3", accent_edge="#b84a5f",
        hover="#ffa9b8", ink="#2b0a14", danger="#ffb86b", danger_edge="#b06a1f", field="#110a22", field_border="#4d3a86",
        track="#110a22", shade="rgba(0,0,0,.5)", hi="rgba(255,255,255,.10)"),
    "Chalkboard": dict(bg1="#0f2a2a", bg2="#0b1f20", glow="#1f5a56", side="#0b1f20", card_a="#225553", card_b="#163837",
        slab="#1d4a48", edge="#0a1f1f", text="#f3f1e7", muted="#9db8b3", accent="#f6c945", accent_edge="#b8901a",
        hover="#ffd95e", ink="#2a2000", danger="#ff7a59", danger_edge="#b3472d", field="#0b1f20", field_border="#2b5c59",
        track="#0b1f20", shade="rgba(0,0,0,.45)", hi="rgba(255,255,255,.10)"),
}

st.set_page_config(page_title="School Desk", page_icon="🎓", layout="wide")

NAV = ["Dashboard", "Register student", "Register teacher", "Add grades", "Student details", "Teacher details"]
with st.sidebar:
    st.markdown('<div class="brand">School Desk</div>', unsafe_allow_html=True)
    page = st.radio("Navigate", NAV, label_visibility="collapsed")
    st.markdown("&nbsp;", unsafe_allow_html=True)
    theme_name = st.selectbox("Theme", list(THEMES), index=0)

T = THEMES[theme_name]
root = ":root{" + "".join(f"--{k.replace('_', '-')}:{v};" for k, v in T.items()) + "}"

STYLE = """
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,800&family=DM+Sans:wght@400;500;700&display=swap');

html, body, .stApp, [class*="css"]{font-family:'DM Sans',sans-serif;}
.stApp{
  background: radial-gradient(1200px 600px at 80% -10%, var(--glow) 0%, transparent 60%),
              linear-gradient(160deg, var(--bg1) 0%, var(--bg2) 100%);
  color:var(--text);
}
#MainMenu, footer{visibility:hidden;}
header[data-testid="stHeader"]{background:transparent;}
.block-container{padding-top:2.2rem; max-width:1150px;}

h1,h2,h3,h4{font-family:'Bricolage Grotesque',sans-serif !important; color:var(--text) !important; letter-spacing:-.01em;}
p, label, li, .stMarkdown, [data-testid="stWidgetLabel"] *{color:var(--text);}

.hero{font-family:'Bricolage Grotesque',sans-serif; font-weight:800; font-size:4.2rem; line-height:1;
  color:var(--accent); margin:0 0 .4rem 0;
  text-shadow:1px 1px 0 var(--accent-edge),2px 2px 0 var(--accent-edge),3px 3px 0 var(--accent-edge),
              4px 4px 0 var(--accent-edge),5px 5px 0 var(--accent-edge),6px 6px 0 var(--accent-edge),
              7px 7px 0 var(--accent-edge),8px 12px 22px var(--shade);
  transform:perspective(700px) rotateX(10deg); transform-origin:left bottom;}
.sub{color:var(--muted); font-size:1.05rem; margin-bottom:1.8rem;}

.card3d{
  background:linear-gradient(145deg,var(--card-a),var(--card-b));
  border-radius:18px; padding:20px 22px; margin-bottom:22px;
  transform:perspective(800px) rotateX(6deg) rotateY(-8deg);
  box-shadow:inset 1px 1px 0 var(--hi), 8px 10px 0 var(--edge), 18px 26px 36px var(--shade);
  transition:transform .25s ease, box-shadow .25s ease;}
.card3d:hover{
  transform:perspective(800px) rotateX(0) rotateY(0) translateY(-4px);
  box-shadow:inset 1px 1px 0 var(--hi), 4px 6px 0 var(--edge), 14px 30px 40px var(--shade);}
.card3d .num{font-family:'Bricolage Grotesque',sans-serif; font-weight:800; font-size:2.4rem; color:var(--accent); line-height:1.1; overflow-wrap:anywhere;}
.card3d .lbl{color:var(--muted); font-size:.95rem;}

.bar-row{margin:12px 0;}
.bar-top{display:flex; justify-content:space-between; font-weight:500; margin-bottom:6px; color:var(--text);}
.bar-track{background:var(--track); border-radius:10px; height:16px; box-shadow:inset 0 3px 5px var(--shade);}
.bar-fill{height:16px; border-radius:10px; background:var(--accent);
  box-shadow:0 4px 0 var(--accent-edge), 0 8px 10px var(--shade); transform:translateY(-2px);}
.bar-fill.low{background:var(--danger); box-shadow:0 4px 0 var(--danger-edge), 0 8px 10px var(--shade);}

.tbl-wrap{overflow-x:auto;}
.tbl{width:100%; border-collapse:separate; border-spacing:0 8px;}
.tbl th{color:var(--muted); font-weight:500; text-align:left !important; padding:4px 14px; white-space:nowrap;}
.tbl td{background:var(--slab); color:var(--text); padding:11px 14px; box-shadow:0 4px 0 var(--edge);}
.tbl td:first-child{border-radius:12px 0 0 12px;}
.tbl td:last-child{border-radius:0 12px 12px 0;}

.stButton > button, .stFormSubmitButton > button{
  background:var(--accent); color:var(--ink); font-weight:700; border:none; border-radius:12px; padding:.65rem 1.6rem;
  box-shadow:0 6px 0 var(--accent-edge), 0 12px 18px var(--shade);
  transition:transform .08s ease, box-shadow .08s ease;}
.stButton > button *, .stFormSubmitButton > button *{color:var(--ink) !important;}
.stButton > button:hover, .stFormSubmitButton > button:hover{background:var(--hover); color:var(--ink);}
.stButton > button:active, .stFormSubmitButton > button:active{transform:translateY(5px); box-shadow:0 1px 0 var(--accent-edge), 0 3px 6px var(--shade);}
.stButton > button:focus-visible, .stFormSubmitButton > button:focus-visible{outline:3px solid var(--text); outline-offset:3px;}

.stTextInput input, .stNumberInput input, div[data-baseweb="select"] > div{
  background:var(--field) !important; color:var(--text) !important; border:2px solid var(--field-border) !important;
  border-radius:12px !important; box-shadow:inset 0 3px 6px var(--shade);}
div[data-baseweb="select"] *{color:var(--text) !important;}
.stTextInput input:focus, .stNumberInput input:focus{border-color:var(--accent) !important;}
.stNumberInput button{background:var(--slab) !important; color:var(--text) !important;}
div[data-baseweb="popover"] ul, div[data-baseweb="popover"] li{background:var(--field) !important; color:var(--text) !important;}
div[data-baseweb="popover"] li:hover{background:var(--slab) !important;}
[data-testid="stForm"]{background:linear-gradient(145deg,var(--card-a),var(--card-b)); border:none; border-radius:20px; padding:26px;
  box-shadow:inset 1px 1px 0 var(--hi), 8px 10px 0 var(--edge), 18px 26px 36px var(--shade);}

[data-testid="stSidebar"]{background:var(--side); box-shadow:8px 0 24px var(--shade);}
[data-testid="stSidebar"] .brand{font-family:'Bricolage Grotesque',sans-serif; font-weight:800; font-size:1.7rem; color:var(--accent);
  text-shadow:2px 2px 0 var(--accent-edge), 4px 6px 10px var(--shade); margin-bottom:1rem;}
[data-testid="stSidebar"] [role="radiogroup"] label{
  background:var(--slab); border-radius:12px; padding:.55rem .9rem; margin-bottom:10px; width:100%;
  box-shadow:0 4px 0 var(--edge); transition:transform .1s ease, box-shadow .1s ease;}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{transform:translateY(-2px); box-shadow:0 6px 0 var(--edge);}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:var(--accent); box-shadow:0 4px 0 var(--accent-edge);}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) *{color:var(--ink) !important; font-weight:700;}
[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child{display:none;}

div[data-testid="stAlert"]{border-radius:14px;}
@media (prefers-reduced-motion: reduce){ .card3d, .card3d:hover, .hero{transform:none; transition:none;} }
@media (max-width:700px){ .hero{font-size:2.8rem;} }
"""
st.markdown(f"<style>{root}{STYLE}</style>", unsafe_allow_html=True)


def stat_card(number, label):
    st.markdown(
        f'<div class="card3d"><div class="num">{escape(str(number))}</div><div class="lbl">{escape(label)}</div></div>',
        unsafe_allow_html=True,
    )


def header(title, sub):
    st.markdown(f'<div class="hero">{escape(title)}</div><div class="sub">{escape(sub)}</div>', unsafe_allow_html=True)


def result(ok, msg):
    (st.success if ok else st.error)(msg)


def student_label(s):
    return f"{s['roll_no']} · {s['name']}"


def bar(label, value, shown=None):
    low = " low" if value < 40 else ""
    shown = f"{value:g}" if shown is None else shown
    return (f'<div class="bar-row"><div class="bar-top"><span>{escape(str(label))}</span><span>{shown}</span></div>'
            f'<div class="bar-track"><div class="bar-fill{low}" style="width:{max(0, min(100, value))}%"></div></div></div>')


def table(df):
    raw = df.to_html(index=False, classes="tbl", border=0, escape=True)
    st.markdown('<div class="tbl-wrap">' + "".join(l.strip() for l in raw.splitlines()) + "</div>", unsafe_allow_html=True)


# ───────────────────────── Pages ─────────────────────────
data = load()

if page == "Dashboard":
    header("School Desk", "Everyone in your school, and how they're doing.")
    students, teachers = data["student"], data["teachers"]
    all_marks = [m for s in students for m in s["grades"].values()]
    school_avg = sum(all_marks) / len(all_marks) if all_marks else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1: stat_card(len(students), "Students")
    with c2: stat_card(len(teachers), "Teachers")
    with c3: stat_card(len(all_marks), "Grades recorded")
    with c4: stat_card(f"{school_avg:.1f}", "School average")

    if students:
        df = pd.DataFrame(
            [{"Roll no": s["roll_no"], "Name": s["name"], "Age": s["age"], "Email": s["email"],
              "Subjects": len(s["grades"]), "Average": round(Student.average(s), 1)} for s in students]
        )
        left, right = st.columns([3, 2])
        with left:
            st.markdown("### Students")
            table(df)
        with right:
            st.markdown("### Averages")
            top = df.sort_values("Average", ascending=False).head(8)
            st.markdown("".join(bar(r.Name, r.Average, f"{r.Average:.1f}") for r in top.itertuples()), unsafe_allow_html=True)
    else:
        st.info("No students yet. Open “Register student” to add the first one.")

elif page == "Register student":
    header("Register student", "Add a new student to the school.")
    with st.form("student_form", clear_on_submit=True):
        a, b = st.columns(2)
        name = a.text_input("Name")
        roll_no = b.text_input("Roll number")
        age = a.number_input("Age", min_value=3, max_value=100, value=15, step=1)
        email = b.text_input("Email")
        if st.form_submit_button("Register student"):
            result(*stud.register(data, name, int(age), email, roll_no))

elif page == "Register teacher":
    header("Register teacher", "Add a new teacher to the staff.")
    with st.form("teacher_form", clear_on_submit=True):
        a, b = st.columns(2)
        name = a.text_input("Name")
        emp_id = b.text_input("Employee ID")
        age = a.number_input("Age", min_value=18, max_value=100, value=30, step=1)
        email = b.text_input("Email")
        subject = st.text_input("Subject")
        if st.form_submit_button("Register teacher"):
            result(*tech.register(data, name, int(age), email, subject, emp_id))

elif page == "Add grades":
    header("Add grades", "Record marks for a student's subject.")
    if not data["student"]:
        st.info("Register a student first, then come back to add grades.")
    else:
        with st.form("grade_form", clear_on_submit=True):
            who = st.selectbox("Student", data["student"], format_func=student_label)
            a, b = st.columns(2)
            subject = a.text_input("Subject")
            marks = b.number_input("Marks (out of 100)", min_value=0.0, max_value=100.0, value=0.0, step=0.5)
            if st.form_submit_button("Save grade"):
                result(*stud.add_grade(data, who["roll_no"], subject, marks))

elif page == "Student details":
    header("Student details", "Profile and grades for one student.")
    if not data["student"]:
        st.info("No students registered yet.")
    else:
        s = st.selectbox("Student", data["student"], format_func=student_label)
        avg = Student.average(s)
        c1, c2, c3 = st.columns(3)
        with c1: stat_card(s["name"], f"Roll no. {s['roll_no']}")
        with c2: stat_card(s["age"], f"Age · {s['email']}")
        with c3: stat_card(f"{avg:.1f}", "Average")

        st.markdown("### Grades")
        if not s["grades"]:
            st.info("No grades yet. Open “Add grades” to record the first one.")
        st.markdown("".join(bar(subj, m) for subj, m in s["grades"].items()), unsafe_allow_html=True)

elif page == "Teacher details":
    header("Teacher details", "Profile for one teacher.")
    if not data["teachers"]:
        st.info("No teachers registered yet.")
    else:
        t = st.selectbox("Teacher", data["teachers"], format_func=lambda x: f"{x['emp_id']} · {x['name']}")
        c1, c2, c3 = st.columns(3)
        with c1: stat_card(t["name"], f"Employee ID {t['emp_id']}")
        with c2: stat_card(t["subject"] or "—", "Subject")
        with c3: stat_card(t["age"], f"Age · {t['email']}")