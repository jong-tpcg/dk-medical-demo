import { create } from "zustand";
import { agentConfig } from "@/features/agents/agentConfig";
import { DefaultChatMessageType } from "@/components/ui/chat";

export type ChatTypeMap = {
  default: DefaultChatMessageType[];
};

type AgentChatDataType = {
  [key in keyof typeof agentConfig]:
    | ChatTypeMap[(typeof agentConfig)[key]["type"]]
    | [];
};
type QnaStore = {
  answer: string;
  question: string;
  documnt_title: string;
  documnt_content: string;
};
type ChatStore = {
  agentChatList: AgentChatDataType;
  qnalist: QnaStore[] | null;
  setQnaList: (qnaList: QnaStore[]) => void;
  addChatMessage: <T extends keyof AgentChatDataType>(
    agent: T,
    message: ChatTypeMap[(typeof agentConfig)[T]["type"]][number]
  ) => void;
  resetChatList: (agent: keyof AgentChatDataType) => void;
};

export const useChatStore = create<ChatStore>((set) => ({
  qnalist: null,
  setQnaList: (qnaList) => {
    set({ qnalist: qnaList });
  },
  agentChatList: Object.keys(agentConfig).reduce((acc, key) => {
    acc[key as keyof typeof agentConfig] = []; // 초기값은 빈 배열
    return acc;
  }, {} as AgentChatDataType),

  addChatMessage: (agent, message) => {
    set((state) => ({
      agentChatList: {
        ...state.agentChatList,
        [agent]: [...state.agentChatList[agent], message],
      },
    }));
  },
  resetChatList: (agent) => {
    set((state) => ({
      agentChatList: {
        ...state.agentChatList,
        [agent]: [],
      },
    }));
  },
}));
