import { useEffect, useRef, useState } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import { Card, Button, message } from "antd";
import {
  LeftOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  RightOutlined,
} from "@ant-design/icons";
import "@/styles/agents.scss";
import "@/styles/d_chat.scss";
import Sider from "antd/es/layout/Sider";
import IImg from "@/assets/agents/2.jpg";

const agents = [
  { title: "일반", img: "", route: "normal", status: "active" },
  {
    title: "보험심사 관련 규정",
    img: IImg,
    route: "insurance",
    status: "active",
  },
  {
    title: "간호자격심사 관련 규정",
    img: "",
    route: "nursing",
    status: "active",
  },
  {
    title: "표준진료 관련 규정",
    img: "",
    route: "treatment",
    status: "active",
  },
];
export const Agents = () => {
  const navigate = useNavigate();
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [showLeftArrow, setShowLeftArrow] = useState(false);
  const [showRightArrow, setShowRightArrow] = useState(false);
  const rowRef = useRef<HTMLDivElement | null>(null);
  const [messageApi, contextHolder] = message.useMessage();
  const [collapsed, setCollapsed] = useState(false);

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
    <div className="chat-container">
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
                color: "#007bff",
                cursor: "pointer",
              }}
            >
              [+ 새채팅]
            </div>

            {/* 즐겨찾기 섹션 */}
            <div
              style={{
                marginBottom: "20px",
                fontSize: "14px",
              }}
            >
              <strong>즐겨찾기:</strong>
              <ul
                style={{
                  paddingLeft: "20px",
                  marginTop: "10px",
                }}
              >
                <li>최근 고시</li>
                <li>요양급여 행위별</li>
                <li>요양급여 (약제)</li>
              </ul>
            </div>

            {/* 최근 채팅 섹션 */}
            <div
              style={{
                marginBottom: "20px",
                fontSize: "14px",
              }}
            >
              <strong>최근채팅:</strong>
              <ul
                style={{
                  paddingLeft: "20px",
                  marginTop: "10px",
                }}
              >
                <li>최근 고시는 ...</li>
                <li>응급진료수가 는 ...</li>
                <li>제2024-181호의 ...</li>
              </ul>
            </div>

            {/* 하단 사용자 정보 */}
            <div
              style={{
                marginTop: "auto",
                fontSize: "14px",
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
        {selectedAgent && <Outlet context={{ selectedAgent }} />}
      </div>
    </div>
  );
};
