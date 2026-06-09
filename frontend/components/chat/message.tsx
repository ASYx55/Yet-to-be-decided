type Props = {
  role: "user" | "assistant";
  content: string;
};

export function Message({ role, content }: Props) {
  const isUser = role === "user";

  return (
    <div
      className={`rounded-2xl border p-5 ${
        isUser
          ? "border-blue-900 bg-blue-950/30"
          : "border-zinc-800 bg-zinc-900"
      }`}
    >
      <div className="mb-2 text-xs uppercase tracking-wide text-zinc-500">
        {role}
      </div>

      <p>{content}</p>
    </div>
  );
}