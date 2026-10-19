"""
====================================================================
Fitzen – Personal Fitness and Wellness Tracker
Phase 1: Application Entrypoint & Core Logic
====================================================================
This file handles:
1. Environment configuration and Flask initialization
2. Supabase database & authentication client connection
3. Authentication helpers and route protection decorators
4. Health & Fitness calculation helpers (BMI, categories)
5. Route definitions for web pages and data processing
====================================================================
"""

import os
from functools import wraps
from datetime import date
from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)
from supabase import create_client, Client

# ====================================================================
# 1. ENVIRONMENT CONFIGURATION & APP INITIALIZATION
# ====================================================================

# Load environment variables from the .env file
load_dotenv()

# Initialize Flask web application
app = Flask(__name__)

# Configure a secret key used by Flask to securely sign session cookies
app.secret_key = os.getenv("FLASK_SECRET_KEY", "fitzen-dev-secret-key-change-in-production")

# Fetch Supabase configuration credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize the Supabase Client
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY and SUPABASE_URL != "https://your-project-id.supabase.co":
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("[INFO] Supabase client initialized successfully.")
    except Exception as e:
        print(f"[WARNING] Failed to initialize Supabase client: {e}")
else:
    print("[WARNING] Supabase credentials not set or using defaults. Please update .env")


# ====================================================================
# 2. SUPABASE CLIENT HELPER (WITH ROW LEVEL SECURITY SUPPORT)
# ====================================================================

def get_supabase_client() -> Client:
    """
    Returns an instance of the Supabase client.
    If a user is logged in with an active access token in the session,
    the client's PostgREST authorization header is updated so PostgreSQL
    Row Level Security (RLS) policies (auth.uid() = user_id) work properly.
    """
    if not supabase:
        raise RuntimeError("Supabase client is not configured. Check your .env file.")

    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    access_token = session.get("access_token")
    if access_token:
        # Set the JWT bearer token for authenticated RLS queries
        client.postgrest.auth(access_token)
    return client


# ====================================================================
# 3. AUTHENTICATION HELPERS & DECORATORS
# ====================================================================

