// API documentation:
// https://api.hevyapp.com/docs/

// Implement all the endpoints from the api documentation
// Instead of using the api directly, use the sqlite

const express = require("express");
const sqlite3 = require("sqlite3").verbose();
const router = express.Router();

// Database connection
const db = new sqlite3.Database("./hevy/api/workouts.db");

// Helper function for database queries
function query(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => {
      if (err) {
        reject(err);
      } else {
        resolve(rows);
      }
    });
  });
}

function queryOne(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.get(sql, params, (err, row) => {
      if (err) {
        reject(err);
      } else {
        resolve(row);
      }
    });
  });
}

function run(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function (err) {
      if (err) {
        reject(err);
      } else {
        resolve({ id: this.lastID, changes: this.changes });
      }
    });
  });
}

// 1. GET /api/workouts - Get all workouts
router.get("/workouts", async (req, res) => {
  try {
    const { page = 1, limit = 20, search, start_date, end_date } = req.query;
    const offset = (page - 1) * limit;

    let sql = `
      SELECT 
        w.id,
        w.title,
        w.start_time,
        w.end_time,
        w.description,
        w.created_at,
        COUNT(e.id) as exercise_count,
        SUM(CASE WHEN e.duration_seconds IS NOT NULL THEN e.duration_seconds ELSE 0 END) as total_duration
      FROM workouts w
      LEFT JOIN exercises e ON w.id = e.workout_id
    `;

    const whereConditions = [];
    const params = [];

    if (search) {
      whereConditions.push("(w.title LIKE ? OR w.description LIKE ?)");
      params.push(`%${search}%`, `%${search}%`);
    }

    if (start_date) {
      whereConditions.push("w.start_time >= ?");
      params.push(start_date);
    }

    if (end_date) {
      whereConditions.push("w.start_time <= ?");
      params.push(end_date);
    }

    if (whereConditions.length > 0) {
      sql += " WHERE " + whereConditions.join(" AND ");
    }

    sql +=
      " GROUP BY w.id ORDER BY datetime(w.start_time) DESC LIMIT ? OFFSET ?";
    params.push(parseInt(limit), offset);

    const workouts = await query(sql, params);

    // Get total count for pagination
    let countSql = "SELECT COUNT(DISTINCT w.id) as total FROM workouts w";
    if (whereConditions.length > 0) {
      countSql += " WHERE " + whereConditions.join(" AND ");
    }
    const countResult = await queryOne(countSql, params.slice(0, -2));

    res.json({
      workouts,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total: countResult.total,
        pages: Math.ceil(countResult.total / limit),
      },
    });
  } catch (error) {
    console.error("Error fetching workouts:", error);
    res.status(500).json({ error: "Failed to fetch workouts" });
  }
});

// 2. GET /api/workouts/:id - Get specific workout with exercises
router.get("/workouts/:id", async (req, res) => {
  try {
    const { id } = req.params;

    // Get workout details
    const workout = await queryOne(
      `
      SELECT * FROM workouts WHERE id = ?
    `,
      [id]
    );

    if (!workout) {
      return res.status(404).json({ error: "Workout not found" });
    }

    // Get exercises for this workout
    const exercises = await query(
      `
      SELECT * FROM exercises 
      WHERE workout_id = ? 
      ORDER BY set_index, exercise_title
    `,
      [id]
    );

    res.json({
      workout,
      exercises,
      exercise_count: exercises.length,
    });
  } catch (error) {
    console.error("Error fetching workout:", error);
    res.status(500).json({ error: "Failed to fetch workout" });
  }
});

// 3. POST /api/workouts - Create new workout
router.post("/workouts", async (req, res) => {
  try {
    const { title, start_time, end_time, description, exercises } = req.body;

    if (!title || !start_time || !end_time) {
      return res
        .status(400)
        .json({ error: "Title, start_time, and end_time are required" });
    }

    // Insert workout
    const workoutResult = await run(
      `
      INSERT INTO workouts (title, start_time, end_time, description)
      VALUES (?, ?, ?, ?)
    `,
      [title, start_time, end_time, description || ""]
    );

    const workoutId = workoutResult.id;

    // Insert exercises if provided
    if (exercises && Array.isArray(exercises)) {
      for (const exercise of exercises) {
        await run(
          `
          INSERT INTO exercises (workout_id, exercise_title, superset_id, exercise_notes, set_index, set_type, weight_kg, reps, distance_km, duration_seconds, rpe)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `,
          [
            workoutId,
            exercise.exercise_title,
            exercise.superset_id || null,
            exercise.exercise_notes || null,
            exercise.set_index || 0,
            exercise.set_type || "normal",
            exercise.weight_kg || null,
            exercise.reps || null,
            exercise.distance_km || null,
            exercise.duration_seconds || null,
            exercise.rpe || null,
          ]
        );
      }
    }

    res.status(201).json({
      message: "Workout created successfully",
      workout_id: workoutId,
    });
  } catch (error) {
    console.error("Error creating workout:", error);
    res.status(500).json({ error: "Failed to create workout" });
  }
});

