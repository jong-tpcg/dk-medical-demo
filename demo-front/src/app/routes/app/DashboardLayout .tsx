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
        <Sider width={270} className="task-sider">
          <Card
            style={{
              minHeight: "100%",
              maxHeight: "calc(100vh - 160px)",
              overflowY: "auto",
            }}
            bordered={false}
          >
            <div
              style={{
                marginBottom: "20px",
                fontWeight: "bold",
                fontSize: "16px",
              }}
            >
              사용자 관심분야
            </div>
            <div style={{ marginBottom: "20px" }}>
              <select
                style={{ width: "100%", padding: "5px", fontSize: "14px" }}
              >
                <option>일반</option>
                <option>보험심사 관련규정</option>
                <option>간호자격심사 관련 규정</option>
                <option>표준진료 관련 규정</option>
              </select>
            </div>

            <div
              style={{
                marginBottom: "10px",
                fontWeight: "bold",
                fontSize: "16px",
              }}
            >
              보험심사관련규정
            </div>

            <ul
              style={{
                marginBottom: "10px",
                paddingLeft: "20px",
                fontSize: "14px",
              }}
            >
              <li>요양급여의 적용기준 및 방법에 관한 세부사항 [링크]</li>
              <li>요양급여의 적용기준 및 방법에 관한 세부사항 (약제) [링크]</li>
            </ul>

            <div
              style={{
                marginBottom: "10px",
                fontWeight: "bold",
                fontSize: "16px",
              }}
            >
              자주하는 질문:
            </div>
            <ul
              style={{
                marginBottom: "10px",
                paddingLeft: "20px",
                fontSize: "14px",
              }}
            >
              <li>최근 고시 목록</li>
              <li>예정 고시 목록</li>
              <li>응급의료수가 관련 ...</li>
            </ul>

            <div
              style={{
                marginBottom: "10px",
                fontWeight: "bold",
                fontSize: "16px",
              }}
            >
              사용자정의의 자주하는 질문:
            </div>
            <ul
              style={{
                marginBottom: "10px",
                paddingLeft: "20px",
                fontSize: "14px",
              }}
            >
              <li>최근 고시 목록</li>
              <li>예정 고시 목록</li>
              <li>응급의료수가 관련 ...</li>
            </ul>

            <div style={{ fontWeight: "bold", fontSize: "16px" }}>용어사전</div>
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
