# 🎓 Smart Attendance System – QR Code

<p align="center">

  *Smart • Simple • Secure • Efficient*

</p>

---

## 🌟 About The Project

The **Smart Attendance System** is a web-based application designed to simplify university attendance management using QR code technology.

The system allows instructors to generate QR codes for attendance sessions while students can check in and track their attendance records through an intuitive web interface.

Built with **Flask, MySQL, Docker, and Docker Compose**, this project demonstrates containerization, database integration, service communication, and cloud computing fundamentals.

### ✨ Key Features

- 🔐 **User Authentication** — Separate access for students and instructors.
- 📱 **QR Code Attendance** — Simplified attendance check-in.
- 👨‍🏫 **Session Management** — Create and manage attendance sessions.
- 📊 **Attendance Reports** — View student and session attendance records.
- 📈 **Statistics Dashboard** — Access general attendance statistics.
- 🗄️ **MySQL Database** — Store student and attendance data.
- 🐳 **Dockerized Architecture** — Run the entire application using Docker Compose.
- 💾 **Persistent Storage** — Preserve database data using Docker volumes.
- 🌐 **REST API** — Connect the frontend with the backend.

---

## ⚡ Quick Start

### 🛠️ Prerequisites

Before running the project, make sure you have installed:

- 🐳 [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- 💻 Git (optional, for cloning the repository)

### 🚀 Run the Application

**Step 1:** Open your terminal in the project directory.

**Step 2:** Run the following command:

```bash
docker-compose up --build
```

**Step 3:** Wait for the services to start, then open the application in your browser.

| Service | URL |
|---|---|
| 🌐 Frontend | http://localhost:3000 |
| ⚙️ Backend API | http://localhost:5000 |
| 🗄️ MySQL Database | Internal Docker service |

🎉 **That's it! Your application is ready to test once all services are running.**

---

## 👥 Demo Accounts

Use the following accounts to explore the system.

| Role | User ID | Password |
|---|---|---|
| 🎓 Student | `S001` | `1234` |
| 🎓 Student | `S002` | `1234` |
| 🎓 Student | `S003` | `1234` |
| 👨‍🏫 Instructor | `INST001` | `admin` |

🔒 **Security Note:** These are demonstration credentials only. Use secure password hashing and replace default credentials before any production deployment.

---

## 🏗️ Project Architecture

The application consists of three main services working together through a shared Docker network.

```text
                    🌐 WEB BROWSER
                          |
                          v
                 ┌──────────────────┐
                 │  Frontend 🌐     │
                 │  Flask Server    │
                 │  Port: 3000      │
                 └────────┬─────────┘
                          |
                          v
                 ┌──────────────────┐
                 │  Backend ⚙️      │
                 │  Flask REST API  │
                 │  Port: 5000      │
                 └────────┬─────────┘
                          |
                          v
                 ┌──────────────────┐
                 │  MySQL Database  │
                 │  Port: 3306      │
                 └────────┬─────────┘
                          |
                          v
                    💾 mysql_data

          🐳 Shared Network: attendance_network
```

### 📂 Project Structure

```text
attendance-system/
│
├── 🐳 docker-compose.yml
│
├── ⚙️ backend/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
│
└── 🌐 frontend/
    ├── Dockerfile
    ├── server.py
    ├── requirements.txt
    │
    ├── templates/
    │   └── index.html
    │
    └── static/
        ├── css/
        │   └── style.css
        │
        └── js/
            └── app.js
```

### 📌 Main Components

| Component | Responsibility |
|---|---|
| 🐳 `docker-compose.yml` | Orchestrates all application services. |
| ⚙️ `backend/app.py` | Implements the Flask REST API and business logic. |
| 🌐 `frontend/server.py` | Serves the frontend application. |
| 🎨 `style.css` | Defines the user interface styling. |
| 🖥️ `app.js` | Handles frontend interactions and API requests. |
| 📄 `index.html` | Contains the main application interface. |
| 🗄️ MySQL | Stores application data. |

---

## 🐳 Docker & Cloud Computing Requirements

This project demonstrates the following containerization and orchestration concepts.

| # | Requirement | Implementation |
|---|---|---|
| 1️⃣ | Three separate containers | Frontend, Backend, and Database |
| 2️⃣ | Separate Dockerfiles | Frontend and Backend |
| 3️⃣ | Database container | MySQL service |
| 4️⃣ | Persistent storage | `mysql_data` volume |
| 5️⃣ | Service dependencies | `depends_on` |
| 6️⃣ | Shared networking | `attendance_network` |
| 7️⃣ | Container orchestration | Docker Compose |
| 8️⃣ | Service communication | Internal Docker networking |

💡 *The actual service names, ports, volumes, and networking configuration are defined in `docker-compose.yml`.*

---

## 🗄️ Database Design

The system uses MySQL to organize and manage attendance-related information.

| Table | Description |
|---|---|
| 👨‍🎓 `students` | Stores student and account information according to the implemented schema. |
| 📱 `qr_codes` | Stores QR codes and associated expiration information. |
| 📋 `attendance_records` | Stores student attendance records for individual sessions. |

### 💾 Data Persistence

The `mysql_data` named volume is used to preserve database files beyond the lifecycle of individual containers.

⚠️ Removing the volume with `docker-compose down -v` can permanently delete the stored database data.

---

## 🔌 REST API Endpoints

The backend exposes the following endpoints for application functionality.

| Method | Endpoint | Description |
|---|---|---|
| 🔑 `POST` | `/api/login` | Authenticate a user. |
| 🚪 `POST` | `/api/logout` | Log out a user. |
| 📱 `POST` | `/api/generate-qr` | Generate a QR code for an attendance session. |
| ✅ `POST` | `/api/checkin` | Process student attendance check-in. |
| 📚 `GET` | `/api/sessions` | Retrieve attendance sessions. |
| 📋 `GET` | `/api/session/:id/attendance` | Retrieve attendance for a specific session. |
| 👨‍🎓 `GET` | `/api/student/:id/attendance` | Retrieve a student's attendance history. |
| 📊 `GET` | `/api/stats` | Retrieve general attendance statistics. |

📌 *Request formats, response structures, and authorization rules depend on the actual backend implementation.*

---

## 🔄 How It Works

The attendance process follows a simple workflow:

1. 🌐 The user opens the web application.
2. 🔐 The student or instructor logs in.
3. 👨‍🏫 The instructor generates a QR code for an attendance session.
4. 📱 The student scans the QR code.
5. ⚙️ The backend validates the check-in request.
6. ✅ The attendance record is saved in MySQL.
7. 📊 The instructor can review attendance records and available statistics.

🔒 QR expiration, authorization, and duplicate check-in prevention should be enforced on the backend.

---

## 🧰 Useful Docker Commands

### 🚀 Start the Application

```bash
docker-compose up
```

### 🔨 Build and Start

```bash
docker-compose up --build
```

### ⚡ Run in the Background

```bash
docker-compose up --build -d
```

### 📦 Check Running Containers

```bash
docker-compose ps
```

### 📜 View Logs

```bash
docker-compose logs
```

### 🔍 Follow Logs in Real Time

```bash
docker-compose logs -f
```

### ⚙️ View Backend Logs

```bash
docker-compose logs -f backend
```

### 🌐 View Frontend Logs

```bash
docker-compose logs -f frontend
```

### 🛑 Stop the Application

```bash
docker-compose down
```

### 🧹 Stop and Remove Database Volumes

```bash
docker-compose down -v
```

⚠️ **Warning:** The last command removes Compose-managed volumes, including `mysql_data` when configured as a Compose volume. Back up important data first.

---

## 🛠️ Troubleshooting

### 🔴 Port Already in Use

If ports `3000` or `5000` are occupied, stop the conflicting process or modify the host port mappings in `docker-compose.yml`.

### 🗄️ Database Connection Issues

- Check the MySQL container logs.
- Verify the database credentials and configuration.
- Use the MySQL service name as the hostname from the backend container.
- Ensure the database is ready before processing requests.

### 🌐 Frontend Cannot Connect to the Backend

Check the API URL configured in the frontend. Browser-based requests generally require a host-accessible address, such as `http://localhost:5000`.

### 🔄 Rebuild After Changes

```bash
docker-compose up --build
```

---

## 🔐 Security Recommendations

For a more secure and production-ready application, consider implementing:

- 🔒 Secure password hashing.
- 🛡️ Authentication and authorization for protected endpoints.
- ⏱️ Server-side QR code expiration validation.
- 🚫 Duplicate attendance prevention.
- 🔑 Environment variables or a secrets manager for credentials.
- 🧹 Input validation and parameterized SQL queries.
- 🔐 HTTPS for production deployments.
- 📜 Audit logging and rate limiting.
- ❤️ Database health checks and backend retry logic.

*These are recommended improvements and should not be considered implemented unless verified in the source code.*

---

## 🎯 Project Objectives

- 🐳 Understand Docker containerization.
- ☁️ Apply cloud computing concepts.
- 🔗 Orchestrate multiple services using Docker Compose.
- ⚙️ Develop a Flask REST API.
- 🗄️ Integrate a MySQL database.
- 📱 Implement a QR-based attendance workflow.
- 💾 Configure persistent storage and container networking.
- 📊 Build a web-based attendance management system.

---

## 🎓 Academic Information

| Detail | Information |
|---|---|
| 🏛️ University | Pharos University in Alexandria |
| 📚 Course | CS405 – Cloud Computing |
| 💻 Project | Smart Attendance System – QR Code |
| 🐳 Deployment | Docker & Docker Compose |
| ⚙️ Backend | Python & Flask |
| 🗄️ Database | MySQL |

---

<p align="center">

  **🚀 Smart Attendance. Smarter Campus. 🎓**

  *Developed as part of the CS405 – Cloud Computing course.*

</p>