// 4. PUT /api/workouts/:id - Update workout
router.put("/workouts/:id", async (req, res) => {
  try {
    const { id } = req.params;
    const { title, start_time, end_time, description } = req.body;

    // Check if workout exists
    const existingWorkout = await queryOne(
      "SELECT id FROM workouts WHERE id = ?",
      [id]
    );
    if (!existingWorkout) {
      return res.status(404).json({ error: "Workout not found" });
    }

    // Update workout
    await run(
      `
      UPDATE workouts 
      SET title = ?, start_time = ?, end_time = ?, description = ?
      WHERE id = ?
    `,
      [title, start_time, end_time, description || "", id]
    );

    res.json({ message: "Workout updated successfully" });
  } catch (error) {
    console.error("Error updating workout:", error);
    res.status(500).json({ error: "Failed to update workout" });
  }
});

// 5. DELETE /api/workouts/:id - Delete workout
router.delete("/workouts/:id", async (req, res) => {
  try {
    const { id } = req.params;

    // Check if workout exists
    const existingWorkout = await queryOne(
      "SELECT id FROM workouts WHERE id = ?",
      [id]
    );
    if (!existingWorkout) {
      return res.status(404).json({ error: "Workout not found" });
    }

    // Delete exercises first (due to foreign key constraint)
    await run("DELETE FROM exercises WHERE workout_id = ?", [id]);

    // Delete workout
    await run("DELETE FROM workouts WHERE id = ?", [id]);

    res.json({ message: "Workout deleted successfully" });
  } catch (error) {
    console.error("Error deleting workout:", error);
    res.status(500).json({ error: "Failed to delete workout" });
  }
});

// 6. GET /api/exercises - Get all exercises with filtering
router.get("/exercises", async (req, res) => {
  try {
    const {
      page = 1,
      limit = 50,
      exercise_title,
      set_type,
      min_weight,
      max_weight,
      min_reps,
      max_reps,
      workout_id,
    } = req.query;

    const offset = (page - 1) * limit;

    let sql = `
      SELECT 
        e.*,
        w.title as workout_title,
        w.start_time as workout_date
      FROM exercises e
      JOIN workouts w ON e.workout_id = w.id
    `;

    const whereConditions = [];
    const params = [];

    if (exercise_title) {
      whereConditions.push("e.exercise_title LIKE ?");
      params.push(`%${exercise_title}%`);
    }

    if (set_type) {
      whereConditions.push("e.set_type = ?");
      params.push(set_type);
    }

    if (min_weight) {
      whereConditions.push("e.weight_kg >= ?");
      params.push(parseFloat(min_weight));
    }

    if (max_weight) {
      whereConditions.push("e.weight_kg <= ?");
      params.push(parseFloat(max_weight));
    }

    if (min_reps) {
      whereConditions.push("e.reps >= ?");
      params.push(parseInt(min_reps));
    }

    if (max_reps) {
      whereConditions.push("e.reps <= ?");
      params.push(parseInt(max_reps));
    }

    if (workout_id) {
      whereConditions.push("e.workout_id = ?");
      params.push(parseInt(workout_id));
    }

    if (whereConditions.length > 0) {
      sql += " WHERE " + whereConditions.join(" AND ");
    }

    sql +=
      " ORDER BY datetime(w.start_time) DESC, e.set_index LIMIT ? OFFSET ?";
    params.push(parseInt(limit), offset);

    const exercises = await query(sql, params);

    res.json({
      exercises,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total: exercises.length,
      },
    });
  } catch (error) {
    console.error("Error fetching exercises:", error);
    res.status(500).json({ error: "Failed to fetch exercises" });
  }
});

// 7. GET /api/exercises/:id - Get specific exercise
router.get("/exercises/:id", async (req, res) => {
  try {
    const { id } = req.params;

    const exercise = await queryOne(
      `
      SELECT 
        e.*,
        w.title as workout_title,
        w.start_time as workout_date
      FROM exercises e
      JOIN workouts w ON e.workout_id = w.id
      WHERE e.id = ?
    `,
      [id]
    );

    if (!exercise) {
      return res.status(404).json({ error: "Exercise not found" });
    }

    res.json(exercise);
  } catch (error) {
    console.error("Error fetching exercise:", error);
    res.status(500).json({ error: "Failed to fetch exercise" });
  }
});