def login_required(f):
    """
    Decorator function to protect private routes.
    Redirects unauthenticated users to the login page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def register_user(email: str, password: str, full_name: str, fitness_goal: str):
    """
    Registers a new user in Supabase Auth and stores their profile info.
    Returns (user_data, error_message).
    """
    try:
        client = get_supabase_client()
        # Sign up user with email, password, and custom metadata
        response = client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "full_name": full_name,
                    "fitness_goal": fitness_goal
                }
            }
        })

        if response.user:
            # Also create or ensure profile record exists
            try:
                client.table("profiles").upsert({
                    "id": response.user.id,
                    "full_name": full_name,
                    "fitness_goal": fitness_goal
                }).execute()
            except Exception as pe:
                print(f"[DEBUG] Profile creation note: {pe}")

            return response, None
        return None, "Registration failed. Please check your credentials."
    except Exception as e:
        return None, str(e)


def login_user(email: str, password: str):
    """
    Authenticates an existing user via Supabase Auth.
    Returns (auth_response, error_message).
    """
    try:
        client = get_supabase_client()
        response = client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return response, None
    except Exception as e:
        return None, str(e)


# ====================================================================
# 4. HEALTH & FITNESS CALCULATION HELPERS
# ====================================================================

def calculate_bmi(height_cm: float, weight_kg: float) -> float:
    """
    Calculates Body Mass Index (BMI).
    Formula: BMI = weight (kg) / (height (m) ^ 2)
    Returns: BMI rounded to 1 decimal place.
    """
    if height_cm <= 0 or weight_kg <= 0:
        raise ValueError("Height and weight must be positive values.")
    
    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 1)


def get_bmi_category(bmi: float) -> str:
    """
    Classifies a BMI value into standard World Health Organization (WHO) categories.
    """
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25.0:
        return "Normal weight"
    elif 25.0 <= bmi < 30.0:
        return "Overweight"
    else:
        return "Obese"


# ====================================================================
# 5. FLASK ROUTES
# ====================================================================

# --------------------------------------------------------------------
# Route: Public Landing / Home Page
# --------------------------------------------------------------------
@app.route("/")
def home():
    """
    Landing page introducing the Fitzen fitness and wellness application.
    If the user is already logged in, redirect them directly to their dashboard.
    """
    if "user" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


# --------------------------------------------------------------------
# Route: User Registration (Sign-Up)
# --------------------------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    """
    GET: Displays the user registration form.
    POST: Processes registration, creates user in Supabase, and logs them in.
    """
    if "user" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        fitness_goal = request.form.get("fitness_goal", "General Fitness")

        if not email or not password or not full_name:
            flash("All fields are required.", "danger")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("register.html")

        # Call registration helper
        res, error = register_user(email, password, full_name, fitness_goal)

        if error:
            flash(f"Registration Error: {error}", "danger")
            return render_template("register.html")

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# --------------------------------------------------------------------
# Route: User Login
# --------------------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    GET: Displays the login form.
    POST: Authenticates credentials against Supabase Auth and establishes session.
    """
    if "user" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template("login.html")

        res, error = login_user(email, password)

        if error:
            flash(f"Login failed: {error}", "danger")
            return render_template("login.html")

        if res and res.user and res.session:
            # Save user information and session tokens into Flask session
            user_metadata = res.user.user_metadata or {}
            session["user"] = {
                "id": res.user.id,
                "email": res.user.email,
                "full_name": user_metadata.get("full_name", "Fitzen User"),
                "fitness_goal": user_metadata.get("fitness_goal", "General Fitness")
            }
            session["access_token"] = res.session.access_token

            flash(f"Welcome back, {session['user']['full_name']}!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid credentials. Please try again.", "danger")
        return render_template("login.html")

    return render_template("login.html")


# --------------------------------------------------------------------
# Route: User Logout
# --------------------------------------------------------------------
@app.route("/logout")
def logout():
    """
    Clears the Flask session and logs the user out from Supabase Auth.
    """
    try:
        if supabase:
            supabase.auth.sign_out()
    except Exception as e:
        print(f"[DEBUG] Logout sign_out notice: {e}")

    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("login"))


