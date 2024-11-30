import { ConfigProvider } from "antd";

type AppProviderProps = {
  children: React.ReactNode;
};

const theme = {};

export const AppProvider = ({ children }: AppProviderProps) => {
  return <ConfigProvider theme={theme}>{children}</ConfigProvider>;
};
