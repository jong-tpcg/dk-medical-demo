import { Button, Divider, message, Typography, Tag } from "antd";
import "@/styles/chats-all.scss";
import { useCallback, useState } from "react";
import { ScrollModal } from "@/components/ui/chat/ScrollModal";
import UserInput from "@/components/ui/chat/user-input";
import { ScrollButtons } from "@/components/ui/chat/scroll-buttons";
import { useChatStore } from "@/store/chatStore";
import { DefaultChatMessageType, UserMessage } from "@/components/ui/chat";
import { useMemo } from "react";
import { ArkMessageBox } from "@/components/ui/chat/ark-message-box";
import { ArkDefault } from "@/components/ui/chat/ark-default";
import { agentConfig } from "./agentConfig";
import axios from "axios";

export const AgentsChatCommon = () => {
  const agentChatList = useChatStore((state) => state.agentChatList);
  const addChatMessage = useChatStore((state) => state.addChatMessage);
  const resetChatList = useChatStore((state) => state.resetChatList);
  const setQnaList = useChatStore((state) => state.setQnaList);
  const selectedAgent = useChatStore((state) => state.selectedAgent);
  const setRelatedQuestionsList = useChatStore(
    (state) => state.setRelatedQuestionsList
  );
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [inputValue, setInputValue] = useState<string>("");
  const [messageApi, contextHolder] = message.useMessage();
  const { initialMessage } = agentConfig[selectedAgent!];
  const { Link } = Typography;
  const chatMessages = useMemo(() => {
    if (selectedAgent && selectedAgent in agentChatList) {
      return agentChatList[selectedAgent];
    }
    return [];
  }, [agentChatList, selectedAgent]);

  const handleSendMessage = async () => {
    if (inputValue.trim() !== "") {
      const userMessage: DefaultChatMessageType = {
        message: inputValue,
        tools: null,
        time: new Date().toLocaleTimeString(),
        sender: "user",
        model: "default",
      };
      const newAnswerMessage: DefaultChatMessageType = {
        message: null,
        tools: null,
        time: new Date().toLocaleTimeString(),
        sender: "ai",
        type: "loading",
      };
      sendMessage(inputValue);
      addChatMessage(selectedAgent!, userMessage);
      addChatMessage(selectedAgent!, newAnswerMessage);
      setQnaList("loading");
      setInputValue("");
    } else {
      messageApi.warning("메시지를 입력해주세요.");
      return;
    }
  };
  const handleCancel = () => {
    setIsModalVisible(false);
  };

  const sendMessage = (query: string) => {
    console.log("sendMessage", query);
    // https://demo-app-test-556320446019.us-central1.run.app
    // http://127.0.0.1:8000
    axios
      .post("http://127.0.0.1:8010", {
        query: query,
      })
      .then((res) => {
        if (res.status == 200) {
          console.log(res.data);
          const data = res.data;
          updateLastAiMessage({
            message: data.filter_text ? data.filter_text : data.answer_text,
            tools: data.references.length > 0 ? data.references : null,
            type: "success",
          });

          setQnaList(data.related_qna_list);
          setRelatedQuestionsList(data.related_questions);
        }
      })
      .catch((err) => {
        console.log(err);
        updateLastAiMessage({
          message: "에러가 발생했습니다. 다시 시도해주세요.",
          type: "error",
        });
      });
  };
  const updateLastAiMessage = useCallback(
    (newData: Partial<DefaultChatMessageType>) => {
      if (!selectedAgent) return;
      const state = useChatStore.getState();
      const currentMessages = state.agentChatList[selectedAgent!] || [];
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
    [selectedAgent]
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
              {chat.tools && (
                <>
                  <Button
                    type="primary"
                    onClick={() => {
                      setIsModalVisible(true);
                    }}
                  >
                    References
                  </Button>

                  <ScrollModal
                    title=" References"
                    isVisible={isModalVisible}
                    onClose={handleCancel}
                  >
                    {chat.tools.map((tool, index) => (
                      <div key={index}>
                        <Link
                          href={tool.url_page}
                          style={{
                            fontSize: "20px",
                            fontWeight: "bold",
                          }}
                          target="_blank"
                        >
                          {tool.title}
                        </Link>
                        <div
                          style={{
                            margin: "10px 0 15px",
                            display: "flex",
                            flexWrap: "wrap",
                            gap: "5px",
                          }}
                        >
                          <Tag>
                            <strong>Page:</strong> {tool.pageIdentifier}
                          </Tag>
                          <Tag
                            color={
                              tool.relevanceScore > 0.5 ? "green" : "orange"
                            }
                          >
                            Relevance: {tool.relevanceScore.toFixed(2)}
                          </Tag>
                        </div>

                        <p>{tool.content}</p>
                        <Divider />
                      </div>
                    ))}
                  </ScrollModal>
                </>
              )}
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
          resetChatList(selectedAgent!);
        }}
      />
    </div>
  );
};
