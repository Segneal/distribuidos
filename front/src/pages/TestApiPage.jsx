import React, { useEffect, useState } from "react";
import api from "../api";

export default function TestApiPage() {
  const [msg, setMsg] = useState("");

  useEffect(() => {
    api.get("/usuarios")
      .then(res => setMsg("✅ Conectado: " + JSON.stringify(res.data)))
      .catch(err => setMsg("❌ Error: " + (err.response?.status || err.message)));
  }, []);

  return (
    <div className="container">
      <h2>Prueba API</h2>
      <p>{msg}</p>
    </div>
  );
}
