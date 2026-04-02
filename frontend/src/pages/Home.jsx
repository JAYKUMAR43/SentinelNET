import { useNavigate } from "react-router-dom";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center justify-center h-screen text-center">
      <h1 className="text-4xl font-bold mb-4">
        SentinelNet AI 🔐
      </h1>

      <p className="mb-6 text-gray-400">
        AI Powered Network Intrusion Detection System
      </p>

      <button
        onClick={() => navigate("/upload")}
        className="bg-blue-600 px-6 py-2 rounded"
      >
        Get Started
      </button>
    </div>
  );
}