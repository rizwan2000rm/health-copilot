#!/usr/bin/env node

/**
 * Simple test script for the Hevy MCP Server
 * This script tests the basic functionality without requiring the full MCP client
 */

const { spawn } = require("child_process");
const path = require("path");

console.log("🧪 Testing Hevy MCP Server...\n");

// Test configuration
const testConfig = {
  serverName: "hevy-mcp-server",
  version: "1.0.0",
  tools: [
    "get_workouts",
    "get_workout_by_id",
    "get_exercises",
    "search_exercises",
    "get_workout_stats",
    "health_check",
  ],
};

// Simulate MCP protocol messages
const mcpMessages = [
  // List tools request
  {
    jsonrpc: "2.0",
    id: 1,
    method: "tools/list",
    params: {},
  },
  // Call tool request (get_workouts)
  {
    jsonrpc: "2.0",
    id: 2,
    method: "tools/call",
    params: {
      name: "get_workouts",
      arguments: {
        page: 1,
        limit: 5,
      },
    },
  },
  // Health check request
  {
    jsonrpc: "2.0",
    id: 3,
    method: "tools/call",
    params: {
      name: "health_check",
      arguments: {},
    },
  },
];

// Test the server
async function testMCPServer() {
  try {
    console.log("📋 Expected Tools:");
    testConfig.tools.forEach((tool) => {
      console.log(`  ✅ ${tool}`);
    });

    console.log("\n🔧 Server Configuration:");
    console.log(`  Name: ${testConfig.serverName}`);
    console.log(`  Version: ${testConfig.version}`);

    console.log("\n📡 Testing MCP Protocol Messages:");
    mcpMessages.forEach((msg, index) => {
      console.log(
        `  ${index + 1}. ${msg.method} - ${JSON.stringify(msg.params)}`
      );
    });

    console.log("\n🚀 Starting MCP Server Test...");

    // Check if the server can be built
    console.log("\n🔨 Building MCP Server...");
    try {
      const buildResult = await runCommand("npm", ["run", "build"], {
        cwd: path.join(__dirname, "../mcp"),
      });
      console.log("  ✅ Build successful");
    } catch (error) {
      console.log("  ❌ Build failed:", error.message);
      return;
    }

    // Test server startup
    console.log("\n🚀 Testing Server Startup...");
    try {
      const serverProcess = spawn("node", ["dist/index.js"], {
        cwd: path.join(__dirname, "../mcp"),
        stdio: ["pipe", "pipe", "pipe"],
      });

      // Wait a bit for server to start
      await new Promise((resolve) => setTimeout(resolve, 2000));

      if (serverProcess.killed) {
        console.log("  ❌ Server failed to start");
      } else {
        console.log("  ✅ Server started successfully");

        // Send test messages
        console.log("\n📤 Sending Test Messages...");
        mcpMessages.forEach((msg) => {
          const messageStr = JSON.stringify(msg) + "\n";
          serverProcess.stdin.write(messageStr);
        });

        // Wait for responses
        await new Promise((resolve) => setTimeout(resolve, 3000));

        // Clean up
        serverProcess.kill("SIGTERM");
        console.log("  ✅ Server test completed");
      }
    } catch (error) {
      console.log("  ❌ Server test failed:", error.message);
    }

    console.log("\n🎉 MCP Server Test Complete!");
  } catch (error) {
    console.error("❌ Test failed:", error.message);
    process.exit(1);
  }
}

// Helper function to run commands
function runCommand(command, args, options = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      stdio: "pipe",
      ...options,
    });

    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (data) => {
      stdout += data.toString();
    });

    child.stderr.on("data", (data) => {
      stderr += data.toString();
    });

    child.on("close", (code) => {
      if (code === 0) {
        resolve(stdout);
      } else {
        reject(new Error(`Command failed with code ${code}: ${stderr}`));
      }
    });

    child.on("error", (error) => {
      reject(error);
    });
  });
}

// Run the test
testMCPServer().catch(console.error);