# --------------------------------------------------------------------
# Route: User Dashboard
# --------------------------------------------------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    """
    Displays the user dashboard containing summaries of BMI, workouts,
    daily calories, and progress statistics.
    """
    user_id = session["user"]["id"]
    recent_workouts = []
    latest_bmi = None
    today_calories = 0

    try:
        client = get_supabase_client()

        # Fetch latest BMI record
        bmi_resp = client.table("bmi_records")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()
        if bmi_resp.data:
            latest_bmi = bmi_resp.data[0]

        # Fetch recent workout logs
        workout_resp = client.table("workout_logs")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("date_logged", desc=True)\
            .limit(5)\
            .execute()
        recent_workouts = workout_resp.data or []

        # Fetch today's calorie logs
        today_str = str(date.today())
        food_resp = client.table("food_logs")\
            .select("calories")\
            .eq("user_id", user_id)\
            .eq("date_logged", today_str)\
            .execute()
        if food_resp.data:
            today_calories = sum(item.get("calories", 0) for item in food_resp.data)

    except Exception as e:
        print(f"[ERROR] Failed to fetch dashboard data: {e}")
        flash("Could not fetch some dashboard metrics.", "warning")

    return render_template(
        "dashboard.html",
        user=session["user"],
        latest_bmi=latest_bmi,
        recent_workouts=recent_workouts,
        today_calories=today_calories
    )


# --------------------------------------------------------------------
# Route: BMI Calculator and Tracker
# --------------------------------------------------------------------
@app.route("/bmi", methods=["GET", "POST"])
@login_required
def bmi():
    """
    GET: Displays the BMI calculator form and user's historical BMI logs.
    POST: Calculates BMI, categorizes result, and stores record in Supabase.
    """
    user_id = session["user"]["id"]
    calculated_result = None

    if request.method == "POST":
        try:
            height_cm = float(request.form.get("height_cm", 0))
            weight_kg = float(request.form.get("weight_kg", 0))

            bmi_val = calculate_bmi(height_cm, weight_kg)
            category = get_bmi_category(bmi_val)

            # Insert into Supabase bmi_records table
            client = get_supabase_client()
            client.table("bmi_records").insert({
                "user_id": user_id,
                "height_cm": height_cm,
                "weight_kg": weight_kg,
                "bmi_value": bmi_val,
                "category": category
            }).execute()

            calculated_result = {
                "height_cm": height_cm,
                "weight_kg": weight_kg,
                "bmi_value": bmi_val,
                "category": category
            }
            flash("BMI calculated and saved successfully!", "success")

        except ValueError:
            flash("Please enter valid positive numbers for height and weight.", "danger")
        except Exception as e:
            flash(f"Error saving BMI record: {e}", "danger")

    # Fetch user's historical BMI records
    records = []
    try:
        client = get_supabase_client()
        resp = client.table("bmi_records")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .execute()
        records = resp.data or []
    except Exception as e:
        print(f"[ERROR] Failed to fetch BMI records: {e}")

    return render_template("bmi.html", records=records, result=calculated_result)


# --------------------------------------------------------------------
# Route: Workout Logs & Routines
# --------------------------------------------------------------------
@app.route("/workouts", methods=["GET", "POST"])
@login_required
def workouts():
    """
    GET: Displays logged workouts and exercise recommendations.
    POST: Logs a new workout into Supabase.
    """
    user_id = session["user"]["id"]

    if request.method == "POST":
        workout_name = request.form.get("workout_name", "").strip()
        goal_category = request.form.get("goal_category", "General Fitness")
        duration_mins = request.form.get("duration_mins", 0)
        date_logged = request.form.get("date_logged") or str(date.today())

        try:
            duration_mins = int(duration_mins)
            if not workout_name or duration_mins <= 0:
                flash("Workout name and a positive duration are required.", "danger")
            else:
                client = get_supabase_client()
                client.table("workout_logs").insert({
                    "user_id": user_id,
                    "workout_name": workout_name,
                    "goal_category": goal_category,
                    "duration_mins": duration_mins,
                    "date_logged": date_logged
                }).execute()
                flash("Workout logged successfully!", "success")
        except ValueError:
            flash("Duration must be a valid whole number in minutes.", "danger")
        except Exception as e:
            flash(f"Error logging workout: {e}", "danger")

    # Fetch workouts for this user
    workout_list = []
    try:
        client = get_supabase_client()
        resp = client.table("workout_logs")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("date_logged", desc=True)\
            .execute()
        workout_list = resp.data or []
    except Exception as e:
        print(f"[ERROR] Failed to fetch workouts: {e}")

    return render_template("workouts.html", workouts=workout_list)


# --------------------------------------------------------------------
# Route: Diet & Nutrition Recommendations
# --------------------------------------------------------------------
@app.route("/diet")
@login_required
def diet():
    """
    Displays tailored nutritional guidance and meal suggestions
    based on the user's fitness goal.
    """
    fitness_goal = session["user"].get("fitness_goal", "General Fitness")
    return render_template("diet.html", fitness_goal=fitness_goal)


# --------------------------------------------------------------------
# Route: Calorie Tracker & Food Logging
# --------------------------------------------------------------------
@app.route("/calorie-tracker", methods=["GET", "POST"])
@login_required
def calorie_tracker():
    """
    GET: Displays food intake log and total daily calories consumed.
    POST: Adds a new food item and its calorie value.
    """
    user_id = session["user"]["id"]

    if request.method == "POST":
        food_item = request.form.get("food_item", "").strip()
        calories = request.form.get("calories", 0)
        meal_type = request.form.get("meal_type", "Snacks")
        date_logged = request.form.get("date_logged") or str(date.today())

        try:
            calories = int(calories)
            if not food_item or calories < 0:
                flash("Valid food item and non-negative calories required.", "danger")
            else:
                client = get_supabase_client()
                client.table("food_logs").insert({
                    "user_id": user_id,
                    "food_item": food_item,
                    "calories": calories,
                    "meal_type": meal_type,
                    "date_logged": date_logged
                }).execute()
                flash("Food item logged successfully!", "success")
        except ValueError:
            flash("Calories must be a valid number.", "danger")
        except Exception as e:
            flash(f"Error logging food: {e}", "danger")

    # Fetch user's food logs
    food_list = []
    total_today = 0
    today_str = str(date.today())

    try:
        client = get_supabase_client()
        resp = client.table("food_logs")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("date_logged", desc=True)\
            .execute()
        food_list = resp.data or []

        # Calculate today's total calories
        total_today = sum(
            item["calories"] for item in food_list if str(item.get("date_logged")) == today_str
        )
    except Exception as e:
        print(f"[ERROR] Failed to fetch food logs: {e}")

    return render_template(
        "calorie_tracker.html",
        food_logs=food_list,
        total_today=total_today,
        today_date=today_str
    )


# --------------------------------------------------------------------
# Route: Delete Food Log Entry
# --------------------------------------------------------------------
@app.route("/calorie-tracker/delete/<log_id>", methods=["POST", "GET"])
@login_required
def delete_food_log(log_id):
    """
    Deletes a specific food log record belonging to the logged-in user.
    """
    user_id = session["user"]["id"]
    try:
        client = get_supabase_client()
        client.table("food_logs")\
            .delete()\
            .eq("id", log_id)\
            .eq("user_id", user_id)\
            .execute()
        flash("Food entry removed successfully.", "info")
    except Exception as e:
        flash(f"Error removing food entry: {e}", "danger")

    return redirect(url_for("calorie_tracker"))



# --------------------------------------------------------------------
# Route: Progress Overview & Analytics
# --------------------------------------------------------------------
@app.route("/progress")
@login_required
def progress():
    """
    Provides comprehensive historical progress over time:
    BMI trajectory, total workout minutes, and average daily calories.
    """
    user_id = session["user"]["id"]
    bmi_history = []
    workout_history = []
    food_history = []

    try:
        client = get_supabase_client()

        # Fetch BMI history
        bmi_resp = client.table("bmi_records")\
            .select("created_at, bmi_value, weight_kg")\
            .eq("user_id", user_id)\
            .order("created_at", desc=False)\
            .execute()
        bmi_history = bmi_resp.data or []

        # Fetch Workout history
        workout_resp = client.table("workout_logs")\
            .select("date_logged, duration_mins, workout_name")\
            .eq("user_id", user_id)\
            .order("date_logged", desc=False)\
            .execute()
        workout_history = workout_resp.data or []

        # Fetch Food history
        food_resp = client.table("food_logs")\
            .select("date_logged, calories")\
            .eq("user_id", user_id)\
            .order("date_logged", desc=False)\
            .execute()
        food_history = food_resp.data or []

    except Exception as e:
        print(f"[ERROR] Failed to load progress data: {e}")
        flash("Could not fetch complete progress analytics.", "warning")

    return render_template(
        "progress.html",
        bmi_history=bmi_history,
        workout_history=workout_history,
        food_history=food_history
    )


# ====================================================================
# APPLICATION ENTRYPOINT (For local development)
# ====================================================================
if __name__ == "__main__":
    # Run the Flask development server on port 5000 with debug mode enabled
    app.run(debug=True, host="127.0.0.1", port=5000)
