#!/usr/bin/env node

const axios = require("axios");

const BASE_URL = "http://localhost:3000/api";

async function testAPI() {
  console.log("🚀 Testing Hevy Workout API...\n");

  try {
    // Test 1: Health check
    console.log("1. Testing health endpoint...");
    const health = await axios.get("http://localhost:3000/health");
    console.log("✅ Health check passed:", health.data.message);

    // Test 2: Get workouts
    console.log("\n2. Testing workouts endpoint...");
    const workouts = await axios.get(`${BASE_URL}/workouts?limit=3`);
    console.log(`✅ Found ${workouts.data.workouts.length} workouts`);
    console.log(`   First workout: ${workouts.data.workouts[0].title}`);

    // Test 3: Get specific workout
    if (workouts.data.workouts.length > 0) {
      console.log("\n3. Testing specific workout endpoint...");
      const workoutId = workouts.data.workouts[0].id;
      const workout = await axios.get(`${BASE_URL}/workouts/${workoutId}`);
      console.log(`✅ Workout details: ${workout.data.workout.title}`);
      console.log(`   Exercise count: ${workout.data.exercise_count}`);
    }

    // Test 4: Get exercises
    console.log("\n4. Testing exercises endpoint...");
    const exercises = await axios.get(
      `${BASE_URL}/exercises?limit=5&exercise_title=bench`
    );
    console.log(`✅ Found ${exercises.data.exercises.length} bench exercises`);

    // Test 5: Get statistics
    console.log("\n5. Testing statistics endpoint...");
    const stats = await axios.get(`${BASE_URL}/stats?period=month`);
    console.log(
      `✅ Monthly stats: ${stats.data.total_workouts} workouts, ${stats.data.total_exercises} exercises`
    );

    // Test 6: Search functionality
    console.log("\n6. Testing search endpoint...");
    const search = await axios.get(`${BASE_URL}/search?q=full&type=workouts`);
    console.log(
      `✅ Search results: ${search.data.workouts.length} workouts found for "full"`
    );

    // Test 7: Export functionality
    console.log("\n7. Testing export endpoint...");
    const exportData = await axios.get(`${BASE_URL}/export?format=json`);
    console.log(
      `✅ Export successful: ${exportData.data.total_workouts} workouts exported`
    );

    console.log("\n🎉 All API tests passed successfully!");
    console.log("\n📚 API Documentation:");
    console.log("   - Health: http://localhost:3000/health");
    console.log("   - API Base: http://localhost:3000/api");
    console.log("   - Workouts: http://localhost:3000/api/workouts");
    console.log("   - Exercises: http://localhost:3000/api/exercises");
    console.log("   - Stats: http://localhost:3000/api/stats");
    console.log("   - Search: http://localhost:3000/api/search");
    console.log("   - Export: http://localhost:3000/api/export");
  } catch (error) {
    console.error("❌ API test failed:", error.message);
    if (error.response) {
      console.error("   Status:", error.response.status);
      console.error("   Data:", error.response.data);
    }
    process.exit(1);
  }
}

// Check if server is running
async function checkServer() {
  try {
    await axios.get("http://localhost:3000/health");
    return true;
  } catch (error) {
    return false;
  }
}

async function main() {
  const serverRunning = await checkServer();

  if (!serverRunning) {
    console.log("⚠️  Server is not running. Please start the server first:");
    console.log("   npm start");
    console.log("\n   Then run this test script again.");
    process.exit(1);
  }

  await testAPI();
}

main();
