from __future__ import annotations

from datetime import date
import logging
from pathlib import Path

import streamlit as st

from pawpal_system import Pet, Schedule, Task, User

LOG_PATH = Path("app.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Smart pet care planning with guardrails, agentic scheduling, and reliability checks.")

st.subheader("Owner and Pet")
owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input("Minutes available today", min_value=10, max_value=1440, value=90)
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
pet_age = st.number_input("Pet age", min_value=0, max_value=40, value=4)
health_notes = st.text_area("Health notes", value="Needs daily medication after food.")
custom_health_cases = st.text_area(
    "Custom health cases (optional)",
    value="Example: gets anxious in loud areas; avoid long midday walks in heat.",
)

st.subheader("Task Manager")
if "tasks" not in st.session_state:
    st.session_state.tasks = []

c1, c2, c3 = st.columns(3)
with c1:
    task_title = st.text_input("Task title", value="Morning walk")
with c2:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
with c3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

c4, c5, c6 = st.columns(3)
with c4:
    frequency = st.selectbox(
        "Frequency",
        ["daily", "weekdays", "weekends", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
        index=0,
    )
with c5:
    required = st.checkbox("Required", value=False)
with c6:
    notes = st.text_input("Task notes", value="")

if st.button("Add Task"):
    st.session_state.tasks.append(
        {
            "title": task_title.strip(),
            "duration_min": int(duration),
            "priority": priority,
            "frequency": frequency,
            "is_required": required,
            "notes": notes.strip(),
        }
    )
    logger.info("Added task: %s", task_title)

if st.session_state.tasks:
    st.write("Current tasks")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add a few tasks to build a schedule.")

if st.button("Clear Tasks"):
    st.session_state.tasks = []
    st.rerun()

st.subheader("Generate Daily Plan")
if st.button("Build Schedule"):
    if not owner_name.strip() or not pet_name.strip():
        st.error("Owner name and pet name are required.")
        st.stop()

    if not st.session_state.tasks:
        st.error("Please add at least one task before generating a schedule.")
        st.stop()

    user = User(name=owner_name.strip(), available_minutes_per_day=int(available_minutes))
    pet = Pet(name=pet_name.strip(), species=species, age=int(pet_age), health_notes=health_notes.strip())

    tasks = [
        Task(
            title=t["title"],
            duration_min=t["duration_min"],
            priority=t["priority"],
            frequency=t["frequency"],
            is_required=t["is_required"],
            notes=t.get("notes", ""),
        )
        for t in st.session_state.tasks
        if t["title"].strip()
    ]

    schedule = Schedule(target_day=date.today())
    plan = schedule.generate_plan(
        tasks,
        user,
        pet,
        custom_health_cases=custom_health_cases.strip(),
    )

    if not plan:
        st.warning("No tasks could be scheduled under current constraints.")
    else:
        st.success("Schedule generated.")
        st.write("### Planned Tasks")
        st.table(
            [
                {
                    "title": t.title,
                    "duration_min": t.duration_min,
                    "priority": t.priority,
                    "frequency": t.frequency,
                    "required": t.is_required,
                }
                for t in plan
            ]
        )

    st.write(f"Total minutes used: {schedule.total_minutes_used}")
    st.write(f"Reliability score: {schedule.reliability_score:.2f}")
    st.write("### Planner Reasoning")
    st.code(schedule.explain_plan())

    st.write("### RAG Guidance")
    st.write(schedule.rag_guidance if schedule.rag_guidance else "No RAG guidance available.")

    st.write("### Retrieved Knowledge")
    if schedule.rag_evidence:
        for item in schedule.rag_evidence:
            st.markdown(f"- {item}")
    else:
        st.caption("No evidence retrieved.")

    st.caption(f"Log file: {LOG_PATH.resolve()}")
