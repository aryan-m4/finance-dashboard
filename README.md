# 💰 FinanceIQ — Smart Personal Finance Dashboard

A fully functional personal finance tracker built with Python, Flask, MySQL, and Pandas.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-green)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange)
![Pandas](https://img.shields.io/badge/Pandas-2.x-purple)

---

## 🚀 Features

- 📊 **Dashboard** — Visual spending analytics with charts
- 📋 **Expense Tracker** — Add, edit, delete expenses
- 🤖 **AI Insights** — Rule-based spending suggestions powered by Pandas
- 🔐 **Authentication** — Register/Login with bcrypt password hashing
- 🎲 **Demo Mode** — Load sample dataset instantly
- 🌙 **Dark/Light Mode** — Toggle themes
- 📱 **Responsive** — Works on mobile and desktop

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML, CSS, JavaScript, Chart.js |
| Backend | Python, Flask |
| Database | MySQL |
| Analytics | Pandas, NumPy |
| Auth | Flask Sessions, bcrypt |

---

## 📁 Project Structure

```
finance-dashboard/
├── static/
│   ├── css/style.css        # All styles + dark mode
│   └── js/app.js            # Frontend logic
├── templates/
│   ├── auth.html            # Login + Register page
│   ├── welcome.html         # Welcome screen
│   └── index.html           # Main dashboard
├── data/
│   └── demo_data.csv        # Sample expense dataset
├── analytics.py             # Pandas analytics engine
├── app.py                   # Flask backend + API routes
├── schema.sql               # MySQL schema
├── requirements.txt         # Python dependencies
└── .env.example             # Environment variables template
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/finance-dashboard.git
cd finance-dashboard
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup MySQL
- Open MySQL Workbench
- Run `schema.sql` to create database and tables

### 5. Configure environment
```bash
cp .env.example .env
# Edit .env with your MySQL password
```

### 6. Run the app
```bash
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register` | Create new account |
| POST | `/api/login` | Login |
| POST | `/api/logout` | Logout |
| GET | `/api/expenses` | Get all expenses |
| POST | `/api/expenses` | Add expense |
| PUT | `/api/expenses/<id>` | Edit expense |
| DELETE | `/api/expenses/<id>` | Delete expense |
| GET | `/api/analytics` | Get analytics data |
| POST | `/api/demo` | Load demo data |
| DELETE | `/api/demo` | Clear demo data |

---

## 📸 Screenshots

> Dashboard with charts, expense table, AI insights and dark mode.

---

## 👨‍💻 Author

Built with ❤️ using Python, Flask, MySQL and Pandas.

---

## 📄 License

MIT License — free to use and modify.