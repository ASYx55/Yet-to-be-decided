import { Sidebar } from "./sidebar";
import { Topbar } from "./topbar";
import { ChatWindow } from "../chat/chat_window";
import { PromptBox } from "../chat/prompt_box";

export default function AppShell() {
  return (
    <div className="h-screen bg-zinc-950 text-zinc-100">
      <div className="grid h-full grid-cols-[280px_1fr]">
        <Sidebar />

        <div className="flex flex-col">
          <Topbar />

          <div className="flex-1 overflow-hidden">
            <ChatWindow />
          </div>

          <PromptBox />
        </div>
      </div>
    </div>
  );
}