import { useState } from "react";

function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);

  const sendMessage = async () => {
    if (!message.trim()) return;

    // הוספת הודעת משתמש
    setMessages(prev => [...prev, { from: "user", text: message }]);

    const res = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ message })
    });

    const data = await res.json();

    // הוספת תשובת Agent
    setMessages(prev => [
      ...prev,
      { from: "bot", text: data.reply }
    ]);

    setMessage("");
  };

  return (
    <div style={{ maxWidth: 600, margin: "40px auto", fontFamily: "Arial" }}>
      <h2>📝 Todo Chat</h2>

      <div
        style={{
          border: "1px solid #ccc",
          padding: 10,
          minHeight: 300,
          marginBottom: 10
        }}
      >
        {messages.map((m, i) => (
          <div
            key={i}
            style={{
              textAlign: m.from === "user" ? "right" : "left",
              margin: "8px 0"
            }}
          >
            <b>{m.from === "user" ? "את" : "🤖"}:</b> {m.text}
          </div>
        ))}
      </div>

      <input
        style={{ width: "80%", padding: 8 }}
        value={message}
        onChange={e => setMessage(e.target.value)}
        placeholder="כתוב הודעה..."
        onKeyDown={e => e.key === "Enter" && sendMessage()}
      />

      <button onClick={sendMessage} style={{ padding: 8, marginLeft: 5 }}>
        שלח
      </button>
    </div>
  );
}

export default App;