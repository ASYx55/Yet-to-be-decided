export function ModelSelector() {
  return (
    <select className="rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm">
      <option>GPT-OSS</option>
      <option>Qwen</option>
      <option>Gemma</option>
      <option>DeepSeek</option>
    </select>
  );
}