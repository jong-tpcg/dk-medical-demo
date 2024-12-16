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
  qnaList: QnaStore[] | "loading";
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

const defaultQnaList = [
  {
    answer:
      "감염관리 전담간호사는 감염관리실 업무를위해 배치된 인력으로 감염관리 업무만시행하여야 함.",
    document_title:
      "요양병원_감염예방관리료_질의응답(보건복지부+고시+제2023-109호,+제2024-78호)",
    question:
      "(1등급·2등급) 감염관리 전담간호사는 감염관리와 관련된 업무만 시행 하여야 하는지?",
    document_uri:
      "https://storage.googleapis.com/dk-demo/demo-qna/%EC%9A%94%EC%96%91%EB%B3%91%EC%9B%90_%EA%B0%90%EC%97%BC%EC%98%88%EB%B0%A9%EA%B4%80%EB%A6%AC%EB%A3%8C_%EC%A7%88%EC%9D%98%EC%9D%91%EB%8B%B5(%EB%B3%B4%EA%B1%B4%EB%B3%B5%EC%A7%80%EB%B6%80%2B%EA%B3%A0%EC%8B%9C%2B%EC%A0%9C2023-109%ED%98%B8%2C%2B%EC%A0%9C2024-78%ED%98%B8).pdf",
  },
  {
    question:
      "감염관리 전담간호사 및 감염관리 간호사 배치인력은 입원료 차등제 인력과 중복 적용할 수 있는지?",
    document_title:
      "요양병원_감염예방관리료_질의응답(보건복지부+고시+제2023-109호,+제2024-78호)",
    answer:
      "중복 적용할 수 없음. 감염관리 전담 간호사및 감염관리 간호사는 간호인력 확보수준에 따른 입원료 차등제 산정대상에서제외하여야 함. ",
    document_uri:
      "https://storage.googleapis.com/dk-demo/demo-qna/%EC%9A%94%EC%96%91%EB%B3%91%EC%9B%90_%EA%B0%90%EC%97%BC%EC%98%88%EB%B0%A9%EA%B4%80%EB%A6%AC%EB%A3%8C_%EC%A7%88%EC%9D%98%EC%9D%91%EB%8B%B5(%EB%B3%B4%EA%B1%B4%EB%B3%B5%EC%A7%80%EB%B6%80%2B%EA%B3%A0%EC%8B%9C%2B%EC%A0%9C2023-109%ED%98%B8%2C%2B%EC%A0%9C2024-78%ED%98%B8).pdf",
  },
  {
    document_uri:
      "https://storage.googleapis.com/dk-demo/demo-qna/%EC%9A%94%EC%96%91%EB%B3%91%EC%9B%90_%EA%B0%90%EC%97%BC%EC%98%88%EB%B0%A9%EA%B4%80%EB%A6%AC%EB%A3%8C_%EC%A7%88%EC%9D%98%EC%9D%91%EB%8B%B5(%EB%B3%B4%EA%B1%B4%EB%B3%B5%EC%A7%80%EB%B6%80%2B%EA%B3%A0%EC%8B%9C%2B%EC%A0%9C2023-109%ED%98%B8%2C%2B%EC%A0%9C2024-78%ED%98%B8).pdf",
    answer:
      "의료기관 인증 결과는 매월 건강보험심사평가원에연계 되고 있으므로 신고 불필요함. 단, 인증결과가 건강보험심사평원에 정상연계되었는지 아래 경로에서 확인 후 청구하여야 함. \n※보건의료자원통합신고포털(www.hurb.or.kr) > 현황신고·\r\n변경 > 특수운영현황 > 특수운영 지정현황 조회 >\r\n특수운영 현황 조회 > 의료기관 평가인증기관 확인가능",
    question:
      "의료기관 인증 결과가 ‘인증’\r\n또는 ‘조건부 인증’인 경우에도\r\n별도 신고를 해야 하나요?",
    document_title:
      "요양병원_감염예방관리료_질의응답(보건복지부+고시+제2023-109호,+제2024-78호)",
  },
];

export const useChatStore = create<ChatStore>((set) => ({
  selectedAgent: null,
  qnaList: defaultQnaList,
  relatedQuestionsList: [],
  setSelectedAgent: (selectedAgent) => {
    set({ selectedAgent });
  },
  setRelatedQuestionsList: (relatedQuestionsList) => {
    set({ relatedQuestionsList });
  },
  setQnaList: (qnaList: [] | "loading" | QnaStore[]) => {
    if (Array.isArray(qnaList) && qnaList.length === 0) {
      set({ qnaList: defaultQnaList });
    } else {
      set({ qnaList });
    }
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
