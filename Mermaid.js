classDiagram
direction LR

class User {
+String name
+int availableMinutesPerDay
+Map preferences
+updatePreferences(preferences)
}

class Pet {
+String name
+String species
+int age
+String healthNotes
+updateProfile(name, species, age, healthNotes)
}

class Task {
+String title
+int durationMin
+int priority
+String frequency
+bool isRequired
+String earliestTime
+String latestTime
+editTask(title, durationMin, priority, frequency, isRequired, earliestTime, latestTime)
+isValidForDay(date) bool
}

class Schedule {
+String date
+List plannedTasks
+int totalMinutesUsed
+List explanations
+generatePlan(tasks, user, pet) List
+addTask(task) bool
+explainPlan() String
}

User "1" --> "1.." Pet : owns
Pet "1" --> "0.." Task : needs
Schedule "1" --> "1" User : built for
Schedule "1" --> "1" Pet : built for
Schedule "1" o-- "0..*" Task : includes