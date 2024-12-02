import { useEffect } from "react";

const useAutoScrollToBottom = (
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  dependencyArray: any[] | null,
  arkStatus: string,
  delay = 200
) => {
  useEffect(() => {
    // 처음에 약간의 지연 후 스크롤을 맨 아래로 설정
    const initialScrollTimer = setTimeout(() => {
      window.scrollTo({
        top: document.body.scrollHeight,
        behavior: "smooth",
      });
    }, delay); // 지연 시간 기본값 200ms

    // 메시지가 추가된 후 스크롤 확인 및 이동
    if (arkStatus !== "default") {
      const scrollCheckTimer = setTimeout(() => {
        if (window.scrollY + window.innerHeight < document.body.scrollHeight) {
          window.scrollTo({
            top: document.body.scrollHeight,
            behavior: "smooth",
          });
        }
      }, delay * 2); // 두 번째 타이머

      // 클린업
      return () => {
        clearTimeout(initialScrollTimer);
        clearTimeout(scrollCheckTimer);
      };
    }

    return () => {
      clearTimeout(initialScrollTimer);
    };
  }, [arkStatus, delay, dependencyArray]);
};

export default useAutoScrollToBottom;
