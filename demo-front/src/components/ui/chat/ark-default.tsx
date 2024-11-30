import { Avatar } from "antd";
import "@/styles/chatmessage.scss";
import ArkSvg from "@/assets/ark-base.svg";

export interface ChatMessage {
  message: string;
  time: string;
  username?: string;
  avatarUrl?: string;
  sender?: "user" | "ai";
}

export const ArkDefault = ({ message, time, username }: ChatMessage) => {
  return (
    <div className="ai-message">
      <div className="chat-avatar">
        <Avatar
          shape="square"
          size={45}
          src={ArkSvg}
          style={{ backgroundColor: "#cce7ff" }}
        />
      </div>
      <div className="chat-content">
        <div className="chat-header">
          <span className="time">{time}</span>
          <span className="username">{username}</span>
        </div>
        <div className="message">{message}</div>
      </div>
    </div>
  );
};
