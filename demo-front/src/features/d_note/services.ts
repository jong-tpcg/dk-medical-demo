import { TranscriptType, MedicalChatMessage } from "./types";

export const extractTranscriptionData = (
  data: TranscriptType[]
): MedicalChatMessage[] => {
  // 메시지 데이터 변환
  return data.map((msg: TranscriptType) => ({
    speaker: msg.speaker,
    time: msg.timecode,
    message: msg.transcript,
    sender: msg.speaker,
  }));
};
