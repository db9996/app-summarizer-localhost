import React, { useEffect, useState } from "react";
import axios from "axios";

function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");

    async function fetchProtectedData() {
      try {
        const response = await axios.get("https://app-backend1.onrender.com/api/protected", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setData(response.data);
      } catch (error) {
        setError("Error fetching protected data");
        console.error(error);
      }
    }

    fetchProtectedData();
  }, []);

  return (
    <div>
      <h2>Dashboard</h2>
      {data && <div>{JSON.stringify(data)}</div>}
      {error && <div style={{ color: "red" }}>{error}</div>}
    </div>
  );
}

export default Dashboard;
