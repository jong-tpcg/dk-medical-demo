export { UserMessage } from "./user-message";

export interface DefaultChatMessageType {
  message: string | null;
  time?: string;
  userName?: string;
  avatarUrl?: string;
  model?: string;
  type?: "stop" | "loading" | "success" | "error";
  sender: "user" | "ai";
}
