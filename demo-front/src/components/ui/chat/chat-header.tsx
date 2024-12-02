import { useMemo } from "react";
import "@/styles/chats-all.scss";
import { formatTime } from "@/utils/format";
type ChatHeaderProps = {
  model?: string;
  time?: string;
  userName: string;
  align?: "left" | "right";
};

export const ChatHeader = ({
  model,
  time,
  userName,
  align = "left",
}: ChatHeaderProps) => {
  const defaultTime = useMemo(() => new Date().toLocaleTimeString(), []);

  return (
    <div
      className={`chat-header ${align === "right" ? "align-right" : "align-left"}`}
    >
      <div className="username">{userName}</div>
      <div className="time">
        {time ? formatTime(time) : formatTime(defaultTime)}
      </div>
      {model && <div className="model">{model}</div>}
    </div>
  );
};
