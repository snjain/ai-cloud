import { useState, useRef, useEffect } from "react";
import { useAuth } from "../hooks/useAuth";
import { Send, LogOut, Bot, User } from "lucide-react";
import ReactMarkdown from "react-markdown";

const AGENT_ENDPOINT = import.meta.env.VITE_AGENT_ENDPOINT || "http://localhost:8001/api/pydantic-agent";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function Chat() {
  const { user, signOut } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const res = await fetch(AGENT_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg }),
      });
      const data = await res.json();
      setMessages((prev) => [...prev, { role: "assistant", content: data.response }]);
    } catch (err: any) {
      setMessages((prev) => [...prev, { role: "assistant", content: `Error: ${err.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex h-screen flex-col bg-gray-950 text-white">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-gray-800 px-6 py-4">
        <div className="flex items-center gap-2">
          <Bot className="h-6 w-6 text-blue-500" />
          <h1 className="text-lg font-semibold">AI Cloud Agent</h1>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-400">{user?.email}</span>
          <button
            onClick={signOut}
            className="flex items-center gap-1 rounded-md bg-gray-800 px-3 py-1.5 text-sm hover:bg-gray-700"
          >
            <LogOut className="h-4 w-4" />
            Sign Out
          </button>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {messages.length === 0 && (
          <div className="flex h-full items-center justify-center text-gray-500">
            <div className="text-center">
              <Bot className="mx-auto mb-4 h-12 w-12 text-gray-700" />
              <p className="text-lg">How can I help you today?</p>
            </div>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`mb-4 flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-3xl rounded-xl px-4 py-3 ${
                msg.role === "user" ? "bg-blue-600" : "bg-gray-800"
              }`}
            >
              <div className="mb-1 flex items-center gap-1 text-xs font-medium opacity-70">
                {msg.role === "assistant" ? <Bot className="h-3 w-3" /> : <User className="h-3 w-3" />}
                {msg.role === "assistant" ? "Agent" : "You"}
              </div>
              <div className="prose prose-invert max-w-none">
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              </div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="rounded-xl bg-gray-800 px-4 py-3">
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <div className="h-2 w-2 animate-bounce rounded-full bg-gray-500" />
                <div className="h-2 w-2 animate-bounce rounded-full bg-gray-500 [animation-delay:0.2s]" />
                <div className="h-2 w-2 animate-bounce rounded-full bg-gray-500 [animation-delay:0.4s]" />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-800 px-6 py-4">
        <div className="flex items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            rows={1}
            className="max-h-32 flex-1 resize-none rounded-xl bg-gray-800 px-4 py-3 text-white outline-none ring-1 ring-gray-700 placeholder:text-gray-500 focus:ring-blue-500"
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="rounded-xl bg-blue-600 p-3 hover:bg-blue-700 disabled:opacity-50"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
