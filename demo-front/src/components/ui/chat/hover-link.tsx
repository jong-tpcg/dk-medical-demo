import React, { useState, useEffect, useRef } from "react";

interface HoverLinkProps {
  href: string | undefined;
  children: React.ReactNode;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  urls: any[] | null;
}

export const HoverLink = ({ href, children, urls }: HoverLinkProps) => {
  const [isHovered, setIsHovered] = useState(false);
  const [hoverTitle, setHoverTitle] = useState("");
  const [hoverText, setHoverText] = useState("");
  const [position, setPosition] = useState({ top: 0, left: 0 });
  const [showLeft, setShowLeft] = useState(false); // 툴팁 방향 상태
  const linkRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (typeof children === "string" && !isNaN(Number(children))) {
      const childIndex = Number(children) - 1;
      if (urls && urls[childIndex]) {
        console.log("Hover text:", urls[childIndex]);
        setHoverTitle(urls[childIndex].reference_title);
        setHoverText(urls[childIndex].chunkText);
      }
    }
  }, [children, urls]);

  useEffect(() => {
    console.log(showLeft);
  }, [showLeft]);

  const handleMouseEnter = () => {
    setIsHovered(false);
    if (linkRef.current) {
      const rect = linkRef.current.getBoundingClientRect();
      const tooltipWidth = 400; // 예상 툴팁 너비
      const gap = 10; // 여백

      // 툴팁이 화면 끝을 넘어가면 왼쪽으로 표시
      const shouldShowLeft = rect.right + tooltipWidth > window.innerWidth;

      setShowLeft(shouldShowLeft);
      setPosition({
        top: rect.bottom + gap, // 아래쪽에 표시
        left: shouldShowLeft
          ? rect.left - tooltipWidth + rect.width
          : rect.left, // 왼쪽 이동
      });
    }
    // setIsHovered(true);
  };

  return (
    <div
      style={{
        position: "relative",
        display: "inline-block",
      }}
    >
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        onMouseEnter={handleMouseEnter}
        onMouseLeave={() => setIsHovered(false)}
        style={{
          alignItems: "center",
          justifyContent: "center",
          width: "auto",
          padding: "0.25rem 0.6rem",
          marginLeft: "0.4rem",
          borderRadius: "10px",
          backgroundColor: "#E3F2FD",

          fontSize: "0.8rem",
          color: "#1565C0",
          textAlign: "center",
          fontWeight: "bold",
          border: "1px solid white",
          textDecoration: "none",
        }}
      >
        {children}
      </a>

      {isHovered && (
        <div
          style={{
            position: "absolute", // 상대적 위치
            bottom: "100%", // a 태그 위에 위치
            transform: "translateY(-8px)", // 약간 위로 띄우기
            left: `${position.left}px`, // 왼쪽 끝에 맞춤
            maxWidth: "300px", // 최대 너비 지정
            maxHeight: "200px", // 최대 높이 지정
            width: "auto",
            height: "auto",
            backgroundColor: "white",
            border: "2px solid #E3F2FD",
            color: "#4d5e80",
            borderRadius: "8px",
            fontSize: "1.2rem",
            zIndex: 1000,
            lineHeight: "1.4",
            overflow: "hidden", // 넘치는 내용 숨기기
            padding: "1.2rem 2rem",
          }}
        >
          <div
            style={{
              fontWeight: "bold",
              marginBottom: "0.5rem",
              overflow: "hidden", // 넘치는 내용 처리
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
          >
            {hoverTitle}
          </div>
          <div
            style={{
              display: "-webkit-box", // 줄 제한을 위해 flexbox를 사용
              WebkitLineClamp: 4, // 최대 4줄로 제한
              WebkitBoxOrient: "vertical", // 수직 방향으로 박스 설정
              overflow: "hidden", // 넘치는 내용 숨기기
              textOverflow: "ellipsis", // 생략 부호 (...) 표시
            }}
          >
            {hoverText}
          </div>
        </div>
      )}
    </div>
  );
};

export default HoverLink;
