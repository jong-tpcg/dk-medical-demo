import { useEffect, useRef } from "react";

const useAutoScrollToBottom = (
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  dependencyArray: any[], // 배열
  delay = 200
) => {
  const previousLength = useRef(dependencyArray.length); // 이전 배열 길이를 저장하는 ref

  useEffect(() => {
    const scrollToBottom = () => {
      window.scrollTo({
        top: document.body.scrollHeight,
        behavior: "smooth",
      });
    };

    // 초기 스크롤 설정
    const initialScrollTimer = setTimeout(() => {
      scrollToBottom();
    }, delay);

    // 배열의 길이가 변경되면 스크롤을 아래로 이동
    if (previousLength.current !== dependencyArray.length) {
      console.log("scrolling");
      const scrollCheckTimer = setTimeout(() => {
        scrollToBottom();
      }, delay);

      previousLength.current = dependencyArray.length; // 최신 배열 길이로 업데이트

      // 클린업
      return () => {
        clearTimeout(scrollCheckTimer);
      };
    }

    // 클린업
    return () => {
      clearTimeout(initialScrollTimer);
    };
  }, [dependencyArray, delay]);
};

export default useAutoScrollToBottom;
