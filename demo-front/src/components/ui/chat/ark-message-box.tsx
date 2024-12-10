import ReactMarkdown from "react-markdown";
import rehypeRaw from "rehype-raw";
import rehypePrism from "rehype-prism-plus";
import remarkGfm from "remark-gfm";
import { useEffect, useState } from "react";

interface ArkMessageBoxType {
  children?: React.ReactNode;
  message?: string;
  markdownMessage?: string;
  isCompact?: boolean;
  type?: string;
  htmlLink?: string;
  auto?: boolean;
}

export const ArkMessageBox = ({
  children,
  isCompact = false,
  type,
  message,
  markdownMessage,
  htmlLink,
  auto = false,
}: ArkMessageBoxType) => {
  const [combinedMessage, setCombinedMessage] = useState<string | null>(null);

  useEffect(() => {
    if (markdownMessage) {
      const text = markdownMessage
        // 굵은 텍스트(**bold**) 처리
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        // 코드 블록 제거
        .replace(/```[\s\S]*?```/g, "");

      setCombinedMessage(text);
    }
  }, [markdownMessage]);

  return (
    <div
      className={`message-box ark ${isCompact ? "compact" : ""} ${type ? type : ""} ${auto ? "auto" : ""}`}
    >
      {message && message}
      {htmlLink && (
        <iframe
          src={htmlLink}
          title="HTML Content"
          style={{
            width: "100%",
            height: "100vh",
            border: "none",
            overflow: "hidden",
          }}
        ></iframe>
      )}
      {children ? (
        <>{children}</>
      ) : (
        <div className="markdown">
          {combinedMessage && (
            <ReactMarkdown
              rehypePlugins={[rehypeRaw, rehypePrism]}
              remarkPlugins={[remarkGfm]}
              components={{
                a: ({ href, children }) => (
                  <a
                    href={href}
                    target="_blank"
                    style={{
                      display: "inline-block",
                      alignItems: "center",
                      justifyContent: "center",
                      width: "auto",
                      padding: "0.25rem 0.5rem",
                      marginLeft: "0.25rem",
                      borderRadius: "10px",
                      backgroundColor: "#E3F2FD ",
                      fontSize: "0.8rem",
                      color: " #1565C0 ",
                      textAlign: "center",
                      fontWeight: "bold",
                      border: "1px solid white",
                      textDecoration: "none",
                    }}
                  >
                    {children}
                  </a>
                ),
              }}
            >
              {combinedMessage}
            </ReactMarkdown>
          )}
        </div>
      )}
    </div>
  );
};
