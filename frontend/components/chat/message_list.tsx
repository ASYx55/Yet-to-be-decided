import { Message } from "./message";

export function MessageList() {
  return (
    <div className="mx-auto max-w-4xl space-y-6 p-6">
      <Message
        role="assistant"
        content="Hello! I'm your local AI assistant."
      />

      <Message
        role="user"
        content="Can you explain Rust ownership?"
      />
    </div>
  );
}