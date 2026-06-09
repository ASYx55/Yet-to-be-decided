import { MessageList } from "./message_list";

export function ChatWindow() {
  return (
    <main className="h-full overflow-y-auto">
      <MessageList />
    </main>
  );
}