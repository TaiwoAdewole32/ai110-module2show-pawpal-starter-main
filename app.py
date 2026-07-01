import datetime
import streamlit as st
from pawpal_system import Pet, Priority, Task, Owner

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ── Section 1: Owner Setup ────────────────────────────────────────────────────
st.subheader("1. Owner Setup")

owner_name = st.text_input("Your name", value="Jordan")
col1, col2 = st.columns(2)
with col1:
    start_time = st.time_input("Available from", value=datetime.time(7, 0))
with col2:
    end_time = st.time_input("Available until", value=datetime.time(19, 0))

if st.button("Create / Update Owner"):
    st.session_state.owner = Owner(
        name=owner_name,
        startTime=start_time,
        endTime=end_time,
        preferences={},
    )
    st.success(
        f"Owner '{owner_name}' saved — "
        f"{st.session_state.owner.getAvailableTime()} min available "
        f"({start_time.strftime('%H:%M')} to {end_time.strftime('%H:%M')})."
    )

if "owner" in st.session_state:
    o = st.session_state.owner
    st.caption(f"Active owner: **{o.name}** | {o.getAvailableTime()} min available")

# Guard: nothing below can run without an owner
if "owner" not in st.session_state:
    st.info("Fill in your name and time window, then click **Create / Update Owner** to continue.")
    st.stop()

owner: Owner = st.session_state.owner

# ── Section 2: Add a Pet ──────────────────────────────────────────────────────
st.divider()
st.subheader("2. Add a Pet")

with st.form("add_pet_form"):
    col1, col2 = st.columns(2)
    with col1:
        pet_name     = st.text_input("Pet name", value="Mochi")
        species      = st.selectbox("Species", ["dog", "cat", "other"])
        breed        = st.text_input("Breed (optional)", value="")
        age          = st.number_input("Age (years)", min_value=0, max_value=30, value=2)
    with col2:
        energy_level = st.slider("Energy level", min_value=1, max_value=10, value=5)
        food_type    = st.text_input("Food type", value="dry kibble")
        medication   = st.text_input("Medication (or 'none')", value="none")
    pet_submitted = st.form_submit_button("Add Pet")

if pet_submitted:
    new_pet = Pet(
        name=pet_name,
        species=species,
        breed=breed,
        age=int(age),
        foodType=food_type,
        medication=medication,
        energyLevel=int(energy_level),
    )
    owner.addPet(new_pet)
    st.success(f"Pet '{pet_name}' added!")

if owner.pets:
    st.markdown("**Your pets:**")
    for p in owner.pets:
        st.text(p.getPetSummary())
else:
    st.info("No pets yet. Add one above.")

# Guard: task form needs at least one pet for its selector
if not owner.pets:
    st.info("Add at least one pet above before scheduling tasks.")
    st.stop()

# ── Section 3: Schedule a Task ────────────────────────────────────────────────
st.divider()
st.subheader("3. Schedule a Task")

with st.form("add_task_form"):
    col1, col2 = st.columns(2)
    with col1:
        task_name    = st.text_input("Task title", value="Morning walk")
        task_type    = st.text_input("Task type", value="exercise")
        duration     = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        recurrence   = st.selectbox("Recurrence", ["none", "daily", "weekly"])
    with col2:
        priority_str = st.selectbox("Priority", ["high", "medium", "low"])
        selected_pet = st.selectbox(
            "For which pet?",
            options=owner.pets,
            format_func=lambda p: p.name,
        )
        pref_time    = st.time_input("Preferred time", value=datetime.time(8, 0))
        due_date     = st.date_input("Due date", value=datetime.date.today())
    task_submitted = st.form_submit_button("Add Task")

if task_submitted:
    new_task = Task(
        taskName=task_name,
        taskType=task_type,
        durationMinutes=int(duration),
        priority=Priority(priority_str),
        pet=selected_pet,
        preferredTime=pref_time,
        recurrence=recurrence,
        dueDate=due_date,
    )
    owner.scheduler.addTask(new_task)
    st.success(f"Task '{task_name}' added!")

# ── Queued tasks with per-task "Done" button ──────────────────────────────────
if owner.scheduler.tasks:
    st.markdown("**Queued tasks:**")
    for t in owner.scheduler.tasks:
        col1, col2 = st.columns([6, 1])
        with col1:
            st.text(t.getTaskSummary())
        with col2:
            if not t.completed:
                if st.button("Done", key=f"done_{t.taskId}"):
                    next_t = owner.scheduler.completeTask(t)
                    if next_t:
                        st.success(
                            f"Next '{next_t.taskName}' scheduled for {next_t.dueDate}."
                        )
                    st.rerun()
else:
    st.info("No tasks queued yet.")

# ── Section 4: Generate Schedule ─────────────────────────────────────────────
st.divider()
st.subheader("4. Generate Schedule")

if not owner.scheduler.tasks:
    st.info("Add at least one task above before generating a schedule.")
else:
    if st.button("Generate Schedule"):
        owner.scheduler.generatePlan()

        st.markdown("**Daily Plan:**")
        st.text(owner.scheduler.explainPlan())

        conflicts = owner.scheduler.detectConflicts()
        if conflicts:
            st.warning(f"{len(conflicts)} task(s) have overlapping time windows:")
            for c in conflicts:
                st.text(c.getTaskSummary())
        else:
            st.success("No scheduling conflicts detected.")
