import { create } from "zustand";
import { agentConfig } from "@/features/agents/agentConfig";
import { DefaultChatMessageType, QnaStore } from "@/components/ui/chat";

export type ChatTypeMap = {
  default: DefaultChatMessageType[];
};

type AgentChatDataType = {
  [key in keyof typeof agentConfig]:
    | ChatTypeMap[(typeof agentConfig)[key]["type"]]
    | [];
};
type ChatStore = {
  selectedAgent: string | null;
  agentChatList: AgentChatDataType;
  qnaList: QnaStore[] | [] | "loading";
  relatedQuestionsList: [] | [] | "loading";
  setSelectedAgent: (selectedAgent: string | null) => void;
  setRelatedQuestionsList: (relatedQuestionsList: [] | "loading") => void;
  setQnaList: (qnaList: QnaStore[] | "loading" | []) => void;
  addChatMessage: <T extends keyof AgentChatDataType>(
    agent: T,
    message: ChatTypeMap[(typeof agentConfig)[T]["type"]][number]
  ) => void;
  resetChatList: (agent: keyof AgentChatDataType) => void;
};

export const useChatStore = create<ChatStore>((set) => ({
  selectedAgent: null,
  qnaList: [],
  relatedQuestionsList: [],
  setSelectedAgent: (selectedAgent) => {
    set({ selectedAgent });
  },
  setRelatedQuestionsList: (relatedQuestionsList) => {
    set({ relatedQuestionsList });
  },
  setQnaList: (qnaList) => {
    set({ qnaList: qnaList });
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
