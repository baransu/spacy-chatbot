import React, { useEffect, useRef, useState } from "react";
import io from "socket.io-client";

const socket = io("http://localhost:5000");

type Message = {
  side: "left" | "right";
  message: string;
};

export default function App() {
  const [value, setValue] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const messagesRef = useRef<null | HTMLDivElement>(null);

  useEffect(() => {
    socket.on("message", (message) => {
      setMessages((messages) => [
        ...messages,
        { message: message, side: "left" },
      ]);
    });
  }, []);

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    socket.emit("new_message", value);
    setValue("");
    setMessages((messages) => [...messages, { message: value, side: "right" }]);
  }

  function scrollToBottom() {
    if (messagesRef.current) {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    }
  }

  useEffect(() => {
    scrollToBottom();
  }, [messages.length]);

  return (
    <div className="p-4 w-96 border border-gray-400 rounded mx-auto">
      <div ref={messagesRef} className="h-96 overflow-y-auto">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.side == "right" ? "justify-end" : ""}`}
          >
            <div
              className={
                message.side == "right"
                  ? "p-1 mb-2 rounded bg-blue-500 text-white inline-block"
                  : "p-1 mb-2 rounded bg-gray-400 inline-block"
              }
            >
              {message.message}
            </div>
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="mt-2">
        <input
          placeholder="Say something..."
          className="bg-gray-100 p-2 rounded w-full"
          value={value}
          onChange={(event) => setValue(event.target.value)}
        />
      </form>
    </div>
  );
}
