export type Dialect = "sqlite" | "postgres" | "mysql";
export type QueryResult = {
  columns: string[];
  rows: (string | number | null)[][];
  row_count: number;
  truncated: boolean;
  elapsed_ms: number;
  engine: string;
  max_rows: number;
};
export type Cost = {
  level: string;
  summary: string;
  caveat: string;
  scans: number;
  searches: number;
  temporary_sorts: number;
  plan: { id: number; parent: number; detail: string }[];
};
export type Response = {
  status: "success" | "refused" | "clarification" | "error";
  message: string;
  sql: string | null;
  dialect: Dialect;
  explanation: string;
  assumptions: string[];
  diagnostics: string[];
  suggestions: string[];
  validation: { valid: boolean; checks: string[] };
  cost: Cost | null;
  result: QueryResult | null;
  provider: string;
  steps: string[];
  elapsed_ms: number;
};
export type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  dialect: Dialect;
  response?: Response;
};
export type Conversation = {
  id: string;
  title: string;
  updated: number;
  messages: Message[];
};
export type Schema = {
  name: string;
  description: string;
  engine: string;
  examples: string[];
  tables: {
    name: string;
    description: string;
    row_count: number;
    columns: {
      name: string;
      type: string;
      nullable: boolean;
      primary_key: boolean;
    }[];
    foreign_keys: {
      column: string;
      references_table: string;
      references_column: string;
    }[];
    indexes: { name: string; columns: string[]; unique: boolean }[];
  }[];
};
export type Health = {
  status: string;
  database: string;
  provider: string;
  model: string | null;
  version: string;
};
