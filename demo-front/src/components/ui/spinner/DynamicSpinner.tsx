import { Flex } from "antd";
import CLoading from "@/assets/chat_loading.gif";
import LLoading from "@/assets/llm_loading.gif";
import "@/styles/spinner.scss";

interface DynamicSpinnerProps {
  type?: "chat" | "llm";
  currentMessage: string;
}

export const DynamicSpinner = ({
  type = "llm",
  currentMessage,
}: DynamicSpinnerProps) => {
  const gifSrc = type === "llm" ? LLoading : CLoading;

  return (
    <Flex className="spinner" align="center" justify="flex-start" gap="middle">
      <div className="dynamic-loading">
        {currentMessage.split("").map((char, index) => (
          <span
            key={index}
            className={`animated-char ${char === " " ? "space" : ""}`}
            style={{ "--i": index } as React.CSSProperties}
          >
            {char}
          </span>
        ))}
      </div>
      <img className="loading-gif" src={gifSrc} alt="Loading..." />
    </Flex>
  );
};
