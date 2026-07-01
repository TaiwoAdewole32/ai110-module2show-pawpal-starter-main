import unittest
from datetime import time as Time
from pawpal_system import Pet, Task, Scheduler, Priority


def make_pet(name="Mochi"):
    return Pet(
        name=name,
        species="dog",
        breed="Shiba Inu",
        age=3,
        foodType="dry",
        medication="none",
        energyLevel=8,
    )


def make_task(pet, name="Morning Walk", preferred_time=Time(8, 0)):
    return Task(
        taskName=name,
        taskType="exercise",
        durationMinutes=30,
        priority=Priority.HIGH,
        pet=pet,
        preferredTime=preferred_time,
    )


class TestMarkComplete(unittest.TestCase):
    def test_mark_complete_sets_status_to_completed(self):
        pet = make_pet()
        task = make_task(pet)

        self.assertFalse(task.completed, "Task should start as not completed")

        task.markComplete()

        self.assertTrue(task.completed, "Task should be completed after calling markComplete()")


class TestAddTaskIncreasesCount(unittest.TestCase):
    def test_adding_task_increases_pet_task_count(self):
        pet = make_pet()
        scheduler = Scheduler(timeAvailable=120)

        count_before = len(pet.tasks)

        task = make_task(pet)
        scheduler.addTask(task)

        self.assertEqual(
            len(pet.tasks),
            count_before + 1,
            "Pet's task count should increase by 1 after addTask()",
        )


class TestFilterTasks(unittest.TestCase):
    def test_filter_by_completion_status(self):
        pet = make_pet()
        scheduler = Scheduler(timeAvailable=120)
        task_a = make_task(pet, name="Task A")
        task_b = make_task(pet, name="Task B")
        scheduler.addTask(task_a)
        scheduler.addTask(task_b)
        task_a.markComplete()

        self.assertEqual(len(scheduler.filterTasks(completed=True)),  1)
        self.assertEqual(len(scheduler.filterTasks(completed=False)), 1)

    def test_filter_by_pet_name_case_insensitive(self):
        pet_a = make_pet("Rex")
        pet_b = make_pet("Luna")
        scheduler = Scheduler(timeAvailable=120)
        scheduler.addTask(make_task(pet_a, name="Rex task"))
        scheduler.addTask(make_task(pet_b, name="Luna task"))

        self.assertEqual(len(scheduler.filterTasks(petName="Rex")),  1)
        self.assertEqual(len(scheduler.filterTasks(petName="rex")),  1)
        self.assertEqual(len(scheduler.filterTasks(petName="Luna")), 1)

    def test_combined_filter(self):
        pet = make_pet("Scout")
        scheduler = Scheduler(timeAvailable=120)
        t1 = make_task(pet, name="A")
        t2 = make_task(pet, name="B")
        scheduler.addTask(t1)
        scheduler.addTask(t2)
        t1.markComplete()

        pending_scout = scheduler.filterTasks(completed=False, petName="Scout")
        self.assertEqual(len(pending_scout), 1)
        self.assertEqual(pending_scout[0].taskName, "B")


class TestRecurrence(unittest.TestCase):
    def setUp(self):
        from datetime import date
        self.today = date.today()
        self.pet = make_pet()
        self.scheduler = Scheduler(timeAvailable=240)

    def _make_recurring(self, recurrence: str) -> Task:
        return Task(
            taskName="Recurring Task",
            taskType="exercise",
            durationMinutes=30,
            priority=Priority.HIGH,
            pet=self.pet,
            preferredTime=Time(8, 0),
            recurrence=recurrence,
            dueDate=self.today,
        )

    def test_daily_task_spawns_next_day(self):
        from datetime import timedelta
        task = self._make_recurring("daily")
        self.scheduler.addTask(task)

        next_task = self.scheduler.completeTask(task)

        self.assertTrue(task.completed)
        self.assertIsNotNone(next_task)
        self.assertEqual(next_task.dueDate, self.today + timedelta(days=1))
        self.assertEqual(next_task.recurrence, "daily")
        self.assertFalse(next_task.completed)
        self.assertIn(next_task, self.scheduler.tasks)

    def test_weekly_task_spawns_next_week(self):
        from datetime import timedelta
        task = self._make_recurring("weekly")
        self.scheduler.addTask(task)

        next_task = self.scheduler.completeTask(task)

        self.assertIsNotNone(next_task)
        self.assertEqual(next_task.dueDate, self.today + timedelta(weeks=1))
        self.assertEqual(next_task.recurrence, "weekly")

    def test_nonrecurring_task_spawns_nothing(self):
        task = self._make_recurring("none")
        self.scheduler.addTask(task)
        count_before = len(self.scheduler.tasks)

        next_task = self.scheduler.completeTask(task)

        self.assertIsNone(next_task)
        self.assertEqual(len(self.scheduler.tasks), count_before)

    def test_spawned_task_inherits_all_fields(self):
        task = self._make_recurring("daily")
        self.scheduler.addTask(task)

        next_task = self.scheduler.completeTask(task)

        self.assertEqual(next_task.taskName,       task.taskName)
        self.assertEqual(next_task.taskType,       task.taskType)
        self.assertEqual(next_task.durationMinutes, task.durationMinutes)
        self.assertEqual(next_task.priority,       task.priority)
        self.assertEqual(next_task.preferredTime,  task.preferredTime)
        self.assertEqual(next_task.pet,            task.pet)


