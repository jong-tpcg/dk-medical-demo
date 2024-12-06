import { Layout, Menu, message, Typography, Col } from "antd";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import DK_LOGO from "@/assets/dk_logo.png";
import TPCG_G from "@/assets/google.png";
import "@/styles/layout.scss";
import { Footer } from "antd/es/layout/layout";
import { useEffect, useState } from "react";
import { AiOutlineComment, AiOutlineDashboard } from "react-icons/ai";
import { MdOutlineMedicalServices } from "react-icons/md";
import { TbBook2 } from "react-icons/tb";
import { FaInfo, FaRegCircleQuestion } from "react-icons/fa6";

const { Header, Sider, Content } = Layout;
const { Title, Text } = Typography;

const items = [
  {
    key: "d-note",
    label: "D-Note",
    icon: <TbBook2 size={20} />,
    status: "active",
    children: [
      {
        key: "dashboard",
        label: <p>경과기록지 작성</p>,
        icon: <AiOutlineDashboard size={20} />,
      },
      {
        key: "summary",
        label: <p>진료상담 요약</p>,
        icon: <MdOutlineMedicalServices size={20} />,
      },
    ],
  },
  {
    key: "d-chat",
    label: "D-Chat",
    icon: <AiOutlineComment size={20} />,
    status: "active",
  },
  {
    key: "d-qna",
    label: "D-Qna",
    icon: <FaRegCircleQuestion size={20} />,
    status: "inactive",
  },
  {
    key: "d-inq",
    label: "D-INQ",
    icon: <FaInfo size={20} />,
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
    } else if (selectedItem == undefined) {
      const selectedItem = items.find((item) =>
        item.children?.find((child) => child.key === e.key)
      );
      if (e.key === "dashboard") {
        return window.open(
          "https://hallym-poc-demo-556320446019.us-central1.run.app/",
          "_blank"
        );
      } else {
        navigate(`${selectedItem?.key}/${e.key}`);
      }
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
            onClick={() => {
              navigate("/");
            }}
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
        <Sider className="custom-sider" width={240}>
          <div className="menu-wrapper">
            <h1>MAIN MENU</h1>
            <Menu
              mode="inline"
              className="custom-menu"
              defaultSelectedKeys={["/dashboard/d-note"]}
              items={items}
              onClick={onMenuClick}
            />
          </div>
        </Sider>
        <Content className="content">
          <Outlet />
        </Content>
      </Layout>
      <Footer
        style={{
          backgroundColor: "white",
          padding: "10px 0",
          borderTop: "2px solid #f7f8fa",
          textAlign: "center",
          height: "40px",
        }}
      >
        <Col>
          <Text
            style={{
              fontSize: "12px",
              fontWeight: "900",
              textAlign: "center",
            }}
          >
            <span>© 2024 &nbsp;TP</span>
            <span style={{ color: "#82B8AC", fontWeight: "bold" }}>
              CG&nbsp;
            </span>
            <Text style={{ fontSize: "11px", color: "black" }}>
              ALL RIGHTS RESERVED
            </Text>
          </Text>
        </Col>
      </Footer>
    </Layout>
  );
};
