import "@/styles/chats-all.scss";
import { AvatarCustom } from "@/components/ui/avatar";
import { ChatHeader } from "./chat-header";
import { Spinner } from "../spinner/Spinner";
import { useEffect } from "react";
export const ArkDefault = ({
  children,
  time,
  model,
  userName = "D-Chat",
  avatarUrl = "ark",
  status,
}: {
  children: React.ReactNode;
  time?: string;
  model?: string;
  userName?: string;
  avatarUrl?: string;
  status?: string;
}) => {
  useEffect(() => {
    console.log(status);
  }, [status]);
  return (
    <div className="chat-message-container ark">
      <AvatarCustom variant="chat-ark" avatar={avatarUrl} />
      <div className="chat-content-wrapper ark">
        <ChatHeader model={model} time={time} userName={userName} />
        {status == "loading" ? <Spinner /> : children}
      </div>
    </div>
  );
};
