import { axiosAuthAPI } from "./instance";
import { TranscriptType } from "@/features/d_note/types";

export const uploadMusicFileApi = async (
  file: File
): Promise<string | null> => {
  const formData = new FormData();
  formData.append("upload_file", file);

  const { data } = await axiosAuthAPI("medical_t").post(
    "/gcs/upload",
    formData
  );
  return data;
};

export const transcribeAudioApi = async (
  uri: string
): Promise<TranscriptType[] | null> => {
  const { data } = await axiosAuthAPI("medical_t").post(
    `/transcribe/?type=medical`,
    { uri }
  );
  return data;
};

export const summaryRecordApi = async (
  transcribeList: TranscriptType[],
  model: string
): Promise<string | null> => {
  console.log("test", transcribeList);
  const modelQuery =
    model === "gemini" ? "gemini-1.5-flash" : "medlm-large-1.5@001 etc.";
  const { data } = await axiosAuthAPI("medical_r").post(
    `/medical-record/body?type=general&model=${modelQuery}`,
    { transcript: transcribeList }
  );
  console.log(model);
  return data;
};
