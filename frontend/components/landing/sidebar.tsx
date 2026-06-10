"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  MessageCircle,
  Network,
  TriangleAlert,
  History,
  BarChart3,
  BookOpen,
  Settings,
} from "lucide-react";

const items = [
  {
    icon: Home,
    label: "Home",
    href: "/",
  },
  {
    icon: MessageCircle,
    label: "Chat",
    href: "/chat",
  },
  {
    icon: Network,
    label: "Knowledge Graph",
    href: "/graph",
  },
  {
    icon: TriangleAlert,
    label: "Mistakes",
    href: "/mistakes",
  },
  {
    icon: History,
    label: "Revision",
    href: "/revision",
  },
  {
    icon: BarChart3,
    label: "Insights",
    href: "/insights",
  },
  {
    icon: BookOpen,
    label: "Subjects",
    href: "/subjects",
  },
  {
    icon: Settings,
    label: "Settings",
    href: "/settings",
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-full w-72 flex-col border-r border-white/5 bg-[#05070d]">
      <div className="p-6">
        <Link
          href="/"
          className="flex items-center gap-4"
        >
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-500 font-bold">
            R
          </div>

          <div>
            <h1 className="text-2xl font-bold">
              Recursive
            </h1>

            <p className="text-sm text-zinc-400">
              AI Study Copilot
            </p>
          </div>
        </Link>
      </div>

      <nav className="flex-1 px-4">
        <div className="space-y-2">
          {items.map((item) => {
            const active =
              item.href === "/"
                ? pathname === "/"
                : pathname.startsWith(
                    item.href
                  );

            return (
              <Link
                key={item.label}
                href={item.href}
                className={`
                  flex
                  h-12
                  w-full
                  items-center
                  gap-3
                  rounded-xl
                  px-4
                  transition-all
                  duration-200

                  ${
                    active
                      ? "bg-violet-600 text-white shadow-lg shadow-violet-900/40"
                      : "text-zinc-300 hover:bg-white/5 hover:text-white"
                  }
                `}
              >
                <item.icon size={18} />

                <span>
                  {item.label}
                </span>
              </Link>
            );
          })}
        </div>
      </nav>

      <div className="p-4">
        <div className="rounded-2xl border border-violet-500/10 bg-[#0b1020] p-4">
          <div className="mb-3 flex items-center gap-2">
            <span className="leading-none text-green-500">
              ●
            </span>

            <span className="text-sm">
              Memory System Active
            </span>
          </div>

          <div className="space-y-2 text-sm text-zinc-400">
            <p>Model: Qwen 4B</p>

            <p>Memory: 2.4 GB</p>
          </div>
        </div>
      </div>

      <div className="border-t border-white/5 p-4">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-full bg-violet-600">
            SS
          </div>

          <div>
            <p className="font-medium">
              Suyash Srivastava
            </p>

            <p className="text-sm text-zinc-400">
              CS Undergrad
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}