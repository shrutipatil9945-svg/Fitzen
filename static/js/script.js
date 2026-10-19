/**
 * Fitzen – Personal Fitness and Wellness Tracker
 * Frontend Interactivity and Chart.js Visualizations
 */

document.addEventListener("DOMContentLoaded", () => {
    // -------------------------------------------------------------
    // 1. AUTO-DISMISS FLASH ALERTS
    // -------------------------------------------------------------
    const alertElements = document.querySelectorAll(".alert-dismissible");
    alertElements.forEach((alert) => {
        setTimeout(() => {
            try {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                bsAlert.close();
            } catch (err) {
                alert.style.display = "none";
            }
        }, 5000); // Auto dismiss after 5 seconds
    });

    // -------------------------------------------------------------
    // 2. WORKOUT PRESET AUTO-FILLER
    // -------------------------------------------------------------
    const presetButtons = document.querySelectorAll(".btn-preset-workout");
    const workoutNameInput = document.getElementById("workout_name");
    const durationInput = document.getElementById("duration_mins");
    const goalSelect = document.getElementById("goal_category");

    if (presetButtons.length > 0 && workoutNameInput) {
        presetButtons.forEach((btn) => {
            btn.addEventListener("click", () => {
                const name = btn.getAttribute("data-name");
                const duration = btn.getAttribute("data-duration");
                const goal = btn.getAttribute("data-goal");

                if (name) workoutNameInput.value = name;
                if (duration && durationInput) durationInput.value = duration;
                if (goal && goalSelect) goalSelect.value = goal;

                // Smooth scroll to the form for quick submission
                const formCard = document.getElementById("workout-log-form");
                if (formCard) {
                    formCard.scrollIntoView({ behavior: "smooth", block: "center" });
                    workoutNameInput.focus();
                }
            });
        });
    }

    // -------------------------------------------------------------
    // 3. DIET & MEAL TYPE FILTER (FOR CALORIE TRACKER)
    // -------------------------------------------------------------
    const mealFilterButtons = document.querySelectorAll(".meal-filter-btn");
    const foodTableRows = document.querySelectorAll(".food-log-row");

    if (mealFilterButtons.length > 0 && foodTableRows.length > 0) {
        mealFilterButtons.forEach((btn) => {
            btn.addEventListener("click", () => {
                mealFilterButtons.forEach((b) => b.classList.remove("active"));
                btn.classList.add("active");

                const filter = btn.getAttribute("data-filter");
                foodTableRows.forEach((row) => {
                    const mealType = row.getAttribute("data-meal");
                    if (filter === "all" || mealType === filter) {
                        row.style.display = "";
                    } else {
                        row.style.display = "none";
                    }
                });
            });
        });
    }

    // -------------------------------------------------------------
    // 4. CHART.JS INITIALIZATION FOR PROGRESS PAGE
    // -------------------------------------------------------------
    initProgressCharts();
});

/**
 * Initializes and renders Chart.js charts on the /progress page.
 * Safely parses JSON data passed from Jinja2 templates via data attributes.
 */
