from __future__ import annotations
from dataclasses import dataclass, field as dc_field
from datetime import time as Time, datetime, timedelta, date as Date
from enum import Enum
from typing import Any, Optional
import uuid


class Priority(str, Enum):
    LOW    = "low"
    MEDIUM = "medium"
    HIGH   = "high"


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    foodType: str
    medication: str
    energyLevel: int
    careNeeds: list[str] = dc_field(default_factory=list)
    tasks: list[Task] = dc_field(default_factory=list)

    def addCareNeed(self, need: str) -> None:
        """Append a care need string to this pet's careNeeds list."""
        self.careNeeds.append(need)

    def getPetSummary(self) -> str:
        """Return a single-line summary of the pet's key attributes."""
        meds = self.medication or "none"
        needs = ", ".join(self.careNeeds) if self.careNeeds else "none"
        return (
            f"{self.name} ({self.breed}, {self.species}) | "
            f"Age: {self.age} | Food: {self.foodType} | "
            f"Medication: {meds} | Energy: {self.energyLevel}/10 | "
            f"Care needs: {needs}"
        )


@dataclass
class Task:
    taskName: str
    taskType: str
    durationMinutes: int
    priority: Priority
    pet: Pet
    preferredTime: Time          # datetime.time replaces the bare "HH:MM" string
    recurrence: str = "none"     # "none" | "daily" | "weekly"
    dueDate: Date = dc_field(default_factory=lambda: datetime.today().date())
    completed: bool = False
    notes: str = ""
    taskId: str = dc_field(default_factory=lambda: str(uuid.uuid4()))

    def markComplete(self) -> None:
        """Mark this task as completed by setting completed to True."""
        self.completed = True

    def updateTask(self, field_name: str, value: Any) -> None:
        """Update a single task field by name if it exists on the task."""
        if hasattr(self, field_name):
            setattr(self, field_name, value)

    def _spawn_next(self) -> Optional[Task]:
        """Return a fresh Task for the next recurrence, or None if this task is non-recurring."""
        if self.recurrence == "none":
            return None
        delta = timedelta(days=1) if self.recurrence == "daily" else timedelta(weeks=1)
        return Task(
            taskName=self.taskName,
            taskType=self.taskType,
            durationMinutes=self.durationMinutes,
            priority=self.priority,
            pet=self.pet,
            preferredTime=self.preferredTime,
            recurrence=self.recurrence,
            dueDate=self.dueDate + delta,
            notes=self.notes,
        )

    def getTaskSummary(self) -> str:
        """Return a single-line summary of the task including priority, timing, recurrence, and status."""
        status = "done" if self.completed else "pending"
        recur_str = f" ({self.recurrence})" if self.recurrence != "none" else ""
        summary = (
            f"[{self.priority.value.upper()}] {self.taskName} ({self.taskType}) | "
            f"{self.durationMinutes} min @ {self.preferredTime.strftime('%H:%M')} | "
            f"Pet: {self.pet.name} | Due: {self.dueDate}{recur_str} | Status: {status}"
        )
        if self.notes:
            summary += f" | Notes: {self.notes}"
        return summary