// 8. POST /api/exercises - Add exercise to workout
router.post("/exercises", async (req, res) => {
  try {
    const {
      workout_id,
      exercise_title,
      superset_id,
      exercise_notes,
      set_index,
      set_type,
      weight_kg,
      reps,
      distance_km,
      duration_seconds,
      rpe,
    } = req.body;

    if (!workout_id || !exercise_title) {
      return res
        .status(400)
        .json({ error: "workout_id and exercise_title are required" });
    }

    // Check if workout exists
    const workout = await queryOne("SELECT id FROM workouts WHERE id = ?", [
      workout_id,
    ]);
    if (!workout) {
      return res.status(404).json({ error: "Workout not found" });
    }

    const result = await run(
      `
      INSERT INTO exercises (workout_id, exercise_title, superset_id, exercise_notes, set_index, set_type, weight_kg, reps, distance_km, duration_seconds, rpe)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `,
      [
        workout_id,
        exercise_title,
        superset_id || null,
        exercise_notes || null,
        set_index || 0,
        set_type || "normal",
        weight_kg || null,
        reps || null,
        distance_km || null,
        duration_seconds || null,
        rpe || null,
      ]
    );

    res.status(201).json({
      message: "Exercise added successfully",
      exercise_id: result.id,
    });
  } catch (error) {
    console.error("Error adding exercise:", error);
    res.status(500).json({ error: "Failed to add exercise" });
  }
});

// 9. PUT /api/exercises/:id - Update exercise
router.put("/exercises/:id", async (req, res) => {
  try {
    const { id } = req.params;
    const updateData = req.body;

    // Check if exercise exists
    const existingExercise = await queryOne(
      "SELECT id FROM exercises WHERE id = ?",
      [id]
    );
    if (!existingExercise) {
      return res.status(404).json({ error: "Exercise not found" });
    }

    // Build dynamic update query
    const fields = [];
    const values = [];

    Object.keys(updateData).forEach((key) => {
      if (key !== "id" && key !== "workout_id") {
        fields.push(`${key} = ?`);
        values.push(updateData[key]);
      }
    });

    if (fields.length === 0) {
      return res.status(400).json({ error: "No valid fields to update" });
    }

    values.push(id);

    await run(
      `
      UPDATE exercises 
      SET ${fields.join(", ")}
      WHERE id = ?
    `,
      values
    );

    res.json({ message: "Exercise updated successfully" });
  } catch (error) {
    console.error("Error updating exercise:", error);
    res.status(500).json({ error: "Failed to update exercise" });
  }
});

// 10. DELETE /api/exercises/:id - Delete exercise
router.delete("/exercises/:id", async (req, res) => {
  try {
    const { id } = req.params;

    // Check if exercise exists
    const existingExercise = await queryOne(
      "SELECT id FROM exercises WHERE id = ?",
      [id]
    );
    if (!existingExercise) {
      return res.status(404).json({ error: "Exercise not found" });
    }

    await run("DELETE FROM exercises WHERE id = ?", [id]);

    res.json({ message: "Exercise deleted successfully" });
  } catch (error) {
    console.error("Error deleting exercise:", error);
    res.status(500).json({ error: "Failed to delete exercise" });
  }
});

// 11. GET /api/stats - Get workout statistics
router.get("/stats", async (req, res) => {
  try {
    const { period = "all" } = req.query;

    let dateFilter = "";
    let params = [];

    if (period === "week") {
      dateFilter = 'WHERE w.start_time >= date("now", "-7 days")';
    } else if (period === "month") {
      dateFilter = 'WHERE w.start_time >= date("now", "-30 days")';
    } else if (period === "year") {
      dateFilter = 'WHERE w.start_time >= date("now", "-365 days")';
    }

    // Total workouts
    const totalWorkouts = await queryOne(
      `
      SELECT COUNT(*) as count FROM workouts w ${dateFilter}
    `,
      params
    );

    // Total exercises
    const totalExercises = await queryOne(
      `
      SELECT COUNT(*) as count FROM exercises e
      JOIN workouts w ON e.workout_id = w.id
      ${dateFilter}
    `,
      params
    );

    // Most common exercises
    const topExercises = await query(
      `
      SELECT 
        e.exercise_title,
        COUNT(*) as count,
        AVG(e.weight_kg) as avg_weight,
        AVG(e.reps) as avg_reps
      FROM exercises e
      JOIN workouts w ON e.workout_id = w.id
      ${dateFilter}
      GROUP BY e.exercise_title
      ORDER BY count DESC
      LIMIT 10
    `,
      params
    );

    // Workout frequency by day of week
    const workoutFrequency = await query(
      `
      SELECT 
        strftime('%w', w.start_time) as day_of_week,
        COUNT(*) as count
      FROM workouts w
      ${dateFilter}
      GROUP BY strftime('%w', w.start_time)
      ORDER BY day_of_week
    `,
      params
    );

    // Average workout duration
    const avgDuration = await queryOne(
      `
      SELECT 
        AVG(
          CASE 
            WHEN e.duration_seconds IS NOT NULL THEN e.duration_seconds
            ELSE 0
          END
        ) as avg_duration
      FROM exercises e
      JOIN workouts w ON e.workout_id = w.id
      ${dateFilter}
    `,
      params
    );

    res.json({
      period,
      total_workouts: totalWorkouts.count,
      total_exercises: totalExercises.count,
      top_exercises: topExercises,
      workout_frequency: workoutFrequency,
      average_duration_seconds: avgDuration.avg_duration || 0,
    });
  } catch (error) {
    console.error("Error fetching stats:", error);
    res.status(500).json({ error: "Failed to fetch statistics" });
  }
});

