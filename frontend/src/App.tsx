import { useState, useEffect } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import { apiClient, API_BASE_URL } from "./config/api";

interface User {
  id: number;
  name: string;
  email: string;
}

interface ApiResponse {
  users: User[];
}

interface HealthResponse {
  status: string;
  timestamp: string;
}

function App() {
  const [count, setCount] = useState(0);
  const [users, setUsers] = useState<User[]>([]);
  const [healthStatus, setHealthStatus] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Function to test API connection
  const testApiConnection = async () => {
    setLoading(true);
    setError(null);

    try {
      // Test health endpoint
      const health = (await apiClient.getHealth()) as HealthResponse;
      setHealthStatus(health);

      // Get users
      const response = (await apiClient.getUsers()) as ApiResponse;
      setUsers(response.users);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to connect to API");
      console.error("API Error:", err);
    } finally {
      setLoading(false);
    }
  };

  // Test API on component mount
  useEffect(() => {
    testApiConnection();
  }, []);

  return (
    <div className="max-w-5xl mx-auto p-8 text-center">
      <div className="flex justify-center items-center gap-8 mb-8">
        <a href="https://vite.dev" target="_blank" className="block">
          <img
            src={viteLogo}
            className="h-24 p-6 transition-all duration-300 hover:drop-shadow-[0_0_2em_#646cffaa] hover:animate-spin"
            alt="Vite logo"
          />
        </a>
        <a href="https://react.dev" target="_blank" className="block">
          <img
            src={reactLogo}
            className="h-24 p-6 transition-all duration-300 hover:drop-shadow-[0_0_2em_#61dafbaa] animate-spin"
            alt="React logo"
            style={{ animation: "spin 20s linear infinite" }}
          />
        </a>
      </div>

      <h1 className="text-5xl font-bold leading-tight mb-8">Vite + React</h1>

      {/* API Configuration Info */}
      <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg mb-6">
        <h3 className="text-lg font-semibold mb-2">API Configuration</h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Backend URL:{" "}
          <code className="bg-gray-200 dark:bg-gray-700 px-1 rounded">
            {API_BASE_URL}
          </code>
        </p>
      </div>

      {/* API Status */}
      <div className="bg-gray-50 dark:bg-gray-800/50 p-6 rounded-lg mb-6">
        <h3 className="text-xl font-semibold mb-4">Backend API Status</h3>

        {loading && (
          <div className="text-blue-600 dark:text-blue-400">Loading...</div>
        )}

        {error && (
          <div className="text-red-600 dark:text-red-400 mb-4">
            <strong>Error:</strong> {error}
          </div>
        )}

        {healthStatus && (
          <div className="text-green-600 dark:text-green-400 mb-4">
            <strong>✓ Backend is healthy!</strong>
            <div className="text-sm mt-1">
              Last checked: {new Date(healthStatus.timestamp).toLocaleString()}
            </div>
          </div>
        )}

        <button
          onClick={testApiConnection}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {loading ? "Testing..." : "Test API Connection"}
        </button>
      </div>

      {/* Users List */}
      {users.length > 0 && (
        <div className="bg-gray-50 dark:bg-gray-800/50 p-6 rounded-lg mb-6">
          <h3 className="text-xl font-semibold mb-4">Users from Backend</h3>
          <div className="grid gap-4 md:grid-cols-3">
            {users.map((user) => (
              <div
                key={user.id}
                className="bg-white dark:bg-gray-700 p-4 rounded-lg shadow"
              >
                <h4 className="font-semibold">{user.name}</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {user.email}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Original Counter */}
      <div className="p-8 bg-gray-100 dark:bg-gray-800 rounded-lg mb-8">
        <button
          onClick={() => setCount((count) => count + 1)}
          className="px-6 py-3 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 rounded-lg border border-transparent font-medium transition-colors duration-250 hover:border-blue-500 focus:outline-none focus:ring-4 focus:ring-blue-500/50"
        >
          count is {count}
        </button>
        <p className="mt-4 text-gray-600 dark:text-gray-400">
          Edit{" "}
          <code className="bg-gray-200 dark:bg-gray-700 px-1 rounded">
            src/App.tsx
          </code>{" "}
          and save to test HMR
        </p>
      </div>

      <p className="text-gray-500 dark:text-gray-400">
        Click on the Vite and React logos to learn more
      </p>
    </div>
  );
}

export default App;
