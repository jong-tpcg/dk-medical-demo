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
  id: string;
  title: string;
  content: string;
  score: string;
  uri: string;
  url_page: string;
  pageIdentifier: string;
  relevanceScore: number;
}
export interface QnaStore {
  answer: string;
  question: string;
  documnt_title: string;
  documnt_content: string;
}