class Scheduler:
    _PRIORITY_ORDER = {
        Priority.HIGH: 3,
        Priority.MEDIUM: 2,
        Priority.LOW: 1
    }

    def __init__(
        self,
        tasks: Optional[list[Task]] = None,
        timeAvailable: int = 0,
        startTime: Optional[Time] = None,
        dailyPlan: Optional[list[Task]] = None,
        unscheduledTasks: Optional[list[Task]] = None,
        ownerName: str = "",
    ) -> None:
        self.tasks: list[Task] = tasks if tasks is not None else []
        self.timeAvailable = timeAvailable
        self.startTime = startTime
        self.dailyPlan: list[Task] = dailyPlan if dailyPlan is not None else []
        self.unscheduledTasks: list[Task] = (
            unscheduledTasks if unscheduledTasks is not None else []
        )
        self.ownerName = ownerName

    def addTask(self, task: Task) -> None:
        """Add a task to the scheduler and register it on the associated pet."""
        self.tasks.append(task)
        if task not in task.pet.tasks:
            task.pet.tasks.append(task)

    def editTask(self, task: Task) -> None:
        """Replace the stored task matching task.taskId in both the scheduler and the pet."""
        for i, stored_task in enumerate(self.tasks):
            if stored_task.taskId == task.taskId:
                self.tasks[i] = task
                for j, pet_task in enumerate(task.pet.tasks):
                    if pet_task.taskId == task.taskId:
                        task.pet.tasks[j] = task
                        break
                return

    def generatePlan(self) -> list[Task]:
        """Fit today's pending tasks by priority within the available time window."""
        today = datetime.today()
        eligible = [t for t in self.tasks if not t.completed and t.dueDate <= today.date()]
        sorted_tasks = sorted(
            eligible,
            key=lambda task: self._PRIORITY_ORDER.get(task.priority, 0),
            reverse=True,
        )
        self.dailyPlan = []
        self.unscheduledTasks = []
        remaining = self.timeAvailable

        window_end: Optional[Time] = None
        if self.startTime is not None:
            window_end = (
                datetime.combine(today, self.startTime)
                + timedelta(minutes=self.timeAvailable)
            ).time()

        for task in sorted_tasks:
            in_window = (
                self._fits_window(task, today, window_end)
                if self.startTime is not None
                else True
            )
            if task.durationMinutes <= remaining and in_window:
                self.dailyPlan.append(task)
                remaining -= task.durationMinutes
            else:
                self.unscheduledTasks.append(task)

        self.dailyPlan = self.sort_by_time(self.dailyPlan)
        return self.dailyPlan

    def _fits_window(self, task: Task, today_dt: datetime, window_end: Time) -> bool:
        """Return True if the task's time slot falls entirely within the owner's window."""
        task_end = (
            datetime.combine(today_dt, task.preferredTime)
            + timedelta(minutes=task.durationMinutes)
        ).time()
        return task.preferredTime >= self.startTime and task_end <= window_end

    def sortTasksByPriority(self) -> list[Task]:
        """Return all tasks sorted from highest to lowest priority."""
        return sorted(
            self.tasks,
            key=lambda task: self._PRIORITY_ORDER.get(task.priority, 0),
            reverse=True,
        )
    def sort_by_time(self, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Return all tasks sorted from earliest to latest preferred time."""
        task_list = tasks if tasks is not None else self.tasks
        return sorted(task_list, key=lambda task: task.preferredTime)

    def filterTasks(
        self,
        completed: Optional[bool] = None,
        petName: Optional[str] = None,
    ) -> list[Task]:
        """Return tasks matching the given completion status and/or pet name; both filters are optional and combinable."""
        result = self.tasks
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        if petName is not None:
            result = [t for t in result if t.pet.name.lower() == petName.lower()]
        return result

    def completeTask(self, task: Task) -> Optional[Task]:
        """Mark a task complete and auto-register its next occurrence if it is recurring."""
        task.markComplete()
        next_task = task._spawn_next()
        if next_task is not None:
            self.addTask(next_task)
        return next_task

    def detectConflicts(self) -> list[Task]:
        """Return all tasks whose time windows overlap with at least one other task."""
        conflicts: dict[str, Task] = {}
        today = datetime.today()

        for i, task_a in enumerate(self.tasks):
            start_a = datetime.combine(today, task_a.preferredTime)
            end_a = start_a + timedelta(minutes=task_a.durationMinutes)

            for task_b in self.tasks[i + 1:]:
                start_b = datetime.combine(today, task_b.preferredTime)
                end_b = start_b + timedelta(minutes=task_b.durationMinutes)

                if start_a < end_b and start_b < end_a:
                    conflicts[task_a.taskId] = task_a
                    conflicts[task_b.taskId] = task_b

        return list(conflicts.values())

    def getConflictWarnings(self) -> list[str]:
        """Return a warning string for every overlapping task pair, noting whether it is same-pet or cross-pet."""
        warnings: list[str] = []
        today = datetime.today()

        for i, task_a in enumerate(self.tasks):
            start_a = datetime.combine(today, task_a.preferredTime)
            end_a   = start_a + timedelta(minutes=task_a.durationMinutes)

            for task_b in self.tasks[i + 1:]:
                start_b = datetime.combine(today, task_b.preferredTime)
                end_b   = start_b + timedelta(minutes=task_b.durationMinutes)

                if start_a < end_b and start_b < end_a:
                    conflict_type = (
                        "same-pet" if task_a.pet.name == task_b.pet.name else "cross-pet"
                    )
                    warnings.append(
                        f"WARNING [{conflict_type}] "
                        f"'{task_a.taskName}' ({task_a.pet.name}, "
                        f"{start_a.strftime('%H:%M')}–{end_a.strftime('%H:%M')}) "
                        f"overlaps with "
                        f"'{task_b.taskName}' ({task_b.pet.name}, "
                        f"{start_b.strftime('%H:%M')}–{end_b.strftime('%H:%M')})"
                    )

        return warnings

    def explainPlan(self) -> str:
        """Return a daily plan grouped by pet, including unscheduled tasks."""
        if not self.dailyPlan:
            return "No plan generated yet. Call generatePlan() first."

        total_minutes = sum(task.durationMinutes for task in self.dailyPlan)

        if self.ownerName:
            heading = f"Daily plan for {self.ownerName}'s pets"
        else:
            heading = "Daily plan"

        lines = [
            f"{heading} — {len(self.dailyPlan)} task(s), "
            f"{total_minutes} of {self.timeAvailable} min used:"
        ]

        tasks_by_pet: dict[str, list[Task]] = {}
        pet_labels: dict[str, str] = {}

        for task in self.dailyPlan:
            pet_key = task.pet.name
            tasks_by_pet.setdefault(pet_key, []).append(task)
            if task.pet.breed:
                pet_labels[pet_key] = f"{task.pet.name} ({task.pet.breed})"
            else:
                pet_labels[pet_key] = f"{task.pet.name} ({task.pet.species})"

        for pet_key, pet_tasks in tasks_by_pet.items():
            lines.append(f"\n{pet_labels[pet_key]}:")
            for task in sorted(pet_tasks, key=lambda t: t.preferredTime):
                lines.append(
                    f"  {task.preferredTime.strftime('%H:%M')} -> {task.taskName} "
                    f"({task.durationMinutes} min) "
                    f"[priority: {task.priority.value}]"
                )

        if self.unscheduledTasks:
            lines.append(
                f"\nNot scheduled "
                f"({len(self.unscheduledTasks)} task(s) — insufficient time or outside window):"
            )
            for task in self.unscheduledTasks:
                lines.append(
                    f"  - {task.taskName} for {task.pet.name} "
                    f"({task.durationMinutes} min) "
                    f"[priority: {task.priority.value}]"
                )

        return "\n".join(lines)


class Owner:
    def __init__(
        self,
        name: str,
        startTime: Time,
        endTime: Time,
        preferences: dict[str, str],
        pets: Optional[list[Pet]] = None,
        scheduler: Optional[Scheduler] = None,
    ) -> None:
        self.name = name
        self.startTime = startTime
        self.endTime = endTime
        self.preferences = preferences
        self.pets: list[Pet] = pets if pets is not None else []
        self.scheduler: Scheduler = (
            scheduler if scheduler is not None
            else Scheduler(
                timeAvailable=self.availableMinutes,
                startTime=startTime,
                ownerName=name,
            )
        )

    @property
    def availableMinutes(self) -> int:
        """Compute available minutes from the owner's start-to-end time window."""
        start = datetime.combine(datetime.today(), self.startTime)
        end = datetime.combine(datetime.today(), self.endTime)
        return max(0, int((end - start).total_seconds() // 60))

    def addPet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def updatePreferences(self, prefs: dict[str, str]) -> None:
        """Merge the given preferences into the owner's existing preferences."""
        self.preferences.update(prefs)

    def getAvailableTime(self) -> int:
        """Return the number of minutes the owner has available for pet care."""
        return self.availableMinutes
