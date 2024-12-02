import { useState, useEffect } from "react";

export const useScrollPosition = () => {
  const [isAtTop, setIsAtTop] = useState(true);
  const [isAtBottom, setIsAtBottom] = useState(false);
  const [isScrolling, setIsScrolling] = useState(false); // 스크롤 중인지 상태 추가

  useEffect(() => {
    const handleScroll = () => {
      if (isScrolling) return; // 스크롤 중일 때는 상태 업데이트를 막음

      const atTop = window.scrollY === 0;
      const atBottom =
        window.innerHeight + window.scrollY >= document.body.scrollHeight;

      setIsAtTop(atTop);
      setIsAtBottom(atBottom);
    };

    window.addEventListener("scroll", handleScroll);

    // 초기 상태 확인
    handleScroll();

    return () => window.removeEventListener("scroll", handleScroll);
  }, [isScrolling]);

  const scrollToTop = () => {
    setIsScrolling(true); // 스크롤 중임을 표시
    window.scrollTo({ top: 0, behavior: "smooth" });

    // 스크롤 완료 후 isScrolling을 해제하고 상태 업데이트
    setTimeout(() => {
      setIsScrolling(false);
      setIsAtTop(true); // 스크롤 완료 후 맨 위 상태 설정
      setIsAtBottom(false);
    }, 500); // 스크롤 애니메이션 시간에 맞춰 설정
  };

  const scrollToBottom = () => {
    setIsScrolling(true);
    window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });

    // 스크롤 완료 후 isScrolling을 해제하고 상태 업데이트
    setTimeout(() => {
      setIsScrolling(false);
      setIsAtBottom(true); // 스크롤 완료 후 맨 아래 상태 설정
      setIsAtTop(false);
    }, 500); // 스크롤 애니메이션 시간에 맞춰 설정
  };

  return { isAtTop, isAtBottom, scrollToTop, scrollToBottom };
};
