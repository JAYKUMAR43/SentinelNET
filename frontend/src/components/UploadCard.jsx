export default function UploadCard({ setFile, handleUpload, loading }) {
  return (
    <div className="bg-gray-800 p-6 rounded shadow text-center">
      <h2 className="text-xl mb-4">Upload Network Data</h2>

      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
        className="mb-4"
      />

      <br />

      <button
        onClick={handleUpload}
        className="bg-blue-500 px-4 py-2 rounded"
      >
        Upload & Predict
      </button>

      {loading && <p className="mt-3">Processing...</p>}
    </div>
  );
}