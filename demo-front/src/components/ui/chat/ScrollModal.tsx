import { Button, Modal } from "antd";
import "@/styles/modal-scroll.scss";
interface ScrollModalProps {
  isVisible: boolean;
  onClose: () => void;
  title: string;
  header?: React.ReactNode;
  width?: number;
  children?: React.ReactNode;
  footer?: React.ReactNode;
}

export const ScrollModal = ({
  isVisible,
  onClose,
  title,
  width = 1000,
  children,
  header,
  footer = (
    <Button key="close" onClick={onClose} style={{ marginLeft: "auto" }}>
      닫기
    </Button>
  ),
}: ScrollModalProps) => {
  return (
    <Modal
      width={width}
      open={isVisible}
      onCancel={onClose}
      className="modal-custom"
      footer={[footer]}
    >
      <div className="title">{title}</div>
      {header && <div className="header-content">{header}</div>}
      <div className="modal-content">{children}</div>
    </Modal>
  );
};
