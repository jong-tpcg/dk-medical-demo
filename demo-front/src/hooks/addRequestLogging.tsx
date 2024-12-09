import { AxiosInstance } from "axios";

export const addRequestLogging = (instance: AxiosInstance) => {
  // 요청 성공 직전 호출됩니다.
  // axios 설정값을 넣습니다. (사용자 정의 설정도 추가 가능)
  instance.interceptors.request.use((config) => {
    const token = null;

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    console.log("=== Axios Request ===");
    console.log(
      "URL:",
      `${config.baseURL ?? ""}${config.url ?? ""}`,
      "\n Method:",
      config.method,
      "\n Headers:",
      config.headers,
      "\n Data:",
      config.data
    );
    console.log("=====================");
    return config;
  });

  instance.interceptors.response.use(
    (response) => {
      console.log("=== Axios Response ===");
      console.log("Status:", response.status);
      console.log("Data:", response.data);
      console.log("=======================");
      return response;
    },
    (error) => {
      if (error.response) {
        console.error(
          `=== Axios Error === \n`,
          "Status:",
          error.response.status ?? "Unknown",
          "\n Data:",
          error.response.data ?? "Unknown"
        );

        // Custom error handling
        if (error.response.status === 401) {
          console.warn("Unauthorized! Redirecting to login...");
          // Redirect to login page or refresh token
        } else if (error.response.status === 403) {
          console.warn("Forbidden! Check your permissions.");
        } else if (error.response.status >= 500) {
          console.error("Server error! Please try again later.");
        }
      }
      return Promise.reject(error);
    }
  );
};
