import { MessageSquare, Settings, Folder } from "lucide-react";

export function Sidebar() {
  return (
    <aside className="border-r border-zinc-800 bg-zinc-900/50">
      <div className="p-4">
        <h1 className="text-xl font-bold">Recursive</h1>
      </div>

      <nav className="space-y-2 p-3">
        <button className="flex w-full items-center gap-3 rounded-lg p-3 hover:bg-zinc-800">
          <MessageSquare size={18} />
          Chats
        </button>

        <button className="flex w-full items-center gap-3 rounded-lg p-3 hover:bg-zinc-800">
          <Folder size={18} />
          Files
        </button>

        <button className="flex w-full items-center gap-3 rounded-lg p-3 hover:bg-zinc-800">
          <Settings size={18} />
          Settings
        </button>
      </nav>
    </aside>
  );
}