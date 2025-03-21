const API_BASE_URL = "https://your-backend.onrender.com";

const fetchHistory = async () => {
  const response = await axios.get(`${API_BASE_URL}/history`);
  setHistory(response.data);
};

const handleSubmit = async (e) => {
  const response = await axios.post(`${API_BASE_URL}/breakdown`, { instruction });
  setSteps(response.data.steps);
};
import React, { useState, useEffect } from "react";
import { Button, Input, Card, CardContent } from "@/components/ui";
import axios from "axios";

export default function InstructionBreakdown() {
  const [instruction, setInstruction] = useState("");
  const [steps, setSteps] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await axios.get("http://localhost:5000/history");
      setHistory(response.data);
    } catch (error) {
      console.error("Error fetching history", error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post("http://localhost:5000/breakdown", {
        instruction,
      });
      setSteps(response.data.steps);
      fetchHistory();
    } catch (error) {
      console.error("Error fetching steps", error);
    }
    setLoading(false);
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Instruction Breakdown</h1>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Input
          type="text"
          value={instruction}
          onChange={(e) => setInstruction(e.target.value)}
          placeholder="Enter a complex instruction..."
          className="p-2 border rounded"
        />
        <Button type="submit" disabled={loading}>
          {loading ? "Processing..." : "Break Down"}
        </Button>
      </form>
      <div className="mt-4">
        {steps.length > 0 && (
          <Card>
            <CardContent>
              <h2 className="text-lg font-semibold">Steps:</h2>
              <ul className="list-decimal ml-4">
                {steps.map((step, index) => (
                  <li key={index} className="mt-2">{step}</li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}
      </div>
      <div className="mt-8">
        <h2 className="text-xl font-semibold">History</h2>
        {history.length > 0 ? (
          history.map((entry, index) => (
            <Card key={index} className="mt-4">
              <CardContent>
                <p className="font-semibold">{entry.instruction}</p>
                <ul className="list-disc ml-4 mt-2">
                  {entry.steps.map((step, i) => (
                    <li key={i}>{step}</li>
                  ))}
                </ul>
                <p className="text-sm text-gray-500 mt-2">{new Date(entry.created_at).toLocaleString()}</p>
              </CardContent>
            </Card>
          ))
        ) : (
          <p>No history available.</p>
        )}
      </div>
    </div>
  );
}
