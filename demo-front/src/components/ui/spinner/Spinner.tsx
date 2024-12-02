import { Flex } from "antd";
import CLoading from "@/assets/chat_loading.gif";
import LLoading from "@/assets/llm_loading.gif";

interface SpinnerProps {
  type?: "chat" | "llm";
}

export const Spinner = ({ type = "chat" }: SpinnerProps) => {
  const gifSrc = type === "llm" ? LLoading : CLoading;
  return (
    <Flex align="center" gap="middle">
      <img src={gifSrc} alt="Loading..." />
    </Flex>
  );
};