// 12. GET /api/search - Search workouts and exercises
router.get("/search", async (req, res) => {
  try {
    const { q, type = "all" } = req.query;

    if (!q) {
      return res.status(400).json({ error: "Search query is required" });
    }

    let results = {};

    if (type === "all" || type === "workouts") {
      const workouts = await query(
        `
        SELECT * FROM workouts 
        WHERE title LIKE ? OR description LIKE ?
        ORDER BY datetime(start_time) DESC
        LIMIT 20
      `,
        [`%${q}%`, `%${q}%`]
      );

      results.workouts = workouts;
    }

    if (type === "all" || type === "exercises") {
      const exercises = await query(
        `
        SELECT 
          e.*,
          w.title as workout_title,
          w.start_time as workout_date
        FROM exercises e
        JOIN workouts w ON e.workout_id = w.id
        WHERE e.exercise_title LIKE ? OR e.exercise_notes LIKE ?
        ORDER BY datetime(w.start_time) DESC
        LIMIT 20
      `,
        [`%${q}%`, `%${q}%`]
      );

      results.exercises = exercises;
    }

    res.json(results);
  } catch (error) {
    console.error("Error searching:", error);
    res.status(500).json({ error: "Failed to perform search" });
  }
});

// 13. GET /api/export - Export data
router.get("/export", async (req, res) => {
  try {
    const { format = "json" } = req.query;

    if (format === "csv") {
      // Export as CSV
      const workouts = await query(`
        SELECT 
          w.title,
          w.start_time,
          w.end_time,
          w.description,
          e.exercise_title,
          e.superset_id,
          e.exercise_notes,
          e.set_index,
          e.set_type,
          e.weight_kg,
          e.reps,
          e.distance_km,
          e.duration_seconds,
          e.rpe
        FROM workouts w
        LEFT JOIN exercises e ON w.id = e.workout_id
        ORDER BY datetime(w.start_time) DESC, e.set_index
      `);

      // Convert to CSV format
      const csvHeader =
        "title,start_time,end_time,description,exercise_title,superset_id,exercise_notes,set_index,set_type,weight_kg,reps,distance_km,duration_seconds,rpe\n";
      const csvData = workouts
        .map((row) =>
          Object.values(row)
            .map((val) => (val === null ? "" : `"${val}"`))
            .join(",")
        )
        .join("\n");

      res.setHeader("Content-Type", "text/csv");
      res.setHeader(
        "Content-Disposition",
        'attachment; filename="workouts_export.csv"'
      );
      res.send(csvHeader + csvData);
    } else {
      // Export as JSON
      const workouts = await query(`
        SELECT 
          w.*,
          json_group_array(
            json_object(
              'id', e.id,
              'exercise_title', e.exercise_title,
              'superset_id', e.superset_id,
              'exercise_notes', e.exercise_notes,
              'set_index', e.set_index,
              'set_type', e.set_type,
              'weight_kg', e.weight_kg,
              'reps', e.reps,
              'distance_km', e.distance_km,
              'duration_seconds', e.duration_seconds,
              'rpe', e.rpe
            )
          ) as exercises
        FROM workouts w
        LEFT JOIN exercises e ON w.id = e.workout_id
        GROUP BY w.id
        ORDER BY datetime(w.start_time) DESC
      `);

      res.json({
        export_date: new Date().toISOString(),
        total_workouts: workouts.length,
        workouts,
      });
    }
  } catch (error) {
    console.error("Error exporting data:", error);
    res.status(500).json({ error: "Failed to export data" });
  }
});

module.exports = router;
