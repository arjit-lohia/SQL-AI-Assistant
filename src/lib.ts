import type { Conversation, Message, QueryResult } from "./types";

export function toCSV(result: QueryResult): string {
  const field = (v: string | number | null) => {
    let value = v === null ? "" : String(v);
    if (
      typeof v === "string" &&
      (/^[=+\-@\t\r\n]/.test(value) || /^[\s\x00-\x1f]+[=+\-@]/.test(value))
    )
      value = "'" + value;
    return '"' + value.replaceAll('"', '""') + '"';
  };
  return (
    "\uFEFF" +
    [result.columns, ...result.rows]
      .map((row) => row.map(field).join(","))
      .join("\r\n")
  );
}

export function download(content: string, name: string, mime: string) {
  const url = URL.createObjectURL(new Blob([content], { type: mime }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function loadConversations(): Conversation[] {
  try {
    const saved = localStorage.getItem("queryatlas.v1");
    if (!saved || saved.length > 2_500_000) return [];
    const value: unknown = JSON.parse(saved);
    if (!Array.isArray(value)) return [];
    return value
      .filter(
        (c): c is Conversation =>
          c &&
          typeof c.id === "string" &&
          typeof c.title === "string" &&
          typeof c.updated === "number" &&
          Array.isArray(c.messages) &&
          c.messages.every(
            (m: Message) =>
              m &&
              typeof m.id === "string" &&
              ["user", "assistant"].includes(m.role) &&
              typeof m.content === "string" &&
              ["sqlite", "mysql", "postgres"].includes(m.dialect) &&
              (!m.response ||
                (Array.isArray(m.response.diagnostics) &&
                  Array.isArray(m.response.assumptions) &&
                  Array.isArray(m.response.suggestions) &&
                  typeof m.response.validation?.valid === "boolean")),
          ),
      )
      .slice(0, 12);
  } catch {
    return [];
  }
}

export function persist(conversations: Conversation[]) {
  let bounded = conversations
    .slice(0, 12)
    .map((c) => ({ ...c, messages: c.messages.slice(-32) }));
  let text = JSON.stringify(bounded);
  if (text.length > 2_000_000) {
    bounded = bounded.map((c) => ({
      ...c,
      messages: c.messages.map((m) =>
        m.response ? { ...m, response: { ...m.response, result: null } } : m,
      ),
    }));
    text = JSON.stringify(bounded);
  }
  localStorage.setItem("queryatlas.v1", text);
}

export function context(messages: Message[]) {
  const turns = messages.slice(-16).map((m) => ({
    role: m.role,
    content: m.content.slice(0, 4000),
    sql: m.response?.sql || null,
    dialect: m.dialect,
  }));
  while (
    turns.reduce((n, t) => n + t.content.length + (t.sql?.length || 0), 0) >
    24000
  )
    turns.shift();
  return turns;
}

export async function apiError(response: globalThis.Response) {
  try {
    const json = await response.json();
    return typeof json.detail === "string"
      ? json.detail
      : "Please check your request and try again.";
  } catch {
    return `Request failed (${response.status}). Please retry.`;
  }
}

export async function streamChat(
  body: unknown,
  signal: AbortSignal,
  event: (name: string, data: Record<string, unknown>) => void,
) {
  const response = await fetch("/api/chat/stream", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
    signal,
  });
  if (!response.ok) throw new Error(await apiError(response));
  if (!response.body)
    throw new Error("Streaming is unavailable. Please retry.");
  const reader = response.body.getReader(),
    decoder = new TextDecoder();
  let buffer = "",
    terminal = false;
  while (true) {
    const { value, done } = await reader.read();
    buffer += decoder.decode(value, { stream: !done }).replaceAll("\r\n", "\n");
    let boundary: number;
    while ((boundary = buffer.indexOf("\n\n")) >= 0) {
      const frame = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);
      const name = frame
        .split("\n")
        .find((l) => l.startsWith("event:"))
        ?.slice(6)
        .trim();
      const data = frame
        .split("\n")
        .filter((l) => l.startsWith("data:"))
        .map((l) => l.slice(5).trim())
        .join("\n");
      if (name && data) {
        const parsed = JSON.parse(data);
        if (name === "error")
          throw new Error(
            parsed.message || "The query could not be completed.",
          );
        if (name === "result") terminal = true;
        event(name, parsed);
      }
    }
    if (done) break;
  }
  if (!terminal)
    throw new Error(
      "The connection ended before the response completed. Please retry.",
    );
}
