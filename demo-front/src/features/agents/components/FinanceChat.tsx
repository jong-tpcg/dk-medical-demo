import { Button, Input } from "antd";
import "../../../styles/financechat.scss";
import { SendOutlined } from "@ant-design/icons";
import { useState } from "react";
import {
  UserMessage,
  ChatMessage,
  ArkDefault,
} from "../../../components/ui/chat";

const { TextArea } = Input;
export const FinanceChat = () => {
  const [inputValue, setInputValue] = useState<string>("");
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      message:
        "안녕하세요.  금융상품 상담 에이전트입니다. 카드, 보험, 예적금 등 궁금하신 내용에 대해 답변을 준비가 되어 있습니다.",
      time: new Date().toLocaleTimeString(),
      username: "Ark",
      sender: "ai",
    },
  ]);
  const handleInputChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(event.target.value);
  };

  const handleSendMessage = () => {
    console.log("채팅 메세지", inputValue);
    if (inputValue.trim() !== "") {
      const newMessage: ChatMessage = {
        message: inputValue,
        time: new Date().toLocaleTimeString(),
        username: "테스트 유저",
        sender: "user",
      };

      setChatMessages((prevMessages) => [...prevMessages, newMessage]);
      setInputValue("");
    }
  };

  return (
    <div className="chat-wrapper">
      <div className="chat-content">
        {chatMessages.map((chat, index) =>
          chat.sender === "user" ? (
            <UserMessage
              key={index}
              message={chat.message}
              time={chat.time}
              username={chat.username}
              avatarUrl={chat.avatarUrl || ""}
            />
          ) : (
            <ArkDefault
              key={index}
              message={chat.message}
              time={chat.time}
              username={chat.username}
            ></ArkDefault>
          )
        )}
      </div>
      <div className="search-input-wrapper">
        <TextArea
          value={inputValue}
          onChange={handleInputChange}
          autoSize={{ minRows: 1, maxRows: 5 }}
          placeholder="키워드를 입력하면 뉴스 수집 및 분석을 시작합니다."
          className="chat-input"
        />
        <Button
          type="primary"
          shape="circle"
          icon={<SendOutlined />}
          onClick={handleSendMessage}
          className="send-button"
        />
      </div>
    </div>
  );
};
