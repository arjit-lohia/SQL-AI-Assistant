import { useEffect, useRef, useState, type ReactNode } from "react";
import {
  ArrowDownToLine,
  ArrowUp,
  ArrowUpRight,
  BarChart3,
  Check,
  ChevronDown,
  ChevronRight,
  Code2,
  Copy,
  Database,
  FileCode2,
  History,
  KeyRound,
  Layers,
  LoaderCircle,
  Menu,
  MessageSquare,
  Plus,
  Search,
  ShieldCheck,
  Sparkles,
  Square,
  Sun,
  Moon,
  Table2,
  Trash2,
  Users,
  X,
  Workflow,
  AlertCircle,
  Play,
} from "lucide-react";
import type {
  Conversation,
  Cost,
  Dialect,
  Health,
  Message,
  Response,
  Schema,
} from "./types";
import {
  apiError,
  context,
  download,
  loadConversations,
  persist,
  streamChat,
  toCSV,
} from "./lib";

const uid = () => crypto.randomUUID();
const dialectNames = {
  sqlite: "SQLite",
  postgres: "PostgreSQL",
  mysql: "MySQL",
};
const examples = [
  {
    icon: Users,
    title: "Explore your customers",
    text: "Show customers in California",
    tag: "FILTER",
  },
  {
    icon: BarChart3,
    title: "Understand revenue",
    text: "Monthly revenue for 2025",
    tag: "AGGREGATE",
  },
  {
    icon: History,
    title: "Find your newest hires",
    text: "Show all employees hired after January 2024",
    tag: "DATE RANGE",
  },
  {
    icon: Layers,
    title: "Discover top products",
    text: "Top 5 products by revenue",
    tag: "JOIN + RANK",
  },
];

function Dialog({
  title,
  children,
  onClose,
}: {
  title: string;
  children: ReactNode;
  onClose: () => void;
}) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const previous = document.activeElement as HTMLElement;
    ref.current?.focus();
    const key = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
      if (e.key === "Tab") {
        const all = Array.from(
          ref.current?.querySelectorAll<HTMLElement>(
            'button,input,select,a,[tabindex="0"]',
          ) || [],
        );
        const first = all[0],
          last = all[all.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last?.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first?.focus();
        }
      }
    };
    document.addEventListener("keydown", key);
    return () => {
      document.removeEventListener("keydown", key);
      previous?.focus();
    };
  }, [onClose]);
  return (
    <div
      className="modal-backdrop"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        className="dialog"
        ref={ref}
        role="dialog"
        aria-modal="true"
        aria-label={title}
        tabIndex={-1}
      >
        <div className="dialog-head">
          <h2>{title}</h2>
          <button
            className="icon-button"
            aria-label="Close dialog"
            onClick={onClose}
          >
            <X size={20} />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

function SQLCode({ sql }: { sql: string }) {
  const tokens = sql.split(
    /(--[^\n]*|'(?:''|[^'])*'|"[^"]*"|`[^`]*`|\b\d+(?:\.\d+)?\b|\b[A-Za-z_]+\b)/g,
  );
  const keywords =
    /^(SELECT|FROM|WHERE|AND|OR|AS|JOIN|LEFT|RIGHT|INNER|ON|GROUP|BY|ORDER|HAVING|LIMIT|OFFSET|ASC|DESC|DISTINCT|WITH|CASE|WHEN|THEN|ELSE|END|IS|NOT|NULL|IN|BETWEEN|UNION|ALL)$/i;
  return (
    <div className="code-scroll">
      <div className="line-numbers" aria-hidden="true">
        {sql.split("\n").map((_, i) => (
          <div key={i}>{i + 1}</div>
        ))}
      </div>
      <pre aria-label="Validated SQL">
        <code>
          {tokens.map((t, i) => (
            <span
              key={i}
              className={
                t.startsWith("'")
                  ? "sql-string"
                  : /^\d/.test(t)
                    ? "sql-number"
                    : keywords.test(t)
                      ? "sql-keyword"
                      : t.startsWith("--")
                        ? "sql-comment"
                        : ""
              }
            >
              {t}
            </span>
          ))}
        </code>
      </pre>
    </div>
  );
}

