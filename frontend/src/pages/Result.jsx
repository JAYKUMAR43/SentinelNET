import { useLocation } from "react-router-dom";
import ResultCard from "../components/ResultCard";

export default function Result() {
  const location = useLocation();
  const results = location.state?.results || [];

  return (
    <div className="p-6">
      <h2 className="text-2xl mb-4">Prediction Results</h2>

      <div className="grid grid-cols-2 gap-4">
        {results.map((res, i) => (
          <ResultCard key={i} result={res} />
        ))}
      </div>
    </div>
  );
}