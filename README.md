# n8n-Workflow-Popularity-System-By-SpeakGenie
This project is a backend system that collects, stores, and exposes popularity data for **n8n workflows** from multiple public sources.  
It helps identify which workflows are trending and widely used based on real engagement metrics.

The system was built as part of the **SpeakGenie AI/Tech Internship Technical Assignment**.

---

## 🚀 Features

- Collects popularity data from:
  - **YouTube** (views, likes, comments)
  - **n8n Community Forum** (views, replies, contributors)
- Stores data in **MySQL** using SQLAlchemy ORM
- Exposes data through a **FastAPI REST API**
- Computes **normalized popularity metrics** such as:
  - Like-to-view ratio
  - Comment-to-view ratio
- Supports filtering by:
  - Platform (YouTube / Forum)
  - Country (US / IN)
- API documentation available via Swagger UI

---

## 🏗️ System Architecture
YouTube API ──┐
├── Collectors ──> MySQL ──> FastAPI ──> JSON API
Forum API ───┘
- **Collectors** fetch data from external sources
- **Database** stores normalized workflow data
- **API** exposes popularity insights for consumers

---

## 📂 Project Structure
speakgenie/
├── api/
│ ├── main.py # FastAPI app
│ └── models.py # Database models
├── collectors/
│ ├── youtube_collector.py
│ ├── discourse_collector.py
│ └── trends_collector.py
├── scripts/
│ └── run_all_collectors.py
├── db.py
├── create_tables.py
├── test_fetch.py
├── requirements.txt
└── .env

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository
```bash```
git clone https://github.com/yourusername/n8n-workflow-popularity.git
cd n8n-workflow-popularity


### 2️⃣ Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate

### 3️⃣ Install dependencies
pip install -r requirements.txt

### 🔐 Environment Variables

Create a .env file in the project root:

DB_USER=your_mysql_user
DB_PASS=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=n8n_popularity

YOUTUBE_API_KEY=your_youtube_api_key
DISCOURSE_BASE=https://community.n8n.io

### 🗄️ Database Setup

Make sure MySQL is running and the database exists.

Create tables:

python create_tables.py

### 🔄 Run Data Collectors

This will fetch data from YouTube and the n8n community forum and store it in MySQL.

python -m scripts.run_all_collectors

### Run the API Server
uvicorn api.main:app --reload

### 🌐 Run the API Server
uvicorn api.main:app --reload

Open in browser:
API Docs: http://127.0.0.1:8000/docs
Health Check: http://127.0.0.1:8000/health

### 🔍 Example API Usage
# Get workflows
GET /workflows

# Filter by platform
GET /workflows?platform=YouTube

# Filter by country
GET /workflows?country=IN

# Limit results
GET /workflows?limit=10

### 📊 Sample Response
{
  "workflow": "Build a Whatsapp AI Agent for appointment handling",
  "platform": "YouTube",
  "country": "US",
  "popularity_metrics": {
    "views": 761865,
    "likes": 19764,
    "comments": 402,
    "like_to_view_ratio": 0.0259,
    "comment_to_view_ratio": 0.00052
  }
}

### 🧠 Design Decisions
# Engagement ratios are used instead of raw views to avoid popularity bias
# Region-based data (US / IN) is stored separately
# Collector failures do not stop the pipeline (graceful error handling)
# API is kept lightweight and extensible

### 🚧 Future Improvements
# Enable Google Trends with caching
# Add ranking score across platforms
# Add scheduled automation (cron / GitHub Actions)
# Build a simple frontend dashboard<img width="1919" height="1010" alt="Screenshot 2025-12-16 181421" src="https://github.com/user-attachments/assets/42d89f1d-c428-415d-a599-6344efb13e25" />

### Screenshots
<img width="1919" height="1004" alt="Screenshot 2025-12-16 181406" src="https://github.com/user-attachments/assets/62b200dc-84ef-42b2-a348-d97407e63433" />
<img width="1339" height="446" alt="Screenshot 2025-12-16 181018" src="https://github.com/user-attachments/assets/86e2ef0e-3f18-4de6-841f-72e1f57a82a8" />
<img width="1915" height="952" alt="Screenshot 2025-12-16 181714" src="https://github.com/user-attachments/assets/1ba85eb3-e5c4-42ef-9d8a-ed5e065a7725" />
<img width="1918" height="948" alt="Screenshot 2025-12-16 181645" src="https://github.com/user-attachments/assets/86d4c928-f77b-4af4-816e-52e66034401f" />
<img width="1915" height="948" alt="Screenshot 2025-12-16 181550" src="https://github.com/user-attachments/assets/c26f49bf-c515-41ec-a89f-f412a454e60a" />
