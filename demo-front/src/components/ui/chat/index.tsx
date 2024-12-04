export { UserMessage } from "./user-message";

export interface DefaultChatMessageType {
  message: string | null;
  tools: RefereceType[] | null;
  time?: string;
  userName?: string;
  avatarUrl?: string;
  model?: string;
  type?: "stop" | "loading" | "success" | "error";
  sender: "user" | "ai";
}

export interface RefereceType {
  title: string;
  content: string;
  page: string;
  relevance: number;
  uri: string;
}
