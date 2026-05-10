# 🧘 PostureGuard AI — Smart Posture Monitoring System

> An AI-powered web application that monitors your sitting posture in real time using your webcam, detects posture risk levels, sends alerts, and tracks your posture history — helping prevent back pain and sciatica before they start.

---

## 📸 Screenshots

| Login Page | Live Monitor | Dashboard |
|------------|-------------|-----------|
| *(screenshots/login.png)* | *(screenshots/monitor.png)* | *(screenshots/dashboard.png)* |

---

## 🗂️ Project Structure

```
PostureGuardAI/
│
├── backend/                    # Flask REST API
│   ├── app.py                  # Main Flask entry point
│   ├── .env.example            # Environment variable template
│   ├── routes/
│   │   ├── auth.py             # Register & Login routes
│   │   ├── posture.py          # Save/fetch posture data routes
│   │   └── video.py            # Live webcam stream & analysis
│   └── utils/
│       ├── db.py               # MySQL connection helper
│       └── posture_analyzer.py # MediaPipe posture logic
│
├── frontend/                   # React.js frontend
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js              # Root component + routes
│   │   ├── index.js            # React entry point
│   │   ├── index.css           # Global styles
│   │   ├── utils/
│   │   │   └── api.js          # Axios API helper (JWT auto-attach)
│   │   ├── components/
│   │   │   ├── Navbar.js       # Top navigation bar
│   │   │   ├── Navbar.css
│   │   │   ├── RiskBadge.js    # LOW / MEDIUM / HIGH badge
│   │   │   ├── RiskBadge.css
│   │   │   ├── AlertBanner.js  # Alert notification banner
│   │   │   └── AlertBanner.css
│   │   └── pages/
│   │       ├── LoginPage.js    # Login form
│   │       ├── RegisterPage.js # Register form
│   │       ├── AuthPage.css    # Shared auth styles
│   │       ├── MonitorPage.js  # Live monitoring + alerts
│   │       ├── MonitorPage.css
│   │       ├── DashboardPage.js # Charts + history
│   │       └── DashboardPage.css
│   └── package.json
│
├── database/
│   └── schema.sql              # MySQL database schema
│
├── screenshots/                # Add your screenshots here
├── requirements.txt            # Python dependencies
└── README.md
```

---

## ⚙️ Tech Stack

| Layer        | Technology                              |
|-------------|------------------------------------------|
| Frontend     | React.js, Chart.js, CSS, JavaScript     |
| Backend      | Python, Flask, Flask-JWT-Extended        |
| CV / AI      | OpenCV, MediaPipe BlazePose              |
| Database     | MySQL                                    |
| Auth         | JWT Tokens + bcrypt password hashing    |
| HTTP Client  | Axios                                    |

---

## 🚀 Setup Guide (Step by Step)

### Prerequisites
- Python 3.9+ installed
- Node.js 18+ and npm installed
- MySQL installed and running
- A webcam

---

### Step 1 — Clone / Download the Project

```bash
git clone https://github.com/YOUR_USERNAME/PostureGuardAI.git
cd PostureGuardAI
```

---

### Step 2 — Set Up the MySQL Database

Open MySQL and run the schema file:

```bash
mysql -u root -p < database/schema.sql
```

This creates:
- Database: `postureguard`
- Tables: `users`, `posture_sessions`, `posture_records`, `alerts`
- A demo user (`demo_user` / `demo1234`)

---

### Step 3 — Configure the Backend

```bash
cd backend
cp .env.example .env
```

Edit `.env` and fill in your MySQL password:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD
DB_NAME=postureguard
JWT_SECRET_KEY=any-long-random-string-here
```

---

### Step 4 — Install Python Dependencies

```bash
# From the project root:
pip install -r requirements.txt
```

> ⚠️ MediaPipe requires Python 3.9–3.11. It does NOT work on Python 3.12+.
> Check your version: `python --version`

---

### Step 5 — Run the Flask Backend

```bash
cd backend
python app.py
```

You should see:
```
PostureGuard AI Backend Running
URL: http://localhost:5000
```

Test it: open `http://localhost:5000/api/health` in your browser.

