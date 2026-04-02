export default function ResultCard({ result, getExplanation }) {
  return (
    <div className="bg-gray-800 p-4 rounded shadow m-2">
      <h3 className="text-lg font-semibold">
        🚨 {result.attack_type}
      </h3>

      <p className="text-gray-300">
        Confidence: {(result.confidence * 100).toFixed(2)}%
      </p>

      <button
        onClick={() => getExplanation(result.attack_type)}
        className="bg-green-500 px-3 py-1 mt-2 rounded"
      >
        Explain
      </button>
    </div>
  );
}