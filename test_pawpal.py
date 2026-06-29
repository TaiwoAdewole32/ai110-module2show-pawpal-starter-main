import unittest
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


def make_task(pet, name="Morning Walk", time="08:00"):
    return Task(
        taskName=name,
        taskType="exercise",
        durationMinutes=30,
        priority=Priority.HIGH,
        pet=pet,
        preferredTime=time,
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


if __name__ == "__main__":
    unittest.main()
