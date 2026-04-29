from datetime import date

from pawpal_system import Pet, Schedule, Task, User
from pawpal_rag import retrieve_pet_knowledge


def test_task_frequency_weekdays_excludes_sunday():
    task = Task("Morning Walk", 20, "high", "weekdays")
    sunday = date(2026, 5, 3)
    assert task.is_valid_for_day(sunday) is False


def test_required_task_is_prioritized_in_schedule():
    user = User("Sam", available_minutes_per_day=30)
    pet = Pet("Mochi", "dog", 3)
    tasks = [
        Task("Play", 20, "low", "daily", is_required=False),
        Task("Medication", 10, "medium", "daily", is_required=True),
        Task("Walk", 20, "high", "daily", is_required=False),
    ]

    schedule = Schedule(target_day=date(2026, 4, 29))
    plan = schedule.generate_plan(tasks, user, pet)
    titles = [t.title for t in plan]
    assert "Medication" in titles


def test_schedule_never_exceeds_time_budget():
    user = User("Lee", available_minutes_per_day=25)
    pet = Pet("Pip", "cat", 2)
    tasks = [
        Task("Long Walk", 30, "high", "daily"),
        Task("Feed", 10, "high", "daily", is_required=True),
        Task("Brush", 20, "medium", "daily"),
    ]

    schedule = Schedule(target_day=date(2026, 4, 29))
    schedule.generate_plan(tasks, user, pet)
    assert schedule.total_minutes_used <= user.available_minutes_per_day


def test_reliability_score_drops_when_required_tasks_cannot_fit():
    user = User("Rae", available_minutes_per_day=10)
    pet = Pet("Nova", "dog", 6)
    tasks = [
        Task("Medication", 15, "high", "daily", is_required=True),
        Task("Feed", 10, "high", "daily", is_required=True),
    ]

    schedule = Schedule(target_day=date(2026, 4, 29))
    schedule.generate_plan(tasks, user, pet)
    assert schedule.reliability_score < 0.7


def test_rag_retrieval_is_integrated_into_schedule_output():
    user = User("Ari", available_minutes_per_day=45)
    pet = Pet("Luna", "dog", 5, health_notes="takes medication with food")
    tasks = [
        Task("Feed", 10, "high", "daily", is_required=True),
        Task("Medication", 10, "high", "daily", is_required=True),
    ]

    schedule = Schedule(target_day=date(2026, 4, 29))
    schedule.generate_plan(tasks, user, pet)

    assert schedule.rag_guidance != ""
    assert len(schedule.rag_evidence) > 0

    top = retrieve_pet_knowledge("dog medication with food", top_k=1)[0]
    assert top.source in {"Medication Safety", "General Care Guide", "Routine Reliability"}
