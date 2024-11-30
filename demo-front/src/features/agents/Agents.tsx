import { useState } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import { Card, Button } from "antd";
import { LeftOutlined, RightOutlined } from "@ant-design/icons";
import "@/styles/myagents.scss";
import FImg from "@/assets/finance.png";

const agents = [
  { title: "금융상품", img: FImg, route: "finance" },
  { title: "여행/맛집", img: "your_image_path_2", route: "travel" },
  { title: "공공 행정/지원", img: "your_image_path_3", route: "public" },
  { title: "기업문서", img: "your_image_path_4", route: "corporate" },
  { title: "생활법률", img: "your_image_path_5", route: "law" },
  { title: "제품문의", img: "your_image_path_6", route: "product" },
];
export const Agents = () => {
  const navigate = useNavigate();
  const [visibleStart, setVisibleStart] = useState(0);
  const visibleCount = 5;
  const handleCardClick = (route: string) => {
    navigate(`/agents/${route}`);
  };

  const scrollRight = () => {
    setVisibleStart((prev) =>
      Math.min(prev + visibleCount, agents.length - visibleCount)
    );
  };

  const scrollLeft = () => {
    setVisibleStart((prev) => Math.max(prev - visibleCount, 0));
  };

  const showLeftArrow = visibleStart > 0;
  const showRightArrow = visibleStart + visibleCount < agents.length;

  return (
    <div>
      <h2>My Agents</h2>
      <div className="my-agents-container">
        {showLeftArrow && (
          <Button className="arrow-button" onClick={scrollLeft}>
            <LeftOutlined />
          </Button>
        )}

        <div className="my-agents-row">
          {agents
            .slice(visibleStart, visibleStart + visibleCount)
            .map((agent) => (
              <div key={agent.title} className="agent-col">
                <Card
                  hoverable
                  cover={<img alt={agent.title} src={agent.img} />}
                  onClick={() => handleCardClick(agent.route)}
                >
                  <Card.Meta title={agent.title} className="card-meta-title" />
                </Card>
              </div>
            ))}
        </div>

        {showRightArrow && (
          <Button className="arrow-button" onClick={scrollRight}>
            <RightOutlined />
          </Button>
        )}
      </div>
      <Outlet />
    </div>
  );
};
