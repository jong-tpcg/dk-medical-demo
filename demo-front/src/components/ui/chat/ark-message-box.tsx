import ReactMarkdown from "react-markdown";
import rehypeRaw from "rehype-raw";
import rehypePrism from "rehype-prism-plus";
import remarkGfm from "remark-gfm";
import { useEffect, useState } from "react";
import { HoverLink } from "./hover-link";

interface ArkMessageBoxType {
  children?: React.ReactNode;
  message?: string;
  markdownMessage?: string;
  isCompact?: boolean;
  type?: string;
  htmlLink?: string;
  auto?: boolean;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  urls: any[] | null;
}

export const ArkMessageBox = ({
  children,
  isCompact = false,
  type,
  message,
  markdownMessage,
  htmlLink,
  auto = false,
  urls,
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
                  <HoverLink
                    href={href}
                    children={children}
                    urls={urls && urls}
                  />
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