---

### Step 6 — Install Frontend Dependencies

Open a **new terminal**:

```bash
cd frontend
npm install
```

---

### Step 7 — Run the React Frontend

```bash
npm start
```

Opens at `http://localhost:3000` automatically.

---

### Step 8 — Use the App

1. Go to `http://localhost:3000`
2. Register an account or use demo: `demo_user` / `demo1234`
3. Click **Monitor** → **Start Monitoring**
4. Sit in front of your webcam
5. The system will:
   - Show your live feed with pose landmarks
   - Detect neck angle and shoulder alignment
   - Display LOW / MEDIUM / HIGH risk badge
   - Alert you if posture is bad
   - Remind you to stretch every 30 minutes
6. Click **Dashboard** to see your history and charts

---

## 🌐 API Routes

### Auth Routes (`/api/auth/`)

| Method | Route       | Description              | Auth Required |
|--------|-------------|--------------------------|---------------|
| POST   | `/register` | Create new account       | No            |
| POST   | `/login`    | Login, get JWT token     | No            |

**Register body:**
```json
{ "username": "john", "email": "john@example.com", "password": "pass123" }
```

**Login body:**
```json
{ "username": "john", "password": "pass123" }
```

**Login response:**
```json
{
  "access_token": "eyJ...",
  "user": { "id": 1, "username": "john", "email": "john@example.com" }
}
```

---

### Posture Routes (`/api/posture/`) — JWT required

| Method | Route             | Description                         |
|--------|-------------------|-------------------------------------|
| POST   | `/save`           | Save a posture snapshot             |
| GET    | `/history`        | Get last 50 posture records         |
| GET    | `/stats`          | Get risk counts for last 7 days     |
| POST   | `/session/start`  | Start a monitoring session          |
| POST   | `/session/end`    | End a session + save total minutes  |
| POST   | `/alert`          | Log an alert shown to user          |

---

### Video Routes (`/api/video/`)

| Method | Route      | Description                              | Auth    |
|--------|------------|------------------------------------------|---------|
| GET    | `/stream`  | MJPEG live webcam stream (pose overlay)  | No      |
| GET    | `/analyze` | Analyze one frame, return JSON data      | JWT     |
| POST   | `/stop`    | Release the webcam                       | No      |

---

## 🗄️ Database Schema

### `users` table
| Column     | Type         | Notes                  |
|------------|--------------|------------------------|
| id         | INT PK       | Auto-increment         |
| username   | VARCHAR(50)  | Unique                 |
| email      | VARCHAR(100) | Unique                 |
| password   | VARCHAR(255) | bcrypt hashed          |
| created_at | DATETIME     | Auto timestamp         |

### `posture_records` table
| Column       | Type                        | Notes                    |
|-------------|-----------------------------|--------------------------|
| id           | INT PK                      |                          |
| user_id      | INT FK → users              |                          |
| session_id   | INT FK → posture_sessions   | Nullable                 |
| risk_level   | ENUM(low, medium, high)     |                          |
| neck_angle   | FLOAT                       | Degrees                  |
| shoulder_diff| FLOAT                       | Pixels                   |
| nose_y       | FLOAT                       | Normalized 0–1           |
| recorded_at  | DATETIME                    | Auto timestamp           |

---

## 🧠 How the AI Posture Detection Works