class TestGeneratePlan(unittest.TestCase):
    def setUp(self):
        from datetime import date
        self.today = date.today()
        self.pet = make_pet()

    def _make_task(self, name, preferred_time, duration=30, priority=Priority.HIGH):
        return Task(
            taskName=name,
            taskType="exercise",
            durationMinutes=duration,
            priority=priority,
            pet=self.pet,
            preferredTime=preferred_time,
            dueDate=self.today,
        )

    def test_no_start_time_schedules_tasks_that_fit(self):
        t1 = self._make_task("Walk", Time(8,  0), duration=30, priority=Priority.HIGH)
        t2 = self._make_task("Feed", Time(12, 0), duration=20, priority=Priority.MEDIUM)
        t3 = self._make_task("Bath", Time(18, 0), duration=60, priority=Priority.LOW)
        s = Scheduler(tasks=[t1, t2, t3], timeAvailable=60)
        result = s.generatePlan()
        self.assertIn(t1, result)
        self.assertIn(t2, result)
        self.assertNotIn(t3, result)
        self.assertIn(t3, s.unscheduledTasks)

    def test_no_start_time_plan_sorted_by_preferred_time(self):
        t_late  = self._make_task("Late",  Time(14, 0), duration=10)
        t_early = self._make_task("Early", Time(7,  0), duration=10)
        result = Scheduler(tasks=[t_late, t_early], timeAvailable=60).generatePlan()
        self.assertEqual(result[0].taskName, "Early")
        self.assertEqual(result[1].taskName, "Late")

    def test_completed_tasks_excluded(self):
        t_done = self._make_task("Done",    Time(8, 0), duration=20)
        t_done.markComplete()
        t_pend = self._make_task("Pending", Time(9, 0), duration=20)
        result = Scheduler(tasks=[t_done, t_pend], timeAvailable=120).generatePlan()
        self.assertNotIn(t_done, result)
        self.assertIn(t_pend, result)

    def test_with_start_time_rejects_task_outside_window(self):
        t_in  = self._make_task("Inside",  Time(8,  0), duration=30)
        t_out = self._make_task("Outside", Time(20, 0), duration=30)
        s = Scheduler(tasks=[t_in, t_out], timeAvailable=60, startTime=Time(8, 0))
        result = s.generatePlan()
        self.assertIn(t_in, result)
        self.assertNotIn(t_out, result)
        self.assertIn(t_out, s.unscheduledTasks)

    def test_with_start_time_rejects_task_that_overruns_window(self):
        # Window 08:00–09:00; task at 08:45 + 30 min ends at 09:15
        t = self._make_task("Overrun", Time(8, 45), duration=30)
        s = Scheduler(tasks=[t], timeAvailable=60, startTime=Time(8, 0))
        self.assertEqual(s.generatePlan(), [])
        self.assertIn(t, s.unscheduledTasks)

    def test_generateplan_resets_state_on_repeated_calls(self):
        t = self._make_task("Walk", Time(8, 0), duration=20)
        s = Scheduler(tasks=[t], timeAvailable=60)
        s.generatePlan()
        self.assertEqual(s.generatePlan().count(t), 1)


if __name__ == "__main__":
    unittest.main()
