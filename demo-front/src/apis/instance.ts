import { addRequestLogging } from "@/hooks/addRequestLogging";
import axios, { AxiosInstance, AxiosRequestConfig } from "axios";

const API_URLS: Record<"base" | "medical_t" | "medical_r", string> = {
  base: "default",
  medical_t: "https://transcribe-api-661430115304.us-central1.run.app",
  medical_r: "https://medical-record-api-661430115304.us-central1.run.app",
};

/**
 * Axios 인스턴스를 생성하는 함수
 * @param type - API 유형 (일반 또는 인증 API)
 * @param options - 추가 Axios 설정
 * @returns AxiosInstance
 */

export const axiosAPI = (
  type: keyof typeof API_URLS,
  options: AxiosRequestConfig = {}
): AxiosInstance => {
  const baseURL = API_URLS[type];
  if (!baseURL) {
    throw new Error(`Invalid API URL type: ${type}`);
  }
  const instance = axios.create({
    baseURL,
    ...options,
  });
  addRequestLogging(instance);
  return instance;
};

export const axiosAuthAPI = (
  type: keyof typeof API_URLS,
  options: AxiosRequestConfig = {}
): AxiosInstance => {
  const baseURL = API_URLS[type];
  if (!baseURL) {
    throw new Error(`Invalid API URL type: ${type}`);
  }

  const instance = axios.create({
    baseURL,
    ...options,
  });
  addRequestLogging(instance);
  return instance;
};
