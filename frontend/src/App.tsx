import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import PriorAuthList from "./components/PriorAuthList";
import PriorAuthDetails from "./components/PriorAuthDetails";
import { PriorAuthProvider } from "./context/PriorAuthContext";

export function App() {
  return (
    <PriorAuthProvider>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <h1 className="text-2xl font-semibold text-gray-900">
              Prior Authorization Portal
            </h1>
          </div>
        </header>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<PriorAuthList />} />
              <Route path="/details/:id" element={<PriorAuthDetails />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </BrowserRouter>
        </main>
      </div>
    </PriorAuthProvider>
  );
}

export default App;
