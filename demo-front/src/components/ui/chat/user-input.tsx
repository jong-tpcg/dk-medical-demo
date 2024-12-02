import "@/styles/chats-all.scss";
import { Button, Input } from "antd";
import { SendOutlined } from "@ant-design/icons";
import { FaRegSquare } from "react-icons/fa";
import { GrPowerReset } from "react-icons/gr";

interface InputComponentProps {
  inputValue: string;
  isResponding?: boolean; // 답변 대기 상태
  onInputChange: (value: string) => void;
  onSendMessage: () => void;
  onResetChat?: () => void;
}

export const UserInput = ({
  inputValue,
  isResponding = true,
  onInputChange,
  onSendMessage,
  onResetChat,
}: InputComponentProps) => {
  const { TextArea } = Input;
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSendMessage();
    }
  };
  const resetChat = () => {
    console.log("Reset Chatting");
    if (onResetChat) {
      onResetChat();
    }
  };
  return (
    <div className="search-input-wrapper">
      <div className="textarea-wrapper">
        <TextArea
          value={inputValue}
          onChange={(e) => onInputChange(e.target.value)}
          autoSize={{ minRows: 1, maxRows: 5 }}
          placeholder="질문을 입력하면 Ark가 분석을 시작합니다."
          className="chat-input"
          onKeyDown={handleKeyDown}
          disabled={!isResponding}
        />
        <Button
          type="primary"
          shape="circle"
          icon={isResponding ? <SendOutlined /> : <FaRegSquare />}
          onClick={onSendMessage}
          className="send-button"
        />
      </div>
      {onResetChat && (
        <Button
          type="primary"
          shape="circle"
          icon={<GrPowerReset />}
          onClick={resetChat}
          className="reset-button"
        />
      )}
    </div>
  );
};

export default UserInput;
