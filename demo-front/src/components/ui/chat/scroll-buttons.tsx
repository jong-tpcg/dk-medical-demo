import { useScrollPosition } from "@/utils/useScrollPosition";
import { DownOutlined, UpOutlined } from "@ant-design/icons";
import { Button } from "antd";

export const ScrollButtons = () => {
  const { isAtTop, isAtBottom, scrollToTop, scrollToBottom } =
    useScrollPosition();

  return (
    <>
      {!isAtTop && (
        <Button
          shape="circle"
          size="large"
          type="primary"
          icon={<UpOutlined />}
          onClick={scrollToTop}
          style={{
            position: "fixed",
            bottom: "70px",
            right: "20px",
            zIndex: 1000,
          }}
        />
      )}
      {!isAtBottom && (
        <Button
          shape="circle"
          size="large"
          icon={<DownOutlined />}
          onClick={scrollToBottom}
          style={{
            position: "fixed",
            bottom: "20px",
            right: "20px",
            zIndex: 1000,
          }}
        />
      )}
    </>
  );
};