```
Webcam Frame
     │
     ▼
OpenCV — captures frame, flips horizontally
     │
     ▼
MediaPipe BlazePose — detects 33 body landmarks
     │
     ▼
posture_analyzer.py
  ├── Neck Angle (nose → shoulder → hip triangle)
  │     Good: > 145°   Poor: < 120°
  ├── Shoulder Difference (left vs right y-pixel)
  │     Good: < 25 px   Poor: > 50 px
  └── Risk Classification:
        HIGH   → neck < 120° OR shoulder diff > 50px
        MEDIUM → neck < 145° OR shoulder diff > 25px
        LOW    → all metrics in normal range
     │
     ▼
Draw landmarks on frame → MJPEG stream → Browser <img> tag
     │
     ▼
Every 30 sec → /api/video/analyze → save to MySQL
```

---

## 📦 GitHub Upload Steps

```bash
# 1. Initialize git in project root
cd PostureGuardAI
git init

# 2. Create .gitignore
echo "backend/.env
node_modules/
__pycache__/
*.pyc
.DS_Store
frontend/build/" > .gitignore

# 3. Add all files
git add .

# 4. First commit
git commit -m "Initial commit: PostureGuard AI full stack project"

# 5. Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/PostureGuardAI.git
git branch -M main
git push -u origin main
```

---

## 🎤 Sample Interview Q&A

**Q1: What does this project do?**
> PostureGuard AI is a full-stack web application that uses your webcam and MediaPipe pose estimation to monitor your sitting posture in real time. It classifies your posture risk as Low, Medium, or High based on neck angle and shoulder alignment, sends alerts when posture deteriorates, reminds you to stretch, and saves your history to a MySQL database for trend analysis.

**Q2: How does the posture detection work?**
> I use MediaPipe BlazePose which detects 33 body landmarks in real time. I then calculate the angle at the shoulder joint formed by the nose, shoulder, and hip landmarks — this approximates the neck/forward-head angle. I also measure the pixel difference between left and right shoulder heights to detect sideways leaning. If the neck angle drops below 120° or shoulder difference exceeds 50px, it's High Risk.

**Q3: Why did you choose Flask + React instead of a monolithic app?**
> Separating the backend (Flask) from the frontend (React) follows the modern REST API architecture. Flask handles all the data logic and AI processing, while React handles the UI. This makes the code cleaner, easier to test, and allows the frontend and backend to be developed/deployed independently.

**Q4: How do you handle authentication?**
> I use JWT (JSON Web Tokens). When a user logs in, the Flask backend validates their password (hashed with bcrypt) and returns a JWT token. The React frontend stores this token in localStorage and includes it in every API request via an Axios interceptor. Protected routes in Flask use `@jwt_required()` to verify the token.

**Q5: How is the live video stream served?**
> Flask uses a generator function that continuously reads webcam frames via OpenCV, runs MediaPipe pose detection on each frame, draws landmarks, and yields JPEG bytes in a `multipart/x-mixed-replace` HTTP response. The React frontend simply displays this stream in an `<img>` tag — the browser handles the rest.

**Q6: How would you scale this project?**
> For scaling: deploy Flask on Gunicorn with Nginx, use a managed MySQL instance, add Redis for caching stats, containerise with Docker, and deploy to a cloud provider. The frontend can be built with `npm run build` and served as static files via a CDN. We could also add mobile support using TensorFlow Lite for on-device inference.

**Q7: What are the limitations?**
> The posture detection accuracy depends on camera angle, lighting, and whether the full upper body is visible. The neck angle calculation is a 2D approximation — a 3D IMU sensor would be more accurate. Also, the system is preventive only — it cannot diagnose or treat medical conditions.

---

## 🔮 Future Enhancements

- [ ] Mobile app (React Native + TensorFlow Lite)
- [ ] Email/SMS alerts for high-risk days
- [ ] Weekly PDF report of posture trends
- [ ] Guided stretch video library
- [ ] Multi-user admin panel for employers
- [ ] Wearable sensor integration (IMU)

---

## ⚠️ Disclaimer

PostureGuard AI is a **preventive monitoring tool only**. It does not provide medical diagnosis or treatment advice. Always consult a qualified healthcare professional for any pain or medical condition.

---

## 📄 License

MIT License — free for personal and educational use.
