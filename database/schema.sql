-- ====================================================================
-- Fitzen - Personal Fitness and Wellness Tracker
-- Database Schema for Supabase (PostgreSQL)
-- ====================================================================
-- Instructions:
-- 1. Open your Supabase Dashboard (https://supabase.com/dashboard)
-- 2. Navigate to "SQL Editor" from the left menu
-- 3. Paste this entire script and click "RUN"
-- ====================================================================

-- --------------------------------------------------------------------
-- 1. PROFILES TABLE
-- Stores user profile metadata linked to Supabase Auth (auth.users)
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT,
    fitness_goal TEXT CHECK (fitness_goal IN ('Weight Loss', 'Muscle Gain', 'General Fitness', 'Endurance', 'Flexibility')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::TEXT, NOW()) NOT NULL
);

-- --------------------------------------------------------------------
-- 2. BMI RECORDS TABLE
-- Tracks user body metrics and calculated BMI records over time
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.bmi_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    height_cm NUMERIC(5, 2) NOT NULL CHECK (height_cm > 0),
    weight_kg NUMERIC(5, 2) NOT NULL CHECK (weight_kg > 0),
    bmi_value NUMERIC(4, 1) NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('Underweight', 'Normal weight', 'Overweight', 'Obese')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::TEXT, NOW()) NOT NULL
);

-- --------------------------------------------------------------------
-- 3. WORKOUT LOGS TABLE
-- Records daily physical exercise, duration, and target fitness goal
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.workout_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    workout_name TEXT NOT NULL,
    goal_category TEXT NOT NULL,
    duration_mins INTEGER NOT NULL CHECK (duration_mins > 0),
    date_logged DATE DEFAULT CURRENT_DATE NOT NULL
);

-- --------------------------------------------------------------------
-- 4. FOOD LOGS TABLE
-- Records daily nutritional intake, calories, and meal categories
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.food_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    food_item TEXT NOT NULL,
    calories INTEGER NOT NULL CHECK (calories >= 0),
    meal_type TEXT NOT NULL CHECK (meal_type IN ('Breakfast', 'Lunch', 'Dinner', 'Snacks')),
    date_logged DATE DEFAULT CURRENT_DATE NOT NULL
);

-- ====================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- Ensure that logged-in users can only read and write their own data.
-- ====================================================================

-- Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bmi_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workout_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.food_logs ENABLE ROW LEVEL SECURITY;

-- --------------------------------------------------------------------
-- Policies for: PROFILES
-- --------------------------------------------------------------------
DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
CREATE POLICY "Users can view own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can insert own profile" ON public.profiles;
CREATE POLICY "Users can insert own profile"
    ON public.profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

-- --------------------------------------------------------------------
-- Policies for: BMI RECORDS
-- --------------------------------------------------------------------
DROP POLICY IF EXISTS "Users can view own BMI records" ON public.bmi_records;
CREATE POLICY "Users can view own BMI records"
    ON public.bmi_records FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own BMI records" ON public.bmi_records;
CREATE POLICY "Users can insert own BMI records"
    ON public.bmi_records FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own BMI records" ON public.bmi_records;
CREATE POLICY "Users can delete own BMI records"
    ON public.bmi_records FOR DELETE
    USING (auth.uid() = user_id);

-- --------------------------------------------------------------------
-- Policies for: WORKOUT LOGS
-- --------------------------------------------------------------------
DROP POLICY IF EXISTS "Users can view own workout logs" ON public.workout_logs;
CREATE POLICY "Users can view own workout logs"
    ON public.workout_logs FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own workout logs" ON public.workout_logs;
CREATE POLICY "Users can insert own workout logs"
    ON public.workout_logs FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own workout logs" ON public.workout_logs;
CREATE POLICY "Users can delete own workout logs"
    ON public.workout_logs FOR DELETE
    USING (auth.uid() = user_id);

-- --------------------------------------------------------------------
-- Policies for: FOOD LOGS
-- --------------------------------------------------------------------
DROP POLICY IF EXISTS "Users can view own food logs" ON public.food_logs;
CREATE POLICY "Users can view own food logs"
    ON public.food_logs FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own food logs" ON public.food_logs;
CREATE POLICY "Users can insert own food logs"
    ON public.food_logs FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own food logs" ON public.food_logs;
CREATE POLICY "Users can delete own food logs"
    ON public.food_logs FOR DELETE
    USING (auth.uid() = user_id);

-- --------------------------------------------------------------------
-- OPTIONAL: Automatic Profile Creation Trigger on Sign-Up
-- Automatically inserts a row into public.profiles whenever a new user
-- registers via Supabase Auth.
-- --------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, full_name, fitness_goal)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
        COALESCE(NEW.raw_user_meta_data->>'fitness_goal', 'General Fitness')
    )
    ON CONFLICT (id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
