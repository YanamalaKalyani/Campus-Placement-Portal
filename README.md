# 🎓 Campus Placement Portal

A modern web-based platform designed to streamline and digitize the entire campus recruitment process with dedicated dashboards for Admins, Students, and Companies.

---

## ✨ Features

### 👨‍💼 Admin Dashboard
- 📊 Real-time Statistics (students, companies, placement %)
- 📈 Visual Analytics (salary distribution, branch-wise performance)
- 🏢 Manage Companies (update roles, packages, profiles)
- 👨‍🎓 Manage Students (academic records, resumes, placement status)
- 📢 Send Notifications to targeted users
- 📅 Monitor Placement Drives & Progress

### 🎓 Student Dashboard
- 👤 Personalized Profile (CGPA, placement status)
- 🏢 View Eligible Companies
- ✅ Apply for Jobs directly
- 📄 Upload & Manage Resume
- 📊 Track Application Status (shortlisted/accepted/rejected)
- 🔔 Receive Real-time Notifications

### 🏢 Company Dashboard
- 📥 View Applications & Student Profiles
- 📄 Download Resumes
- ✅ Shortlist Candidates
- 📊 Recruitment Analytics Dashboard
- 📈 Application Status Distribution
- 📅 Track Monthly Application Trends
- ⚙️ Manage Company Profile

---

## 📊 System Highlights
- 🔄 Multi-role Authentication System
- 🎯 Smart Eligibility Filtering
- 📡 Real-time Updates & Notifications
- 📈 Data-driven Decision Making
- 📱 Responsive User Interface

---

## 🛠️ Technologies Used

### 💻 Frontend
- HTML5 & CSS3 (Vanilla) – Core structure and advanced UI styling  
- JavaScript – Handles dynamic UI, API calls, and DOM manipulation  
- Chart.js – Used for analytics dashboards (bar charts, pie charts, trends)  

### ⚙️ Backend
- Python 3 – Core backend language  
- Flask – Lightweight REST API framework

### 🧰 Tools & Utilities
- XAMPP – Local server environment (Apache & MySQL)  
- phpMyAdmin – Database management   

### 🔐 Architecture & Features
- RESTful API Architecture  
- Role-Based Authentication (Admin, Student, Company)  
- MVC Design Pattern  
- Responsive UI Design  
- Data Visualization Dashboard  

---

## ⚙️ How to Run

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```
The server will run at: http://localhost:5000

### Frontend (Web Interface)
```bash
cd frontend
npm install
npm run dev
```
---

## 🔗 API Endpoints

### Authentication
- `POST /login` → User login (Admin / Student / Company)  
- `POST /register` → New user registration  

### Admin APIs
- `GET /admin/dashboard` → Get dashboard statistics  
- `GET /students` → Fetch all students  
- `GET /companies` → Fetch all companies  
- `PUT /student/{id}` → Update student details  
- `POST /notifications` → Send notifications  

### Student APIs
- `GET /jobs` → View available jobs  
- `POST /apply` → Apply for a job  
- `GET /applications` → View application history  
- `PUT /profile` → Update student profile  

### Company APIs
- `POST /jobs` → Create job posting  
- `GET /applications/{job_id}` → View applicants  
- `PUT /application/{id}` → Update application status  
- `GET /analytics` → View recruitment analytics  

---

## 🗄️ Database details

The project uses a MySQL database named **`campus_placement`** to manage all placement-related data including users, students, companies, drives, and applications.

### ⚙️ Backend Technologies
- **Language**: Python 
- **Framework**: Flask
- **Database**: MySQL  
- **API Type**: RESTful APIs

### ⚠️ Important Notes
- Default admin credentials:
  - Email: `admin@campus.edu`
  - Password: `admin123`
- Make sure MySQL server is running before importing  
- Import the provided `schema.sql` file using phpMyAdmin

### 📥 How to Import Database

1. Open phpMyAdmin  
2. Create a new database (e.g., `placement_portal`)  
3. Import the `schema.sql` file  
4. Run the backend server  

---

## 🚀 Usage

### Admin
- Login using admin credentials  
- Manage students, companies, and placement drives  
- View real-time analytics and placement statistics  
- Send notifications to students or companies  
- Update placement status and salary details  

### Student
- Register/Login to the portal  
- View eligible companies based on criteria  
- Apply for jobs directly  
- Upload and update resume  
- Track application status (shortlisted, selected, rejected)  
- Receive real-time notifications  

### Company
- Login to company dashboard  
- Post job openings and manage drives  
- View student applications  
- Shortlist candidates  
- Download resumes  
- Track recruitment progress and analytics  

---

## 📌 Additional Information

### 🔐 Authentication & Security
- Role-based authentication system (Admin, Student, Company)  
- Secure login and session handling  

### 📊 Data & Analytics
- Real-time data visualization for placement stats  
- Salary distribution and performance insights  
- Application tracking and reporting  

### ⚙️ System Capabilities
- Multi-user support  
- Scalable architecture  
- Modular design for easy updates  

### 📈 Why This Project?
- Solves manual placement process issues  
- Improves efficiency and transparency  
- Helps students, admins, and recruiters in one platform  

---

**💼 A brief overview of this project is also available on my LinkedIn profile: 
