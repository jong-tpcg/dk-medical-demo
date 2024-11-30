import {
  FileTextOutlined,
  InfoCircleOutlined,
  MessageOutlined,
  QuestionCircleOutlined,
} from "@ant-design/icons";
import { Layout, Menu, Card, message, Typography, Col } from "antd";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import DK_LOGO from "@/assets/dk_logo.png";
import TPCG_G from "@/assets/tpcg_google.png";
import "@/styles/layout.scss";
import { Footer } from "antd/es/layout/layout";
import { useEffect, useState } from "react";

const { Header, Sider, Content } = Layout;
const { Title, Text } = Typography;

const items = [
  {
    key: "d-note",
    label: "D-Note",
    icon: <FileTextOutlined />,
    status: "inactive",
  },
  {
    key: "d-chat",
    label: "D-Chat",
    icon: <MessageOutlined />,
    status: "active",
  },
  {
    key: "d-qna",
    label: "D-Qna",
    icon: <QuestionCircleOutlined />,
    status: "inactive",
  },
  {
    key: "d-inq",
    label: "D-INQ",
    icon: <InfoCircleOutlined />,
    status: "inactive",
  },
];

export const DashboardLayout = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [messageApi, contextHolder] = message.useMessage();
  const [title, setTitle] = useState("DK AI Platform");
  const onMenuClick = (e: { key: string }) => {
    const selectedItem = items.find((item) => item.key === e.key);
    if (selectedItem?.status === "active") {
      navigate(e.key);
    } else {
      messageApi.warning("준비중인 기능입니다.");
    }
  };
  useEffect(() => {
    const currentPath = location.pathname.split("/")[1];
    const selectedItem = items.find((item) => item.key === currentPath);

    if (selectedItem) {
      setTitle(selectedItem.label);
    } else {
      setTitle("DK AI Platform");
    }
  }, [location.pathname]);

  return (
    <Layout style={{ minHeight: "100vh" }}>
      {contextHolder}
      <Header className="header">
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            position: "relative",
            height: "100%",
          }}
        >
          {/* 왼쪽 로고 */}
          <div
            style={{
              position: "absolute",
              left: 0,
              display: "flex",
              alignItems: "flex-end",
            }}
            onClick={() => navigate("/")}
          >
            <img src={DK_LOGO} alt="Logo" style={{ height: "30px" }} />
          </div>

          {/* 중앙 타이틀 */}
          <Title
            level={3}
            style={{
              margin: 0,
              fontWeight: "bold",
              textAlign: "center",
              lineHeight: "normal",
            }}
          >
            {title}
          </Title>

          {/* 오른쪽 로고 */}
          <div
            style={{
              position: "absolute",
              right: 0,
              display: "flex",
              alignItems: "flex-end",
            }}
          >
            <img src={TPCG_G} alt="Logo" style={{ height: "30px" }} />
          </div>
        </div>
      </Header>
      <Layout className="layout">
        <Sider theme="light" width={140}>
          <Menu
            className="menu-wrapper"
            mode="inline"
            theme="light"
            defaultSelectedKeys={["/dashboard/d-note"]}
            items={items}
            onClick={onMenuClick}
          />
        </Sider>
        <Content className="content">
          <Outlet />
        </Content>
        <Sider width={300} className="task-sider">
          <Card title="MY TASK" bordered={false}>
            <p>Card content</p>
            <p>Card content</p>
            <p>Card content</p>
          </Card>
        </Sider>
      </Layout>
      <Footer
        style={{
          backgroundColor: "white",
          padding: "15px 0",
          borderTop: "2px solid #f7f8fa",
          textAlign: "center",
        }}
      >
        <Col>
          <Text
            style={{
              fontSize: "13px",
              fontWeight: "900",
              textAlign: "center",
            }}
          >
            <span>© 2024 &nbsp;TP</span>
            <span style={{ color: "#82B8AC", fontWeight: "bold" }}>
              CG&nbsp;
            </span>
            <Text style={{ fontSize: "12px", color: "black" }}>
              ALL RIGHTS RESERVED
            </Text>
          </Text>
        </Col>
      </Footer>
    </Layout>
  );
};
