# Smart Attendance System – QR Code
## Pharos University | CS405 | Cloud Computing

---

## 🚀 تشغيل المشروع (خطوة واحدة)

```bash
docker-compose up --build
```

بعد التشغيل افتح المتصفح على:
- **الواجهة**: http://localhost:3000
- **API**: http://localhost:5000

---

## 👤 حسابات تجريبية

| النوع | الرقم | كلمة المرور |
|-------|-------|-------------|
| طالب | S001 | 1234 |
| طالب | S002 | 1234 |
| طالب | S003 | 1234 |
| دكتور | INST001 | admin |

---

## 📁 هيكل المشروع

```
attendance-system/
├── docker-compose.yml          # يشغل الـ 3 containers
├── backend/
│   ├── Dockerfile              # Backend container
│   ├── app.py                  # Flask API
│   └── requirements.txt
└── frontend/
    ├── Dockerfile              # Frontend container
    ├── server.py               # Flask static server
    ├── requirements.txt
    ├── templates/
    │   └── index.html          # الواجهة الرئيسية
    └── static/
        ├── css/style.css
        └── js/app.js
```

---

## 🐳 Docker Requirements (المطلوبة في التقييم)

| # | المتطلب | الملف |
|---|---------|-------|
| 1 | docker-compose.yml يشغل 3 containers | `docker-compose.yml` |
| 2 | Dockerfile منفصل للـ Frontend والـ Backend | `*/Dockerfile` |
| 3 | Database container + Volume | `docker-compose.yml` → `mysql_data` |
| 4 | depends_on لترتيب التشغيل | `docker-compose.yml` → `depends_on` |
| 5 | Shared Docker Network | `docker-compose.yml` → `attendance_network` |

---

## 🗄️ قاعدة البيانات

| الجدول | الوصف |
|--------|-------|
| `students` | بيانات الطلاب |
| `qr_codes` | الأكواد مع وقت الانتهاء |
| `attendance_records` | سجل الحضور |

---

## 📡 API Endpoints

| Method | Endpoint | الوصف |
|--------|----------|-------|
| POST | /api/login | تسجيل الدخول |
| POST | /api/logout | الخروج |
| POST | /api/generate-qr | توليد QR (دكتور) |
| POST | /api/checkin | تسجيل الحضور |
| GET | /api/sessions | قائمة الجلسات |
| GET | /api/session/:id/attendance | حضور جلسة |
| GET | /api/student/:id/attendance | حضور طالب |
| GET | /api/stats | إحصائيات عامة |

---

## ⚙️ إيقاف المشروع

```bash
docker-compose down
```

لحذف البيانات أيضاً:
```bash
docker-compose down -v
```
