import { Avatar } from "antd";
import "@/styles/chatmessage.scss";
import { UserOutlined } from "@ant-design/icons";

export interface ChatMessage {
  message: string;
  time: string;
  username?: string;
  avatarUrl?: string;
  sender?: "user" | "ai";
}

export const UserMessage = ({
  message,
  time,
  username,
  avatarUrl,
}: ChatMessage) => {
  return (
    <div className="user-message">
      <div className="chat-avatar">
        {avatarUrl && <Avatar shape="square" size={45} src={avatarUrl} />}
        <Avatar shape="square" size={45} icon={<UserOutlined />} />
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

export default UserMessage;
