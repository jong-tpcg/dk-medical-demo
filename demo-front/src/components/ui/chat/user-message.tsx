import "@/styles/chats-all.scss";
import { DefaultChatMessageType } from "@/components/ui/chat";
import { AvatarCustom } from "../avatar";
import { ChatHeader } from "./chat-header";

export const UserMessage = ({
  message,
  time,
  userName,
  avatarUrl,
  type,
}: DefaultChatMessageType) => {
  const defaultUsername = "테스트 유저";
  return (
    <div className="chat-message-container user">
      <AvatarCustom variant="chat-user" avatar={avatarUrl} />
      <div className="chat-content-wrapper user">
        <ChatHeader
          align="right"
          time={time}
          userName={userName ? userName : defaultUsername}
        />
        <div className={`message-box user ${type ? type : ""}`}>{message}</div>
      </div>
    </div>
  );
};

export default UserMessage;
