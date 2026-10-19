# 🌿 Fitzen – Personal Fitness and Wellness Tracker

A full-stack, responsive web application designed to help individuals monitor, assess, and improve their physical health and daily wellness. Fitzen features Body Mass Index (BMI) screening, goal-based workout tracking, personalized nutritional blueprints, daily calorie logging, and interactive habit analytics.

---

## 📌 Table of Contents
1. [Project Overview](#-project-overview)
2. [Key Features](#-key-features)
3. [Tech Stack](#-tech-stack)
4. [Prerequisites](#-prerequisites)
5. [Project Architecture](#-project-architecture)
6. [Step-by-Step Setup Guide](#-step-by-step-setup-guide)
7. [Supabase Database Setup](#-supabase-database-setup)
8. [Environment Configuration](#-environment-configuration)
9. [Running the Application](#-running-the-application)
10. [Troubleshooting & FAQs](#-troubleshooting--faqs)

---

## 📖 Project Overview

**Fitzen** was created to address the fragmented nature of personal health tracking. Instead of juggling separate tools for BMI screening, gym workout logs, calorie counts, and nutrition advice, Fitzen unifies them into a single, cohesive, and secure dashboard.

Built using **Python Flask** and **Supabase (PostgreSQL)**, it enforces **Row Level Security (RLS)** to protect user health records and provides interactive visual feedback using **Chart.js** and **Bootstrap 5**.

---

## ✨ Key Features

- **🔐 User Authentication & Session Security**: Secure user registration and login powered by Supabase Auth with server-side session management and `@login_required` route protection.
- **📊 Real-time Dashboard**: Quick-access wellness snapshot featuring current BMI, today's calorie consumption, workout session totals, and daily lifestyle tips.
- **⚖️ BMI Calculator & Historical Tracker**: Computes Body Mass Index ($\text{BMI} = \frac{\text{weight in kg}}{(\text{height in m})^2}$), displays WHO classification badges (`Underweight`, `Normal weight`, `Overweight`, `Obese`), provides clear screening disclaimers, and archives past calculations.
- **🏋️ Workout Routines & Logging**: Curated preset routines across four fitness goals (*General Fitness*, *Strength & Muscle Gain*, *Weight Loss & HIIT*, *Endurance & Mobility*) with single-click form auto-filling and custom activity logging.
- **🥗 Goal-Based Nutrition Guide**: Scientific dietary principles (protein priorities, hydration targets, and dietary fiber) accompanied by targeted meal plans across Breakfast, Lunch, Dinner, and Snacks.
- **🍎 Daily Calorie Tracker**: Fast food item logger with live meal-type filtering (*Breakfast*, *Lunch*, *Dinner*, *Snacks*), daily calorie summation, and delete capability.
- **📈 Progress & Habit Analytics**: Visual trends powered by Chart.js displaying daily calorie intake curves, workout duration bar charts, and long-term BMI progression.

---

## 🛠️ Tech Stack

| Layer | Technologies Used |
|---|---|
| **Frontend** | HTML5, Vanilla CSS3 (Custom Design System), Bootstrap 5.3, Bootstrap Icons |
| **Data Visualization** | Chart.js 4.x (Responsive Canvas Charts) |
| **Backend Framework** | Python 3.8+, Flask 3.x (Jinja2 Templates, Sessions, Flash messaging) |
| **Database & Auth** | Supabase (Managed PostgreSQL, GoTrue Auth, PostgREST API) |
| **Database Security** | PostgreSQL Row Level Security (RLS) with JWT Bearer Token validation |
| **Environment Management** | `python-dotenv` |
| **Deployment / Server** | Gunicorn (WSGI support included) |

---

## 📋 Prerequisites

Before running the project, ensure you have installed:

1. **Python 3.8 or higher**:
   - Check version in terminal:
     ```bash
     python --version
     # or on macOS/Linux:
     python3 --version
     ```
2. **Git**:
   - Check version: `git --version`
3. **Free Supabase Account**:
   - Sign up at [https://supabase.com](https://supabase.com) (no credit card required).

---

## 📂 Project Architecture

```text
fitzen/
│
├── database/
│   └── schema.sql             # PostgreSQL tables, RLS policies, and triggers
│
├── static/
│   ├── css/
│   │   └── style.css          # Custom styling, emerald/teal theme, cards, badges
│   └── js/
│       └── script.js          # Auto-dismiss alerts, preset fillers, meal filters, Chart.js
│
├── templates/
│   ├── base.html              # Core layout, responsive navbar, flash notifications, footer
│   ├── index.html             # Landing page with hero section & feature highlights
│   ├── login.html             # Authentication form (Sign In)
│   ├── register.html          # Registration form with goal selector
│   ├── dashboard.html         # User overview dashboard with metric cards & quick actions
│   ├── bmi.html               # BMI calculator, WHO reference table, and history
│   ├── workouts.html          # Preset workout routines & activity logger
│   ├── diet.html              # Nutrition guidelines & goal meal architecture
│   ├── calorie_tracker.html   # Food item logger, daily total, and meal filters
│   └── progress.html          # Interactive Chart.js charts & progress metrics
│
├── .env.example               # Template for environment variables
├── .gitignore                 # Excludes cache, venv, and secret environment files
├── app.py                     # Flask application entrypoint, helpers, and routes
├── requirements.txt           # Python package dependencies
└── README.md                  # Complete project documentation
```

---

## 🚀 Step-by-Step Setup Guide

### Step 1: Clone or Navigate to the Project Directory

```bash
cd path/to/fitzen
```

### Step 2: Create a Python Virtual Environment

It is strongly recommended to isolate dependencies inside a virtual environment.

- **On Windows (Command Prompt or PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  ```

- **On macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

*(When activated, your terminal prompt will show `(venv)` at the beginning).*

### Step 3: Install Required Python Packages

```bash
pip install -r requirements.txt
```

---

## 🗄️ Supabase Database Setup

1. **Create a New Project on Supabase**:
   - Go to your [Supabase Dashboard](https://supabase.com/dashboard).
   - Click **"New Project"**.
   - Give your project a name (e.g., `fitzen-db`), choose a strong database password, and pick the closest region.

2. **Execute Database Schema**:
   - In your Supabase project dashboard, open the **SQL Editor** tab from the left sidebar.
   - Click **"New query"**.
   - Copy the entire contents of [`database/schema.sql`](database/schema.sql) and paste it into the editor.
   - Click **"Run"** (or press `Ctrl+Enter`).
   - You should see `Success. No rows returned`. This creates:
     * `profiles` (User profile and goal tracking)
     * `bmi_records` (Body mass metrics and categories)
     * `workout_logs` (Workout sessions and durations)
     * `food_logs` (Meals, calories, and categories)
     * **Row Level Security (RLS)** policies for each table.

3. **Retrieve Supabase API Credentials**:
   - In Supabase, go to **Project Settings** (gear icon at the bottom left) $\rightarrow$ **API**.
   - Find and copy:
     * **Project URL** (e.g., `https://xyzprojectid.supabase.co`)
     * **Project API Keys** $\rightarrow$ `anon` / `public` key.

---

## ⚙️ Environment Configuration

1. Create a `.env` file in the root of the project by copying `.env.example`:

   - **On Windows:**
     ```cmd
     copy .env.example .env
     ```
   - **On macOS / Linux:**
     ```bash
     cp .env.example .env
     ```

2. Open `.env` in any text editor and fill in your values:

   ```env
   # Flask Session Secret (replace with any long random string)
   FLASK_SECRET_KEY=fitzen_super_secret_session_key_2026_xyz!

   # Supabase Credentials (from Step 7 above)
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your_supabase_anon_public_key_here
   ```

> **Tip:** You can generate a cryptographically strong Flask secret key in your terminal by running:
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

---

## 🏃 Running the Application

1. Make sure your virtual environment is active:
   ```bash
   # Windows:
   .\venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

2. Start the Flask server:
   ```bash
   python app.py
   ```

3. Launch your browser and visit:
   ```
   http://127.0.0.1:5000
   ```

4. **Test the Workflow**:
   - Click **"Get Started Free"** or **"Register"** to create an account.
   - Enter your name, email, password, and primary fitness goal.
   - Sign in and explore your personal dashboard, calculate your BMI, log workout routines, view nutrition plans, and track your daily calories!

---

## ❓ Troubleshooting & FAQs

### 1. `ModuleNotFoundError: No module named 'flask'` (or `supabase`)
- **Cause**: The dependencies were installed outside the virtual environment, or the virtual environment is not active.
- **Solution**: Ensure `(venv)` is visible in your terminal prompt. Run `pip install -r requirements.txt` again.

### 2. Supabase Initialization Warning (`[WARNING] Supabase credentials not set...`)
- **Cause**: The `.env` file is missing or still contains the placeholder URL `https://your-project-id.supabase.co`.
- **Solution**: Check that the `.env` file is in the root directory (same level as `app.py`) and has your actual Supabase URL and Anon key.

### 3. RLS / Permission Denied Errors in Supabase
- **Cause**: Row Level Security is rejecting an unauthenticated query.
- **Solution**: Ensure you are logged into Fitzen through the web interface. Fitzen automatically passes the user's Supabase JWT access token to authenticate queries so that `auth.uid() = user_id` policies succeed.

### 4. PowerShell Execution Policy Restriction on Windows
- If running `.\venv\Scripts\activate` throws an execution policy error:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
  Then re-run `.\venv\Scripts\activate`.

---

## 📄 License
This project is open-source and intended for educational, academic, and personal wellness tracking purposes.
