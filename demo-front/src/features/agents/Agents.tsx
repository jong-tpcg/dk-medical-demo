import { useEffect, useRef, useState } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import { Card, Button, message, Select } from "antd";
import {
  LeftOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  RightOutlined,
} from "@ant-design/icons";
import "@/styles/agents.scss";
import "@/styles/d_chat.scss";
import Sider from "antd/es/layout/Sider";
import IImg from "@/assets/agents/1.jpg";
import NImg from "@/assets/agents/2.jpg";
import DImg from "@/assets/agents/3.jpg";
import { useChatStore } from "@/store/chatStore";
import { Spinner } from "@/components/ui/spinner/Spinner";
import { DefaultChatMessageType, QnaStore } from "@/components/ui/chat";

const agents = [
  {
    title: "보험심사 관련 규정",
    img: IImg,
    route: "insurance",
    status: "active",
  },
  {
    title: "간호자격심사 관련 규정",
    img: NImg,
    route: "nursing",
    status: "inactive",
  },
  {
    title: "표준진료 관련 규정",
    img: DImg,
    route: "treatment",
    status: "inactive",
  },
];
export const Agents = () => {
  const navigate = useNavigate();
  const { Option } = Select;
  const [showLeftArrow, setShowLeftArrow] = useState(false);
  const [showRightArrow, setShowRightArrow] = useState(false);
  const rowRef = useRef<HTMLDivElement | null>(null);
  const [messageApi, contextHolder] = message.useMessage();
  const [collapsed, setCollapsed] = useState(false);
  const selectedAgent = useChatStore((state) => state.selectedAgent);
  const setSelectedAgent = useChatStore((state) => state.setSelectedAgent);
  const qnaList = useChatStore((state) => state.qnaList);
  // const relatedQuestionsList = useChatStore(
  //   (state) => state.relatedQuestionsList
  // );
  const addChatMessage = useChatStore((state) => state.addChatMessage);

  const handleCardClick = (route: string) => {
    //agents에서 선택한 agent의 route에 해당하는 객체의 status확인
    const selectedAgent = agents.find((agent) => agent.route === route);
    if (selectedAgent?.status === "inactive") {
      messageApi.warning("준비중인 기능입니다.");
    } else {
      navigate(`/d-chat/${route}`);
      setSelectedAgent(route);
    }
  };
  useEffect(() => {
    const currentPath = location.pathname;
    if (currentPath.includes("d-chat/")) {
      const agent = currentPath.split("/").pop();
      if (agent) setSelectedAgent(agent);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const scrollRight = () => {
    if (rowRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = rowRef.current;
      const remainingScroll = scrollWidth - clientWidth - scrollLeft;

      rowRef.current.scrollBy({
        left: Math.min(400, remainingScroll),
        behavior: "smooth",
      });
      updateArrows();
    }
  };

  const scrollLeft = () => {
    if (rowRef.current) {
      const scrollAmount = Math.min(400, rowRef.current.scrollLeft);
      rowRef.current.scrollBy({
        left: -scrollAmount,
        behavior: "smooth",
      });
      updateArrows();
    }
  };
  const updateArrows = () => {
    if (rowRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = rowRef.current;
      setShowLeftArrow(scrollLeft > 0);
      setShowRightArrow(scrollLeft + clientWidth < scrollWidth);
    }
  };
  const addQnaToChat = (qna: QnaStore) => {
    if (!selectedAgent) return;
    const userMessage: DefaultChatMessageType = {
      message: qna.question,
      tools: null,
      time: new Date().toLocaleTimeString(),
      sender: "user",
      model: "default",
    };
    const newAnswerMessage: DefaultChatMessageType = {
      message: qna.answer,
      tools: null,
      time: new Date().toLocaleTimeString(),
      sender: "ai",
      model: "default",
    };
    addChatMessage(selectedAgent, userMessage);
    addChatMessage(selectedAgent, newAnswerMessage);
  };
  useEffect(() => {
    const row = rowRef.current;
    if (!row) return;

    const updateArrowVisibility = (entries: IntersectionObserverEntry[]) => {
      entries.forEach((entry) => {
        if (entry.target === row.firstChild) {
          setShowLeftArrow(!entry.isIntersecting);
        }
        if (entry.target === row.lastChild) {
          setShowRightArrow(!entry.isIntersecting);
        }
      });
    };

    const observerOptions = {
      root: row,
      threshold: 1.0,
    };

    const observer = new IntersectionObserver(
      updateArrowVisibility,
      observerOptions
    );

    if (row.firstChild) observer.observe(row.firstChild as Element);
    if (row.lastChild) observer.observe(row.lastChild as Element);

    return () => observer.disconnect();
  }, []);

  return (
    <div className="agent-box-container">
      <Sider width={200} className="chat-sider" collapsed={collapsed}>
        <Button
          onClick={() => setCollapsed(!collapsed)}
          shape="circle"
          icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          size="middle"
          className="sider-button"
        />
        {!collapsed && (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              height: "100%",
            }}
          >
            {/* D-Chat 타이틀 */}
            <div
              style={{
                fontWeight: "bold",
                fontSize: "20px",
                marginBottom: "20px",
                color: "#1b1f26b8",
              }}
            >
              D-Chat
            </div>

            {/* 새 채팅 버튼 */}
            <div
              style={{
                marginBottom: "20px",
                fontSize: "14px",
                fontWeight: "bold",
                color: "#1890ff",
                cursor: "pointer",
              }}
            >
              [+ 새채팅]
            </div>

            <div className="task-block">
              <h5>즐겨찾기:</h5>
              <ul>
                <li>최근 고시</li>
                <li>요양급여 행위별</li>
                <li>요양급여 (약제)</li>
              </ul>
            </div>

            <div className="task-block">
              <h5>최근채팅:</h5>
              <ul>
                <li>최근 고시는 ... </li>
                <li>응급진료수가 는 ...</li>
                <li>제2024-181호의 ...</li>
              </ul>
            </div>

            {/* 하단 사용자 정보 */}
            <div
              style={{
                marginTop: "auto",
                fontSize: "14px",
                color: "#1b1f26b8",
              }}
            >
              <strong>보험심사팀</strong> 한DK 님
            </div>
          </div>
        )}
      </Sider>
      <div
        style={{
          width: "100%",
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
          height: "100%",
        }}
      >
        <div className="my-agents-wrapper">
          <h2>전문분야</h2>
          <div className="my-agents-container">
            {showLeftArrow && (
              <div className="arrow-button-wrapper left">
                <Button className="arrow-button left" onClick={scrollLeft}>
                  <LeftOutlined />
                </Button>
              </div>
            )}

            <div className="agents-scroll-wrapper" ref={rowRef}>
              {contextHolder}
              {agents.map((agent) => (
                <div
                  key={agent.title}
                  className={`agent-col  ${agent.status === "active" ? "" : "inactive"} ${selectedAgent !== agent.route ? "" : "dimmed"}`}
                >
                  <Card
                    className="agent-card"
                    hoverable
                    cover={
                      agent.img ? (
                        <img alt={agent.title} src={agent.img} />
                      ) : (
                        <div
                          style={{
                            backgroundColor: "#f0f0f0", // 원하는 배경색
                            height: "100%",
                          }}
                        />
                      )
                    }
                    onClick={() => handleCardClick(agent.route)}
                  >
                    <Card.Meta
                      title={agent.title}
                      className="card-meta-title"
                    />
                  </Card>
                </div>
              ))}
            </div>

            {showRightArrow && (
              <div className="arrow-button-wrapper right">
                <Button className="arrow-button right" onClick={scrollRight}>
                  <RightOutlined />
                </Button>
              </div>
            )}
          </div>
        </div>
        {selectedAgent && <Outlet />}
      </div>
      <div className="task-sider-wrapper">
        <Card
          className="task-card"
          title={
            <h1
              style={{
                color: "#7d8fb3",
                textAlign: "center",
                fontSize: "1.6rem",
              }}
            >
              My Task
            </h1>
          }
          bordered={false}
        >
          <div className="task-block">
            <h5>사용자 관심분야</h5>
            <Select
              placeholder="관심 분야를 선택해주세요"
              style={{ width: "100%", color: "#7d8fb3" }}
            >
              <Option value="insurance">보험심사 관련규정</Option>
              <Option value="nursing">간호자격심사 관련 규정</Option>
              <Option value="standardCare">표준진료 관련 규정</Option>
            </Select>
          </div>

          <div className="task-block">
            <h5>보험 심사 관련 규정</h5>
            <ul>
              <li>요양급여의 적용기준 및 방법에 관한 세부사항 </li>
              <li>요양급여의 적용기준 및 방법에 관한 세부사항 (약제)</li>
            </ul>
          </div>
          <div className="task-block">
            <h5>QNA</h5>
            <ul>
              {qnaList === "loading" ? (
                <Spinner type="llm" />
              ) : (
                qnaList?.map((qna, id) => (
                  <button
                    key={id}
                    onClick={() => {
                      addQnaToChat(qna);
                    }}
                    style={{
                      background: "none",
                      border: "none",
                      color: "blue",
                      cursor: "pointer",
                    }}
                  >
                    <li>{qna.question}</li>
                  </button>
                ))
              )}
            </ul>
          </div>
        </Card>
      </div>
    </div>
  );
};
