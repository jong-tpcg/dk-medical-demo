import { ChatTypeMap } from "@/store/chatStore";

type AgentConfigType = {
  [key: string]: {
    route: string;
    initialMessage: string;
    type: keyof ChatTypeMap;
  };
};

export const agentConfig: AgentConfigType = {
  normal: {
    route: "normal",
    initialMessage:
      "안녕하세요. 일반 분야  질문에 대한 상담을 도와드리겠습니다.",
    type: "default",
  },
  insurance: {
    route: "insurance",
    initialMessage:
      "안녕하세요. 보험심사 관련 규정 분야  질문에 대한 상담을 도와드리겠습니다.",
    type: "default",
  },
  nursing: {
    route: "nursing",
    initialMessage:
      "안녕하세요. 간호자격심사 관련 규정 분야  질문에 대한 상담을 도와드리겠습니다.",
    type: "default",
  },
  treatment: {
    route: "treatment",
    initialMessage:
      "안녕하세요. 표준진료 관련 규정 분야  질문에 대한 상담을 도와드리겠습니다.",
    type: "default",
  },
};
