# Habit Reminder AI

An intelligent CLI/desktop application that helps you build and maintain habits by sending smart notifications at optimal times. The application uses machine learning to analyze your past behavior and predict the best times for reminders.

## Features

- 🤖 AI-powered reminder timing based on your completion patterns
- 📊 SQLite database for reliable data persistence
- 🔔 Cross-platform desktop notifications
- 📈 Pattern recognition for optimal reminder scheduling
- ⚡ Lightweight and efficient
- 🔄 Automatic adjustment to your changing habits

## Installation

1. Clone the repository:
```bash
git clone https://github.com/makalin/Habit-Reminder-AI.git
cd Habit-Reminder-AI
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Dependencies

- Python 3.8+
- numpy
- scikit-learn
- schedule
- win10toast (Windows only)

## Usage

1. Start the application:
```bash
python habit_reminder.py
```

2. Add a new habit:
```python
from habit_reminder import HabitReminder

reminder_system = HabitReminder()
habit_id = reminder_system.db.add_habit(
    name="Daily Exercise",
    description="30 minutes of cardio",
    target_time="08:00"
)
```

3. Record habit completions:
```python
from datetime import datetime
reminder_system.db.record_completion(habit_id, datetime.now())
```

4. Let the system run and learn from your patterns:
```python
reminder_system.start()
```

## How It Works

### Machine Learning Model

The application uses a Random Forest Regressor to predict optimal reminder times based on:
- Day of the week
- Previous completion times
- Historical patterns

### Database Structure

The SQLite database contains two main tables:

1. `habits`:
   - id (PRIMARY KEY)
   - name
   - description
   - target_time
   - created_at

2. `completions`:
   - id (PRIMARY KEY)
   - habit_id (FOREIGN KEY)
   - completed_at

### Notification System

Platform-specific notifications are implemented for:
- Windows (using win10toast)
- macOS (using osascript)
- Linux (using notify-send)

## Configuration

The application creates a `habits.db` file in the root directory by default. You can modify the database location by passing a different path to the `HabitDatabase` constructor:

```python
db = HabitDatabase(db_name="path/to/your/database.db")
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Future Enhancements

- [ ] Web interface for habit management
- [ ] Mobile app integration
- [ ] More sophisticated ML models
- [ ] Habit streaks and statistics
- [ ] Social features and habit sharing
- [ ] Custom notification sounds
- [ ] Export/import functionality

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by atomic habits and behavior psychology
- Built with scikit-learn for machine learning capabilities
- Uses schedule package for reliable task scheduling

## Support

For support, please open an issue in the GitHub repository or contact the maintainers directly.

## Disclaimer

This is an experimental project that uses basic machine learning concepts. The effectiveness of the predictions depends on the consistency and quality of the historical data provided.