function Plan({ cost }: { cost: Cost }) {
  return (
    <div className="plan">
      <div className="plan-summary">
        <Workflow size={22} />
        <div>
          <span className={"cost-tag " + cost.level}>
            {cost.level} relative work
          </span>
          <p>{cost.summary}</p>
        </div>
      </div>
      {cost.plan.map((p) => (
        <div className="plan-row" key={p.id}>
          <span>{String(p.id).padStart(2, "0")}</span>
          <code>{p.detail}</code>
        </div>
      ))}
      <p className="muted fine-print">{cost.caveat}</p>
    </div>
  );
}

export default function App() {
  const [conversations, setConversations] =
    useState<Conversation[]>(loadConversations);
  const [active, setActive] = useState(() => conversations[0]?.id || uid());
  const [selected, setSelected] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const dialect: Dialect = "sqlite";
  const [mode, setMode] = useState<"generate" | "optimize" | "debug">(
    "generate",
  );
  const [autoRun, setAutoRun] = useState(true);
  const [schema, setSchema] = useState<Schema | null>(null);
  const [health, setHealth] = useState<Health | null>(null);
  const [connectionError, setConnectionError] = useState("");
  const [busy, setBusy] = useState(false),
    [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(""),
    [streamText, setStreamText] = useState("");
  const [error, setError] = useState(""),
    [notice, setNotice] = useState("");
  const [tab, setTab] = useState("results");
  const [modal, setModal] = useState<"schema" | null>(null);
  const [sidebar, setSidebar] = useState(false);
  const [mobilePane, setMobilePane] = useState<"chat" | "query">("chat");
  const [copied, setCopied] = useState(false);
  const [dark, setDark] = useState(() => {
    try {
      return (
        (localStorage.getItem("queryatlas.theme") ||
          (matchMedia("(prefers-color-scheme: dark)").matches
            ? "dark"
            : "light")) === "dark"
      );
    } catch {
      return false;
    }
  });
  const abort = useRef<AbortController | null>(null),
    bottom = useRef<HTMLDivElement>(null);
  const current = conversations.find((c) => c.id === active);
  const messages = current?.messages || [];
  const selectedMessage =
    messages.find((m) => m.id === selected) ||
    [...messages].reverse().find((m) => m.response);
  const response = selectedMessage?.response;
  const result = response?.result;
  const waiting = busy || running;

  useEffect(() => {
    const key = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k" && !waiting) {
        e.preventDefault();
        setActive(uid());
        setSelected(null);
        setInput("");
        setError("");
        setSidebar(false);
      }
    };
    document.addEventListener("keydown", key);
    return () => document.removeEventListener("keydown", key);
  }, [waiting]);

  useEffect(() => {
    document.documentElement.dataset.theme = dark ? "dark" : "light";
    try {
      localStorage.setItem("queryatlas.theme", dark ? "dark" : "light");
    } catch {}
  }, [dark]);
  useEffect(() => {
    try {
      persist(conversations);
    } catch {
      setNotice(
        "Browser storage is unavailable. Your conversation will stay in memory for this session.",
      );
    }
  }, [conversations]);
  useEffect(() => {
    const scrollArea = bottom.current?.parentElement;
    scrollArea?.scrollTo({
      top: messages.length ? scrollArea.scrollHeight : 0,
      behavior: messages.length ? "smooth" : "instant",
    });
  }, [messages.length, progress]);
  async function connect() {
    setConnectionError("");
    try {
      const [s, h] = await Promise.all([
        fetch("/api/schema"),
        fetch("/api/health"),
      ]);
      if (!s.ok || !h.ok)
        throw new Error(
          "The sample database is unavailable. Start the backend or rebuild the sample data.",
        );
      setSchema(await s.json());
      setHealth(await h.json());
    } catch (e) {
      setConnectionError(
        e instanceof Error ? e.message : "Could not connect to the backend.",
      );
    }
  }
  useEffect(() => {
    void connect();
    return () => abort.current?.abort();
  }, []);
  function changeConversation(id: string) {
    setActive(id);
    setSelected(null);
    setError("");
    setSidebar(false);
    setMobilePane("chat");
    setStreamText("");
    setMobilePane("chat");
  }
  function fresh() {
    changeConversation(uid());
    setInput("");
  }
  function updateResponse(id: string, r: Response) {
    setConversations((cs) =>
      cs.map((c) =>
        c.id === active
          ? {
              ...c,
              messages: c.messages.map((m) =>
                m.id === id
                  ? { ...m, response: r, content: r.explanation || r.message }
                  : m,
              ),
            }
          : c,
      ),
    );
  }
  async function send(question = input) {
    if (waiting || !question.trim()) return;
    setError("");
    setStreamText("");
    setProgress("Starting the workflow");
    setBusy(true);
    setInput("");
    const id = active,
      previous = messages,
      user: Message = { id: uid(), role: "user", content: question, dialect };
    setConversations((cs) => {
      const existing = cs.find((c) => c.id === id);
      const next = {
        id,
        title: existing?.title || question.slice(0, 48),
        updated: Date.now(),
        messages: [...(existing?.messages || []), user],
      };
      return [next, ...cs.filter((c) => c.id !== id)].slice(0, 12);
    });
    abort.current = new AbortController();
    try {
      await streamChat(
        {
          message: question,
          dialect,
          mode,
          execute: autoRun,
          history: context(previous),
        },
        abort.current.signal,
        (event, data) => {
          if (event === "progress") setProgress(String(data.label));
          if (event === "text") setStreamText((t) => t + String(data.delta));
          if (event === "result") {
            const r = data as unknown as Response,
              assistant: Message = {
                id: uid(),
                role: "assistant",
                content: r.explanation || r.message,
                dialect: r.dialect,
                response: r,
              };
            setConversations((cs) =>
              cs.map((c) =>
                c.id === id
                  ? { ...c, messages: [...c.messages, assistant] }
                  : c,
              ),
            );
            setSelected(assistant.id);
            setTab(r.status === "success" ? "results" : "explanation");
            setMobilePane(r.status === "success" ? "query" : "chat");
          }
        },
      );
    } catch (e) {
      setError(
        e instanceof Error && e.name === "AbortError"
          ? "Request cancelled. Your input is ready to retry."
          : e instanceof Error
            ? e.message
            : "The request failed. Please retry.",
      );
      setInput(question);
    } finally {
      setBusy(false);
      setProgress("");
      setStreamText("");
      abort.current = null;
    }
  }
  async function run() {
    if (!response?.sql || !selectedMessage || waiting) return;
    setRunning(true);
    setError("");
    try {
      const res = await fetch("/api/execute", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ sql: response.sql, dialect: response.dialect }),
      });
      if (!res.ok) throw new Error(await apiError(res));
      const data = await res.json();
      updateResponse(selectedMessage.id, {
        ...response,
        result: data.result,
        cost: data.cost,
      });
      setTab("results");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Execution failed.");
    } finally {
      setRunning(false);
    }
  }
  async function copy() {
    try {
      await navigator.clipboard.writeText(response?.sql || "");
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setError(
        "Clipboard access is unavailable. Select the SQL text and copy it manually.",
      );
    }
  }
  function remove(id: string) {
    setConversations((cs) => cs.filter((c) => c.id !== id));
    if (active === id) fresh();
  }

  return (
    <div className="app-shell">
      {sidebar && (
        <button
          className="sidebar-scrim"
          aria-label="Close navigation"
          onClick={() => setSidebar(false)}
        />
      )}
      <aside className={"sidebar " + (sidebar ? "is-open" : "")}>
        <a className="brand" href="/" aria-label="QueryAtlas home">
          <span className="brand-symbol">
            <Code2 size={23} />
          </span>
          QueryAtlas<span className="brand-dot">.</span>
        </a>
        <div className="workspace-label">YOUR WORKSPACE</div>
        <button className="new-chat" onClick={fresh} disabled={waiting}>
          <Plus size={17} />
          New conversation<span>⌘ K</span>
        </button>
        <div className="history-heading">
          <span>RECENT CONVERSATIONS</span>
          <button
            className="icon-button"
            aria-label="Clear all conversation history"
            title="Clear all conversation history"
            disabled={waiting || !conversations.length}
            onClick={() => {
              if (confirm("Clear all conversations stored in this browser?")) {
                setConversations([]);
                fresh();
              }
            }}
          >
            <Trash2 size={13} />
          </button>
        </div>
        <nav className="history" aria-label="Conversation history">
          {conversations.length ? (
            conversations.map((c) => (
              <div
                className={"history-item " + (active === c.id ? "active" : "")}
                key={c.id}
              >
                <button
                  onClick={() => changeConversation(c.id)}
                  disabled={waiting}
                >
                  <MessageSquare size={14} />
                  <span>{c.title}</span>
                </button>
                <button
                  aria-label={"Delete " + c.title}
                  className="delete-chat"
                  disabled={waiting}
                  onClick={() => remove(c.id)}
                >
                  <Trash2 size={13} />
                </button>
              </div>
            ))
          ) : (
            <p className="history-empty">
              Your conversations will appear here. A good question is a great
              start.
            </p>
          )}
        </nav>
        <div className="sidebar-bottom">
          <div className="dataset-card">
            <span className="dataset-icon">
              <Database size={18} />
            </span>
            <div>
              <strong>Northstar Commerce</strong>
              <span>
                <i className={health ? "tiny-dot" : "tiny-dot offline"} />
                {health
                  ? "Sample database connected"
                  : "Waiting for connection"}
              </span>
            </div>
          </div>
          <div className="profile">
            <span className="avatar">N</span>
            <div>
              <strong>Northstar workspace</strong>
              <span>Local · Synthetic data</span>
            </div>
            <ShieldCheck size={17} />
          </div>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <div className="breadcrumbs">
            <button
              className="icon-button mobile-menu"
              aria-label="Open navigation"
              onClick={() => setSidebar(true)}
            >
              <Menu size={21} />
            </button>
            <span>Workspace</span>
            <ChevronRight size={14} />
            <strong>SQL assistant</strong>
          </div>
          <div className="top-actions">
            <span className="readonly-pill">
              <ShieldCheck size={13} />
              Read-only access
            </span>
            <button
              className="secondary-button schema-button"
              onClick={() => setModal("schema")}
            >
              <Database size={15} />
              View schema
            </button>
            <button
              className="theme-toggle"
              role="switch"
              aria-label="Dark mode"
              aria-checked={dark}
              title={dark ? "Use light theme" : "Use dark theme"}
              onClick={() => setDark(!dark)}
            >
              <span
                className={"theme-option " + (!dark ? "selected" : "")}
                aria-hidden="true"
              >
                <Sun size={16} />
              </span>
              <span className="theme-track" aria-hidden="true">
                <span className="theme-thumb" />
              </span>
              <span
                className={"theme-option " + (dark ? "selected" : "")}
                aria-hidden="true"
              >
                <Moon size={16} />
              </span>
            </button>
          </div>
        </header>
        <main className="workspace">
          {connectionError && (
            <div role="alert" className="error-banner">
              <AlertCircle size={17} />
              {connectionError}
              <button onClick={() => void connect()}>Retry connection</button>
            </div>
          )}
          {notice && (
            <div className="notice-banner" role="status">
              {notice}
            </div>
          )}
          <div
            className="mobile-view-switch"
            role="group"
            aria-label="Workspace view"
          >
            <button
              aria-pressed={mobilePane === "chat"}
              onClick={() => setMobilePane("chat")}
            >
              <MessageSquare size={14} />
              Chat
            </button>
            <button
              aria-pressed={mobilePane === "query"}
              onClick={() => setMobilePane("query")}
            >
              <FileCode2 size={14} />
              Query workspace
            </button>
          </div>
          <div className="workbench" data-active-pane={mobilePane}>
            <section className="chat-panel" aria-label="SQL conversation">
              <div className="panel-heading">
                <span>
                  <Sparkles size={16} />
                  SQL assistant
                </span>
                <span
                  className={
                    "provider-badge " +
                    (health?.provider === "groq" ? "live" : "")
                  }
                >
                  {health?.provider === "groq" ? "Live AI" : "Sample mode"}
                </span>
              </div>
              <div className="chat-scroll">
                {!messages.length ? (
                  <div className="welcome">
                    <div className="welcome-icon">
                      <Sparkles size={27} />
                    </div>
                    <h2>
                      What would you like
                      <br />
                      to find out?
                    </h2>
                    <p>
                      Explore customers, revenue, products, and your team. Start
                      with a question below.
                    </p>
                    <div className="example-grid">
                      {examples.map(({ icon: Icon, ...e }) => (
                        <button
                          key={e.title}
                          className="example-card"
                          disabled={waiting}
                          onClick={() => void send(e.text)}
                        >
                          <span className="example-top">
                            <Icon size={18} />
                            <ArrowUpRight size={15} />
                          </span>
                          <strong>{e.title}</strong>
                          <span>{e.text}</span>
                          <small>{e.tag}</small>
                        </button>
                      ))}
                    </div>
                    <div className="sample-note">
                      <ShieldCheck size={15} />
                      <span>
                        {health?.provider === "groq"
                          ? `Powered by ${health.model}. SQL is independently validated.`
                          : "Sample mode works without an API key. Configure Groq on the server for full natural-language support."}
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="messages">
                    {messages.map((m) => (
                      <article className={"message " + m.role} key={m.id}>
                        {m.role === "assistant" && (
                          <span className="assistant-avatar">
                            <Sparkles size={16} />
                          </span>
                        )}
                        <div className="message-body">
                          <span className="message-author">
                            {m.role === "user" ? "You" : "QueryAtlas"}
                            {m.response && (
                              <span
                                className={"status-label " + m.response.status}
                              >
                                {m.response.status === "success"
                                  ? "Validated"
                                  : m.response.status === "refused"
                                    ? "Out of scope"
                                    : m.response.status === "clarification"
                                      ? "Clarification"
                                      : "Needs attention"}
                              </span>
                            )}
                          </span>
                          <p>
                            {m.role === "assistant"
                              ? m.response?.status === "success"
                                ? m.response.explanation
                                : m.response?.message
                              : m.content}
                          </p>
                          {m.response?.sql && (
                            <button
                              className={
                                "query-link " +
                                (selectedMessage?.id === m.id ? "chosen" : "")
                              }
                              onClick={() => {
                                setSelected(m.id);
                                setTab("results");
                                setMobilePane("query");
                              }}
                            >
                              <FileCode2 size={15} />
                              View query & results
                              <ArrowUpRight size={13} />
                            </button>
                          )}
                          {m.response?.diagnostics.map((d, i) => (
                            <p className="diagnostic" key={i}>
                              {d}
                            </p>
                          ))}
                        </div>
                      </article>
                    ))}
                  </div>
                )}
                {busy && (
                  <div className="streaming-message" role="status">
                    <LoaderCircle size={16} className="spin" />
                    <span>{progress}</span>
                    {streamText && <p>{streamText}</p>}
                  </div>
                )}
                <div ref={bottom} />
              </div>
              <div className="composer-area">
                {error && (
                  <div className="error-banner compact" role="alert">
                    <AlertCircle size={16} />
                    <span>{error}</span>
                    <button
                      className="icon-button"
                      aria-label="Dismiss error"
                      onClick={() => setError("")}
                    >
                      <X size={14} />
                    </button>
                  </div>
                )}
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    void send();
                  }}
                >
                  <div className="composer">
                    <label className="sr-only" htmlFor="question">
                      Your SQL or database question
                    </label>
                    <textarea
                      id="question"
                      placeholder={
                        mode === "generate"
                          ? "Ask anything about your data…"
                          : mode === "debug"
                            ? "Paste a SQL query to diagnose and correct…"
                            : "Paste a SQL query to format and optimize…"
                      }
                      value={input}
                      maxLength={4000}
                      disabled={busy}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={(e) => {
                        if (
                          e.key === "Enter" &&
                          !e.shiftKey &&
                          !e.nativeEvent.isComposing
                        ) {
                          e.preventDefault();
                          void send();
                        }
                      }}
                    />
                    <div className="composer-toolbar">
                      <div className="mode-select">
                        <Code2 size={14} />
                        <label className="sr-only" htmlFor="mode">
                          Task mode
                        </label>
                        <select
                          id="mode"
                          value={mode}
                          disabled={waiting}
                          onChange={(e) =>
                            setMode(e.target.value as typeof mode)
                          }
                        >
                          <option value="generate">Generate SQL</option>
                          <option value="optimize">Optimize SQL</option>
                          <option value="debug">Debug SQL</option>
                        </select>
                      </div>
                      {busy ? (
                        <button
                          type="button"
                          className="send-button"
                          aria-label="Cancel request"
                          onClick={() => abort.current?.abort()}
                        >
                          <Square size={15} />
                        </button>
                      ) : (
                        <button
                          type="submit"
                          className="send-button"
                          aria-label="Send question"
                          disabled={!input.trim() || waiting}
                        >
                          <ArrowUp size={19} />
                        </button>
                      )}
                    </div>
                  </div>
                </form>
                <div className="composer-foot">
                  <label className="auto-run">
                    <input
                      type="checkbox"
                      checked={autoRun}
                      onChange={(e) => setAutoRun(e.target.checked)}
                    />
                    Auto-run queries
                  </label>
                  <span>Enter to send · Shift + Enter for a new line</span>
                </div>
              </div>
            </section>
            <section className="query-panel" aria-label="Query workspace">
              <div className="panel-heading">
                <span>
                  <FileCode2 size={16} />
                  Query workspace
                </span>
                <span className="muted small">
                  {response?.sql
                    ? dialectNames[response.dialect]
                    : dialectNames[dialect]}
                </span>
              </div>
              <div className="sql-toolbar">
                <div>
                  <span className="file-dot" />
                  <strong>query.sql</strong>
                  {response?.validation.valid && (
                    <span className="validation-badge">
                      <Check size={12} />
                      Validated
                    </span>
                  )}
                </div>
                <div className="sql-actions">
                  <button
                    className="icon-button"
                    title="Copy SQL"
                    aria-label="Copy SQL"
                    disabled={!response?.sql || waiting}
                    onClick={() => void copy()}
                  >
                    {copied ? <Check size={15} /> : <Copy size={15} />}
                  </button>
                  <button
                    className="icon-button"
                    title="Download SQL"
                    aria-label="Download SQL"
                    disabled={!response?.sql || waiting}
                    onClick={() =>
                      download(
                        `-- ${dialectNames[response!.dialect]} output; sample execution engine: SQLite\n${response!.sql};\n`,
                        "query.sql",
                        "application/sql",
                      )
                    }
                  >
                    <ArrowDownToLine size={16} />
                  </button>
                </div>
              </div>
              {response?.sql ? (
                <SQLCode sql={response.sql} />
              ) : (
                <div className="sql-empty">
                  <div className="code-placeholder">
                    <span>01</span>
                    <code>-- Your next insight starts with a question.</code>
                  </div>
                  <div className="code-placeholder">
                    <span>02</span>
                    <code>-- Validated SQL will appear here.</code>
                  </div>
                  <div className="code-placeholder">
                    <span>03</span>
                    <span className="code-cursor" />
                  </div>
                </div>
              )}
              <div className="run-toolbar">
                <span className="engine-note">
                  <ShieldCheck size={13} />
                  Executes on SQLite sample data
                </span>
                <button
                  className="primary-button"
                  disabled={!response?.sql || waiting}
                  onClick={() => void run()}
                >
                  {running ? (
                    <LoaderCircle size={14} className="spin" />
                  ) : (
                    <Play size={13} />
                  )}
                  Run query
                </button>
              </div>
              <div
                className="result-tabs"
                role="tablist"
                aria-label="Query details"
              >
                {[
                  { id: "results", icon: Table2, label: "Results" },
                  {
                    id: "explanation",
                    icon: MessageSquare,
                    label: "Explanation",
                  },
                  { id: "plan", icon: Workflow, label: "Query plan" },
                ].map(({ id, icon: Icon, label }) => (
                  <button
                    role="tab"
                    id={"tab-" + id}
                    aria-controls={"panel-" + id}
                    aria-selected={tab === id}
                    tabIndex={tab === id ? 0 : -1}
                    onKeyDown={(e) => {
                      if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
                        e.preventDefault();
                        const ids = ["results", "explanation", "plan"];
                        const next =
                          ids[
                            (ids.indexOf(id) +
                              (e.key === "ArrowRight" ? 1 : 2)) %
                              3
                          ];
                        setTab(next);
                        document.getElementById("tab-" + next)?.focus();
                      }
                    }}
                    key={id}
                    className={tab === id ? "active" : ""}
                    onClick={() => setTab(id)}
                  >
                    <Icon size={15} />
                    {label}
                    {id === "results" && result && (
                      <span>{result.row_count}</span>
                    )}
                  </button>
                ))}
              </div>
              <div
                role="tabpanel"
                id={"panel-" + tab}
                aria-labelledby={"tab-" + tab}
                className={
                  "result-content " +
                  (result && tab === "results" ? "has-results" : "")
                }
              >
                {tab === "results" ? (
                  result ? (
                    <>
                      <div className="results-meta">
                        <span>
                          <span className="tiny-dot" />
                          {result.row_count}{" "}
                          {result.truncated
                            ? "rows shown (limited)"
                            : "rows returned"}
                          <span className="meta-separator">·</span>
                          {result.elapsed_ms.toFixed(1)} ms
                        </span>
                        <button
                          className="text-button"
                          onClick={() =>
                            download(
                              toCSV(result),
                              "query-results.csv",
                              "text/csv;charset=utf-8",
                            )
                          }
                        >
                          <ArrowDownToLine size={13} />
                          Export CSV
                        </button>
                      </div>
                      {result.truncated && (
                        <div className="truncation">
                          Results are capped at {result.max_rows} rows. CSV
                          exports only these displayed rows.
                        </div>
                      )}
                      <div className="table-scroll">
                        <table>
                          <thead>
                            <tr>
                              <th className="row-index">#</th>
                              {result.columns.map((c, i) => (
                                <th key={i}>{c}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {result.rows.map((r, i) => (
                              <tr key={i}>
                                <td className="row-index">{i + 1}</td>
                                {r.map((v, j) => (
                                  <td key={j}>
                                    {v === null ? (
                                      <span className="null-value">NULL</span>
                                    ) : typeof v === "number" &&
                                      !Number.isInteger(v) ? (
                                      v.toLocaleString("en-US", {
                                        maximumFractionDigits: 2,
                                      })
                                    ) : (
                                      String(v)
                                    )}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                        {!result.rows.length && (
                          <p className="zero-rows">
                            No records match this query. Try a different filter
                            or date range.
                          </p>
                        )}
                      </div>
                    </>
                  ) : (
                    <div className="results-empty">
                      <span className="empty-table-icon">
                        <Table2 size={29} />
                      </span>
                      <h3>
                        {response?.sql
                          ? "Ready when you are"
                          : "From question to insight"}
                      </h3>
                      <p>
                        {response?.sql
                          ? "Run your validated query to see the actual sample data."
                          : "Your query results will appear here. Ask a question to explore what’s in your data."}
                      </p>
                      <div className="empty-steps">
                        <span>
                          <MessageSquare size={13} />
                          Ask
                        </span>
                        <ChevronRight size={12} />
                        <span>
                          <Code2 size={13} />
                          Validate
                        </span>
                        <ChevronRight size={12} />
                        <span>
                          <Table2 size={13} />
                          Explore
                        </span>
                      </div>
                    </div>
                  )
                ) : tab === "explanation" ? (
                  response ? (
                    <div className="explanation">
                      <h3>
                        {response.status === "success"
                          ? "What this query does"
                          : response.status === "refused"
                            ? "SQL-only assistant"
                            : "Let’s clarify your question"}
                      </h3>
                      <p>{response.explanation || response.message}</p>
                      {response.assumptions.length > 0 && (
                        <>
                          <h4>Assumptions</h4>
                          <ul>
                            {response.assumptions.map((a, i) => (
                              <li key={i}>{a}</li>
                            ))}
                          </ul>
                        </>
                      )}
                      {response.diagnostics.length > 0 && (
                        <>
                          <h4>Diagnosis & changes</h4>
                          <ul>
                            {response.diagnostics.map((d, i) => (
                              <li key={i}>{d}</li>
                            ))}
                          </ul>
                        </>
                      )}
                      {response.suggestions.length > 0 && (
                        <>
                          <h4>Performance notes</h4>
                          <ul>
                            {response.suggestions.map((s, i) => (
                              <li key={i}>{s}</li>
                            ))}
                          </ul>
                        </>
                      )}
                      {response.validation.valid && (
                        <>
                          <h4>Independent validation</h4>
                          <div className="validation-checks">
                            {response.validation.checks.map((c) => (
                              <span key={c}>
                                <Check size={13} />
                                {c}
                              </span>
                            ))}
                          </div>
                        </>
                      )}
                    </div>
                  ) : (
                    <div className="results-empty">
                      <MessageSquare size={28} />
                      <h3>SQL, explained simply</h3>
                      <p>
                        Understand the filters, joins, and assumptions behind
                        every accepted query.
                      </p>
                    </div>
                  )
                ) : response?.cost ? (
                  <Plan cost={response.cost} />
                ) : (
                  <div className="results-empty">
                    <Workflow size={29} />
                    <h3>A look under the hood</h3>
                    <p>
                      After validation, inspect the real SQLite query plan and a
                      relative work estimate.
                    </p>
                  </div>
                )}
              </div>
              <div className="query-foot">
                <span>
                  <ShieldCheck size={13} />
                  Schema-grounded. Independently validated.
                </span>
                {response && (
                  <span>{response.elapsed_ms.toFixed(0)} ms workflow</span>
                )}
              </div>
            </section>
          </div>
          <footer className="workspace-footer">
            <span>
              <Database size={13} />
              {schema
                ? `${schema.tables.length} tables · ${schema.tables.reduce((n, t) => n + t.row_count, 0).toLocaleString()} synthetic records`
                : "Connecting to your sample data"}
            </span>
            <span>
              Built with LangGraph <span className="footer-dot">·</span> Always
              read-only
            </span>
          </footer>
        </main>
      </div>
      {modal === "schema" && (
        <Dialog title="Database explorer" onClose={() => setModal(null)}>
          <p className="dialog-intro">
            {schema?.name} · {schema?.description}. All SQL is grounded in these
            tables and declared relationships.
          </p>
          <div className="schema-list">
            {schema?.tables.map((t) => (
              <details key={t.name} open={t.name === "customers"}>
                <summary>
                  <Table2 size={16} />
                  <strong>{t.name}</strong>
                  <span>{t.row_count} rows</span>
                  <ChevronDown size={14} />
                </summary>
                <p>{t.description}</p>
                <div className="schema-columns">
                  {t.columns.map((c) => (
                    <div key={c.name}>
                      <span>
                        {c.primary_key ? (
                          <KeyRound size={12} />
                        ) : t.foreign_keys.some((f) => f.column === c.name) ? (
                          <Layers size={12} />
                        ) : (
                          <span className="column-dot" />
                        )}
                        <code>{c.name}</code>
                      </span>
                      <small>
                        {c.type}
                        {c.primary_key ? " · PRIMARY KEY" : ""}
                      </small>
                    </div>
                  ))}
                </div>
                {t.foreign_keys.map((f) => (
                  <p className="relationship" key={f.column}>
                    {t.name}.{f.column} → {f.references_table}.
                    {f.references_column}
                  </p>
                ))}
              </details>
            ))}
          </div>
        </Dialog>
      )}
    </div>
  );
}
