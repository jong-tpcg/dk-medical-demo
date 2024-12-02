import { message } from "antd";
import "@/styles/chats-all.scss";
import { useCallback, useEffect, useState } from "react";

import UserInput from "@/components/ui/chat/user-input";
import { ScrollButtons } from "@/components/ui/chat/scroll-buttons";
import { useChatStore } from "@/store/chatStore";
import { DefaultChatMessageType, UserMessage } from "@/components/ui/chat";
import { useOutletContext } from "react-router-dom";
import { useMemo } from "react";
import { ArkMessageBox } from "@/components/ui/chat/ark-message-box";
import { ArkDefault } from "@/components/ui/chat/ark-default";
import { agentConfig } from "./agentConfig";

type OutletContextType = {
  selectedAgent: string;
};

export const AgentsChatCommon = () => {
  const agentChatList = useChatStore((state) => state.agentChatList);
  const addChatMessage = useChatStore((state) => state.addChatMessage);
  const resetChatList = useChatStore((state) => state.resetChatList);

  const [inputValue, setInputValue] = useState<string>("");
  const [messageApi, contextHolder] = message.useMessage();
  const { selectedAgent } = useOutletContext<OutletContextType>();
  const { initialMessage } = agentConfig[selectedAgent];

  const chatMessages = useMemo(() => {
    if (selectedAgent && selectedAgent in agentChatList) {
      return agentChatList[selectedAgent];
    }
    return [];
  }, [agentChatList, selectedAgent]);

  useEffect(() => {
    console.log(chatMessages);
  }, [chatMessages]);

  const handleSendMessage = async () => {
    if (inputValue.trim() !== "") {
      const userMessage: DefaultChatMessageType = {
        message: inputValue,
        time: new Date().toLocaleTimeString(),
        sender: "user",
        model: "default",
      };
      const newAnswerMessage: DefaultChatMessageType = {
        message: null,
        time: new Date().toLocaleTimeString(),
        sender: "ai",
        type: "loading",
      };
      console.log("메시지 전송", inputValue);
      addChatMessage(selectedAgent, userMessage);
      addChatMessage(selectedAgent, newAnswerMessage);
      setInputValue("");
    } else {
      messageApi.warning("메시지를 입력해주세요.");
      return;
    }

    setTimeout(() => {
      updateLastAiMessage({
        message: "AI 응답입니다.",
        type: "success",
      });
    }, 5000);
  };

  const updateLastAiMessage = useCallback(
    (newData: Partial<DefaultChatMessageType>) => {
      if (!selectedAgent) return;
      console.log("updateLastAiMessage", newData);
      const state = useChatStore.getState();
      const currentMessages = state.agentChatList[selectedAgent!] || [];
      console.log("currentMessages", currentMessages);
      console.log(chatMessages);
      if (currentMessages.length === 0) return;

      const lastMessageIndex = currentMessages.length - 1;
      const lastMessage = currentMessages[lastMessageIndex];
      console.log(currentMessages);
      if (lastMessage.sender !== "ai") return;

      const updatedMessage = {
        ...lastMessage,
        time: new Date().toLocaleTimeString(),
        ...newData,
      };

      const updatedMessages = [
        ...currentMessages.slice(0, lastMessageIndex),
        updatedMessage,
      ];
      useChatStore.setState((state) => ({
        agentChatList: {
          ...state.agentChatList,
          [selectedAgent!]: updatedMessages,
        },
      }));
    },
    [selectedAgent, chatMessages]
  );

  return (
    <div className="chat-wrapper">
      {contextHolder}
      <div className="chat-list-wrapper">
        <ArkDefault avatarUrl="ark_medical">
          <ArkMessageBox message={initialMessage} auto={true} />
        </ArkDefault>
        {chatMessages.map((chat, index) =>
          chat.sender === "user" ? (
            <UserMessage
              key={index}
              message={chat.message}
              time={chat.time}
              sender="user"
              avatarUrl={chat.avatarUrl || ""}
            />
          ) : (
            <ArkDefault
              avatarUrl="ark_medical"
              key={index}
              time={chat.time}
              status={chat.type}
            >
              {chat.message && <ArkMessageBox markdownMessage={chat.message} />}
            </ArkDefault>
          )
        )}
      </div>
      <ScrollButtons />
      <UserInput
        inputValue={inputValue}
        onInputChange={setInputValue}
        onSendMessage={handleSendMessage}
        onResetChat={() => {
          resetChatList(selectedAgent);
        }}
      />
    </div>
  );
};