function initProgressCharts() {
    const chartsContainer = document.getElementById("fitzen-charts-container");
    if (!chartsContainer) return; // Exit if not on progress page

    // Fetch embedded JSON data attributes
    let calorieData = [];
    let workoutData = [];
    let bmiData = [];

    try {
        calorieData = JSON.parse(chartsContainer.getAttribute("data-calories") || "[]");
        workoutData = JSON.parse(chartsContainer.getAttribute("data-workouts") || "[]");
        bmiData = JSON.parse(chartsContainer.getAttribute("data-bmi") || "[]");
    } catch (e) {
        console.error("Error parsing progress charts data:", e);
    }

    // Common Chart Styling Options
    const chartFont = { family: "'Plus Jakarta Sans', sans-serif", size: 12 };

    // --- CHART A: CALORIE INTAKE TREND (Line Chart) ---
    const calorieCanvas = document.getElementById("calorieTrendChart");
    if (calorieCanvas) {
        if (calorieData.length === 0) {
            renderEmptyChartMessage(calorieCanvas, "No calorie data logged yet. Track your meals to view trend!");
        } else {
            // Aggregate calories by date if multiple entries per day
            const dateMap = {};
            calorieData.forEach((item) => {
                const d = item.date_logged || "Unknown";
                dateMap[d] = (dateMap[d] || 0) + (Number(item.calories) || 0);
            });

            const labels = Object.keys(dateMap);
            const values = Object.values(dateMap);

            new Chart(calorieCanvas, {
                type: "line",
                data: {
                    labels: labels,
                    datasets: [{
                        label: "Daily Calories (kcal)",
                        data: values,
                        borderColor: "#0d9488",
                        backgroundColor: "rgba(13, 148, 136, 0.12)",
                        borderWidth: 3,
                        pointBackgroundColor: "#0d9488",
                        pointRadius: 5,
                        pointHoverRadius: 7,
                        fill: true,
                        tension: 0.35
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { labels: { font: chartFont, color: "#334155" } },
                        tooltip: { padding: 10, cornerRadius: 8 }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { color: "#f1f5f9" },
                            ticks: { font: chartFont, color: "#64748b" }
                        },
                        x: {
                            grid: { display: false },
                            ticks: { font: chartFont, color: "#64748b" }
                        }
                    }
                }
            });
        }
    }

    // --- CHART B: WORKOUT LOGS DURATION (Bar Chart) ---
    const workoutCanvas = document.getElementById("workoutBarChart");
    if (workoutCanvas) {
        if (workoutData.length === 0) {
            renderEmptyChartMessage(workoutCanvas, "No workouts logged yet. Log a workout to see duration stats!");
        } else {
            const workoutLabels = workoutData.map((w) => `${w.workout_name} (${w.date_logged})`);
            const durations = workoutData.map((w) => Number(w.duration_mins) || 0);

            new Chart(workoutCanvas, {
                type: "bar",
                data: {
                    labels: workoutLabels,
                    datasets: [{
                        label: "Workout Duration (Minutes)",
                        data: durations,
                        backgroundColor: "rgba(16, 185, 129, 0.8)",
                        hoverBackgroundColor: "#059669",
                        borderRadius: 8,
                        borderSkipped: false
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { labels: { font: chartFont, color: "#334155" } },
                        tooltip: { padding: 10, cornerRadius: 8 }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { color: "#f1f5f9" },
                            ticks: { font: chartFont, color: "#64748b" }
                        },
                        x: {
                            grid: { display: false },
                            ticks: {
                                font: chartFont,
                                color: "#64748b",
                                maxRotation: 45,
                                minRotation: 0
                            }
                        }
                    }
                }
            });
        }
    }

    // --- CHART C: BMI PROGRESSION (Line Chart) ---
    const bmiCanvas = document.getElementById("bmiProgressChart");
    if (bmiCanvas) {
        if (bmiData.length === 0) {
            renderEmptyChartMessage(bmiCanvas, "No BMI history found. Calculate your BMI to track changes!");
        } else {
            const bmiLabels = bmiData.map((b) => {
                const dateStr = b.created_at ? b.created_at.split("T")[0] : "Date";
                return dateStr;
            });
            const bmiValues = bmiData.map((b) => Number(b.bmi_value) || 0);

            new Chart(bmiCanvas, {
                type: "line",
                data: {
                    labels: bmiLabels,
                    datasets: [{
                        label: "BMI Value",
                        data: bmiValues,
                        borderColor: "#0284c7",
                        backgroundColor: "rgba(2, 132, 199, 0.1)",
                        borderWidth: 3,
                        pointBackgroundColor: "#0284c7",
                        pointRadius: 5,
                        fill: true,
                        tension: 0.25
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { labels: { font: chartFont, color: "#334155" } }
                    },
                    scales: {
                        y: {
                            suggestedMin: 15,
                            suggestedMax: 35,
                            grid: { color: "#f1f5f9" },
                            ticks: { font: chartFont, color: "#64748b" }
                        },
                        x: {
                            grid: { display: false },
                            ticks: { font: chartFont, color: "#64748b" }
                        }
                    }
                }
            });
        }
    }
}

/**
 * Fallback empty chart placeholder message
 */
function renderEmptyChartMessage(canvas, message) {
    const parent = canvas.parentElement;
    if (!parent) return;
    canvas.style.display = "none";
    const placeholder = document.createElement("div");
    placeholder.className = "d-flex flex-column align-items-center justify-content-center h-100 p-4 text-center text-muted";
    placeholder.innerHTML = `
        <i class="bi bi-bar-chart-line text-secondary opacity-50 mb-2" style="font-size: 2.5rem;"></i>
        <p class="mb-0 fw-medium small">${message}</p>
    `;
    parent.appendChild(placeholder);
}
