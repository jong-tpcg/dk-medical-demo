import { ConfigProvider } from "antd";

type AppProviderProps = {
  children: React.ReactNode;
};

const theme = {
  token: {
    colorPrimary: "#1890ff",
    colorPrimarySub: "#0b76b7",
    colorBgPrimary: "#f7f8fa",
    colorGray: "#f9f9f9",
  },
};

export const AppProvider = ({ children }: AppProviderProps) => {
  return <ConfigProvider theme={theme}>{children}</ConfigProvider>;
};
