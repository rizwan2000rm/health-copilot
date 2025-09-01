const express = require("express");
const sqlite3 = require("sqlite3").verbose();
const fs = require("fs");
const csv = require("csv-parser");
const cors = require("cors");
const helmet = require("helmet");
const path = require("path");

// Init the db
const db = new sqlite3.Database("./hevy/api/workouts.db", (err) => {
  if (err) {
    console.error("Error opening database:", err.message);
  } else {
    console.log("Connected to SQLite database.");
    initDatabase();
  }
});

// Initialize database tables
function initDatabase() {
  const createWorkoutsTable = `
    CREATE TABLE IF NOT EXISTS workouts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      start_time TEXT NOT NULL,
      end_time TEXT NOT NULL,
      description TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `;

  const createExercisesTable = `
    CREATE TABLE IF NOT EXISTS exercises (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      workout_id INTEGER,
      exercise_title TEXT NOT NULL,
      superset_id TEXT,
      exercise_notes TEXT,
      set_index INTEGER,
      set_type TEXT,
      weight_kg REAL,
      reps INTEGER,
      distance_km REAL,
      duration_seconds INTEGER,
      rpe INTEGER,
      FOREIGN KEY (workout_id) REFERENCES workouts (id)
    )
  `;

  db.serialize(() => {
    db.run(createWorkoutsTable);
    db.run(createExercisesTable);
    console.log("Database tables created successfully.");

    // Check if data already exists
    db.get("SELECT COUNT(*) as count FROM workouts", (err, row) => {
      if (err) {
        console.error("Error checking data:", err.message);
      } else if (row.count === 0) {
        // Import CSV data only if database is empty
        importCSVData();
      } else {
        console.log("Database already contains data, skipping CSV import.");
        startAPIServer();
      }
    });
  });
}

// Read the csv file workouts.csv
// Import the csv file into the db
function importCSVData() {
  console.log("Starting CSV import...");

  const workouts = new Map(); // key: title_startTime_endTime -> workout_id
  const exercises = [];

  fs.createReadStream("./hevy/api/workouts.csv")
    .pipe(csv())
    .on("data", (row) => {
      // Create a unique key for each workout session (title + start_time + end_time)
      const workoutKey = `${row.title}_${row.start_time}_${row.end_time}`;

      if (!workouts.has(workoutKey)) {
        const workoutId = workouts.size + 1; // Temporary ID for mapping
        workouts.set(workoutKey, {
          id: workoutId,
          title: row.title,
          start_time: row.start_time,
          end_time: row.end_time,
          description: row.description || "",
        });
      }

      const workout = workouts.get(workoutKey);
      const exerciseData = {
        workout_id: workout.id,
        exercise_title: row.exercise_title,
        superset_id: row.superset_id || null,
        exercise_notes: row.exercise_notes || null,
        set_index: parseInt(row.set_index) || 0,
        set_type: row.set_type || "normal",
        weight_kg: row.weight_kg ? parseFloat(row.weight_kg) : null,
        reps: row.reps ? parseInt(row.reps) : null,
        distance_km: row.distance_km ? parseFloat(row.distance_km) : null,
        duration_seconds: row.duration_seconds
          ? parseInt(row.duration_seconds)
          : null,
        rpe: row.rpe ? parseInt(row.rpe) : null,
      };

      exercises.push(exerciseData);
    })
    .on("end", () => {
      console.log("CSV parsing completed. Importing to database...");
      console.log(
        `Found ${workouts.size} workout sessions and ${exercises.length} exercises`
      );

      // Import workouts first
      const workoutValues = Array.from(workouts.values());
      const workoutStmt = db.prepare(
        "INSERT INTO workouts (title, start_time, end_time, description) VALUES (?, ?, ?, ?)"
      );

      workoutValues.forEach((workout, index) => {
        workoutStmt.run(
          workout.title,
          workout.start_time,
          workout.end_time,
          workout.description,
          function (err) {
            if (err) {
              console.error("Error inserting workout:", err.message);
            } else {
              // Store the actual database ID for exercises
              workout.dbId = this.lastID;
            }
          }
        );
      });

      workoutStmt.finalize(() => {
        // Import exercises
        const exerciseStmt = db.prepare(`
          INSERT INTO exercises (workout_id, exercise_title, superset_id, exercise_notes, set_index, set_type, weight_kg, reps, distance_km, duration_seconds, rpe)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `);

        exercises.forEach((exercise) => {
          // Find the corresponding workout by temporary ID
          const workout = Array.from(workouts.values()).find(
            (w) => w.id === exercise.workout_id
          );

          if (workout && workout.dbId) {
            exerciseStmt.run(
              workout.dbId,
              exercise.exercise_title,
              exercise.superset_id,
              exercise.exercise_notes,
              exercise.set_index,
              exercise.set_type,
              exercise.weight_kg,
              exercise.reps,
              exercise.distance_km,
              exercise.duration_seconds,
              exercise.rpe
            );
          }
        });

        exerciseStmt.finalize(() => {
          console.log("CSV import completed successfully!");
          console.log(
            `Imported ${workouts.size} workout sessions and ${exercises.length} exercises`
          );
          startAPIServer();
        });
      });
    })
    .on("error", (error) => {
      console.error("Error reading CSV:", error);
      startAPIServer();
    });
}

// Start the api server
function startAPIServer() {
  const app = express();
  const PORT = process.env.PORT || 3000;

  // Middleware
  app.use(helmet());
  app.use(cors());
  app.use(express.json());

  // Import API routes
  const apiRoutes = require("./api");
  app.use("/api", apiRoutes);

  // Health check endpoint
  app.get("/health", (req, res) => {
    res.json({ status: "OK", message: "Hevy Workout API is running" });
  });

  // Start server
  app.listen(PORT, () => {
    console.log(`🚀 Hevy Workout API server running on port ${PORT}`);
    console.log(`📊 Health check: http://localhost:${PORT}/health`);
    console.log(`🔗 API endpoints: http://localhost:${PORT}/api`);
  });
}

// Graceful shutdown
process.on("SIGINT", () => {
  console.log("\n🛑 Shutting down gracefully...");
  db.close((err) => {
    if (err) {
      console.error("Error closing database:", err.message);
    } else {
      console.log("Database connection closed.");
    }
    process.exit(0);
  });
});
