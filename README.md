# 🎬 AI Video Task Manager

![HTML5](https://img.shields.io/badge/HTML5-Markup-orange?logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-Styles-blue?logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-Frontend-yellow?logo=javascript&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-teal?logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey?logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**AI Video Task Manager** is a complete workflow automation system for managing video tutorial creation tasks with intelligent reminder escalation (Email → WhatsApp → IVR).

---

## ✨ Features

- 📋 **Task Management** – Create, update, delete, and track video tasks
- 🎯 **Auto Stage Creation** – 6 workflow stages automatically created per task
- 📧 **Smart Reminders** – Email, WhatsApp, and IVR escalation based on delay
- 📊 **Real-time Reports** – Complete task-stage joined reports
- 👤 **User Authentication** – Secure login with role-based access
- 🔔 **Auto Scheduler** – Daily reminder checks at 9:00 AM

---

## 🛠️ Tech Stack

- **Frontend**: HTML, CSS, Bootstrap, JavaScript
- **Backend**: Python (FastAPI)
- **Database**: SQLite (scalable to PostgreSQL)
- **ORM**: SQLAlchemy
- **Email**: SMTP (Gmail)
- **Scheduler**: APScheduler

---

## 📁 Folder Structure
---
```
Ai_Video_Task_manager/
├── static/
│ ├── css/
│ │ └── style.css
│ ├── js/
│ │ └── app.js
│ ├── index.html
│ └── login.html
├── routers/
│ ├── task.py
│ ├── stage.py
│ └── report.py
├── services/
│ ├── email_service.py
│ └── reminder_service.py
├── main.py
├── database.py
├── models.py
├── schemas.py
├── requirements.txt
├── .env
└── README.md

````
 ⚙️ Getting Started

---

### 1. Clone the repo
```
git clone https://github.com/dj-ayush/MetaSynAI.git
cd MetaSynAI
```

### 2. Create & activate a virtual environment

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```env
DATABASE_URL=sqlite:///./ai_video_tasks.db
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
DEBUG=True
```

### 5. Initialize database
```bash
python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### 6. Run the app
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Open in browser
```
http://localhost:8000
```

### Default Login
```
Email: ayushgupta.7ag@gmail.com
Password: admin123
```

## 🤝 Contributing

We welcome contributions!

1. Fork the repo
2. Create a new branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m "Added feature"`
4. Push to your branch: `git push origin feature-name`
5. Create a pull request 🚀

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

> Built with ❤️ by [@dj-ayush](https://github.com/dj-ayush)

