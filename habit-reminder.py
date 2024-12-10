import sqlite3
import datetime
from datetime import timedelta
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import schedule
import time
import os
import platform
from typing import List, Dict, Tuple

class HabitDatabase:
    def __init__(self, db_name: str = "habits.db"):
        """Initialize database connection and create tables if they don't exist."""
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        """Create necessary tables for habits and completion records."""
        self.cursor.executescript('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                target_time TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS completions (
                id INTEGER PRIMARY KEY,
                habit_id INTEGER,
                completed_at TIMESTAMP,
                FOREIGN KEY (habit_id) REFERENCES habits (id)
            );
        ''')
        self.conn.commit()

    def add_habit(self, name: str, description: str = "", target_time: str = None) -> int:
        """Add a new habit and return its ID."""
        self.cursor.execute('''
            INSERT INTO habits (name, description, target_time)
            VALUES (?, ?, ?)
        ''', (name, description, target_time))
        self.conn.commit()
        return self.cursor.lastrowid

    def record_completion(self, habit_id: int, completion_time: datetime.datetime = None):
        """Record a habit completion."""
        if completion_time is None:
            completion_time = datetime.datetime.now()
        self.cursor.execute('''
            INSERT INTO completions (habit_id, completed_at)
            VALUES (?, ?)
        ''', (habit_id, completion_time))
        self.conn.commit()

    def get_completion_history(self, habit_id: int) -> List[datetime.datetime]:
        """Get completion history for a specific habit."""
        self.cursor.execute('''
            SELECT completed_at FROM completions
            WHERE habit_id = ?
            ORDER BY completed_at
        ''', (habit_id,))
        return [datetime.datetime.fromisoformat(row[0]) for row in self.cursor.fetchall()]

    def get_all_habits(self) -> List[Dict]:
        """Get all habits with their details."""
        self.cursor.execute('SELECT * FROM habits')
        columns = [description[0] for description in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

class ReminderPredictor:
    def __init__(self):
        """Initialize the ML model for predicting optimal reminder times."""
        self.model = RandomForestRegressor(n_estimators=100)

    def prepare_features(self, completion_times: List[datetime.datetime]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features from completion times for ML model."""
        if len(completion_times) < 2:
            return None, None

        features = []
        targets = []
        
        for i in range(1, len(completion_times)):
            # Features: day of week, previous completion hour, previous completion minute
            prev_time = completion_times[i-1]
            features.append([
                prev_time.weekday(),
                prev_time.hour,
                prev_time.minute
            ])
            
            # Target: minutes since midnight for current completion
            current_time = completion_times[i]
            minutes_since_midnight = current_time.hour * 60 + current_time.minute
            targets.append(minutes_since_midnight)

        return np.array(features), np.array(targets)

    def train(self, completion_times: List[datetime.datetime]) -> bool:
        """Train the model on historical completion data."""
        X, y = self.prepare_features(completion_times)
        if X is None or len(X) < 2:
            return False
        
        self.model.fit(X, y)
        return True

    def predict_next_time(self, last_completion: datetime.datetime) -> datetime.datetime:
        """Predict the optimal next reminder time."""
        features = np.array([[
            last_completion.weekday(),
            last_completion.hour,
            last_completion.minute
        ]])
        
        predicted_minutes = self.model.predict(features)[0]
        
        # Get next day's date
        next_date = last_completion.date() + timedelta(days=1)
        predicted_time = datetime.datetime.combine(
            next_date,
            datetime.time(
                hour=int(predicted_minutes // 60),
                minute=int(predicted_minutes % 60)
            )
        )
        
        return predicted_time

class HabitReminder:
    def __init__(self):
        """Initialize the habit reminder system."""
        self.db = HabitDatabase()
        self.predictor = ReminderPredictor()
        self.scheduled_reminders = {}

    def send_notification(self, title: str, message: str):
        """Send a system notification."""
        system = platform.system()

        if system == "Darwin":  # macOS
            os.system(f"""
                osascript -e 'display notification "{message}" with title "{title}"'
            """)
        elif system == "Linux":
            os.system(f'notify-send "{title}" "{message}"')
        elif system == "Windows":
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(title, message, duration=10)

    def schedule_reminder(self, habit_id: int):
        """Schedule the next reminder for a habit based on predicted optimal time."""
        habit = self.db.cursor.execute(
            'SELECT name FROM habits WHERE id = ?', (habit_id,)
        ).fetchone()
        
        if not habit:
            return

        completion_history = self.db.get_completion_history(habit_id)
        
        if completion_history:
            if self.predictor.train(completion_history):
                next_time = self.predictor.predict_next_time(completion_history[-1])
            else:
                # If not enough data, use the last completion time
                next_time = completion_history[-1] + timedelta(days=1)
        else:
            # If no history, use current time tomorrow
            next_time = datetime.datetime.now() + timedelta(days=1)

        # Schedule the reminder
        schedule.every().day.at(next_time.strftime("%H:%M")).do(
            self.send_notification,
            "Habit Reminder",
            f"Time to complete your habit: {habit[0]}"
        )

    def start(self):
        """Start the reminder system."""
        habits = self.db.get_all_habits()
        for habit in habits:
            self.schedule_reminder(habit['id'])

        while True:
            schedule.run_pending()
            time.sleep(60)

def main():
    """Main function to demonstrate usage."""
    reminder_system = HabitReminder()
    
    # Example: Add a new habit
    habit_id = reminder_system.db.add_habit(
        name="Daily Exercise",
        description="30 minutes of cardio",
        target_time="08:00"
    )
    
    # Example: Record some completions
    now = datetime.datetime.now()
    for i in range(7):
        completion_time = now - timedelta(days=i)
        reminder_system.db.record_completion(habit_id, completion_time)
    
    # Start the reminder system
    reminder_system.start()

if __name__ == "__main__":
    main()