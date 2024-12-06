import { Button, Upload, message } from "antd";
import type { UploadFile, UploadProps } from "antd";
import "@/styles/chats-all.scss";
import "@/styles/medical-assistant.scss";
import ReactMarkdown from "react-markdown";
import { EyeOutlined, InboxOutlined } from "@ant-design/icons";
import { useEffect, useState } from "react";
import { ScrollModal } from "@/components/ui/chat/ScrollModal";
import {
  uploadMusicFileApi,
  transcribeAudioApi,
  summaryRecordApi,
} from "@/apis/medical";
import { DynamicSpinner } from "@/components/ui/spinner/DynamicSpinner";
import { MedicalChatMessage, TranscriptType } from "./types";
import { extractTranscriptionData } from "./services";
import { UserMessage } from "@/components/ui/chat";
import { ArkMessageBox } from "@/components/ui/chat/ark-message-box";
import { ArkDefault } from "@/components/ui/chat/ark-default";
import { ArkModelButtons } from "@/components/ui/chat/ark-model-buttons";

export const MedicalSummary = () => {
  const { Dragger } = Upload;
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [audioSrc, setAudioSrc] = useState<string | null>(null);
  const [messageApi, contextHolder] = message.useMessage();
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [loadingText, setLoadingText] = useState("로딩중");
  const [medicalChatMessages, setMedicalChatMessages] = useState<
    MedicalChatMessage[] | null
  >(null);
  const [medicalRecord, setMedicalRecord] = useState<string | null>(null);
  const [transcribeData, setTranscribeData] = useState<TranscriptType[] | null>(
    null
  );
  const [isLoading, setIsLoading] = useState(false);
  const [fail, setFail] = useState<boolean>(false);
  const [activeModel, setActiveModel] = useState<string>("gemini");

  // 파일 업로드 및 처리 흐름 함수
  const handleFileUpload = async (file: File) => {
    setIsLoading(true);
    setLoadingText("파일을 업로드 중입니다.");

    const gsUri = await uploadMusicFileApi(file).then((data) => {
      if (!data) {
        setLoadingText("파일 업로드에 실패했습니다.");
        throw new Error("File upload failed");
      }
      setLoadingText("음성에서 텍스트 추출중입니다.");
      return data;
    });

    const temp = await transcribeAudioApi(gsUri);
    setTranscribeData(temp);
    if (!temp) {
      setLoadingText("텍스트 추출에 실패했습니다.");
      throw new Error("Transcription data is null");
    }
    const formattedData = extractTranscriptionData(temp);
    setMedicalChatMessages(formattedData);

    setLoadingText("텍스트 추출 후 요약 생성 중입니다.");
  };
  useEffect(() => {
    if (transcribeData) {
      setIsLoading(true);
      summaryRecordApi(transcribeData, activeModel).then((data) => {
        if (!data) {
          setLoadingText("요약 생성에 실패했습니다.");
          throw new Error("Summary record failed");
        }
        setIsLoading(false);
        setMedicalRecord(data);
        setLoadingText("요약이 완료되었습니다.");
      });
    }
  }, [activeModel, transcribeData]);

  const showModal = () => {
    setIsModalVisible(true);
  };

  const handleCancel = () => {
    setIsModalVisible(false);
  };

  const props: UploadProps = {
    name: "file",
    multiple: false,
    customRequest: async (options) => {
      const { onSuccess, onError, file } = options;
      try {
        setFail(false);
        await handleFileUpload(file as File);
        if (onSuccess) {
          setIsLoading(false);
          onSuccess("파일 업로드 성공");
        }
      } catch (error) {
        setIsLoading(false);
        console.log("파일 업로드 실패", error);
        if (onError) {
          setFail(true);
          onError(error as Error);
        }
      }
    },
    beforeUpload: (file) => {
      const isAudio = file.type.startsWith("audio/");
      if (!isAudio) {
        messageApi.error("오디오 파일만 업로드 가능합니다.");
        return Upload.LIST_IGNORE;
      }
      setFileList([file]);
      setAudioSrc(URL.createObjectURL(file));
      return true;
    },
    onChange(info) {
      const { status } = info.file;
      if (status !== "uploading") {
        console.log(info.file, info.fileList);
      }
      if (status === "done") {
        setLoadingText(`파일을 업로드중입니다.`);
      } else if (status === "error") {
        messageApi.error(`${info.file.name} 파일 업로드에 실패했습니다.`);
        setFileList((prevList) =>
          prevList.filter((f) => f.uid !== info.file.uid)
        );
      }
    },
    fileList,
    onDrop(e) {
      console.log("드롭된 파일들", e.dataTransfer.files);
    },
  };

  return (
    <div className="medical-container">
      {contextHolder}
      <div className="audio-input-wrapper">
        <Dragger {...props}>
          <InboxOutlined className="audio-input-icon" />
          <p className="ant-upload-text">
            드래그하거나 클릭하여 음성 파일을 업로드하세요
          </p>
        </Dragger>
      </div>
      <ArkModelButtons
        model_list={[
          { label: "Gem 1.5 Flash", type: "gemini" },
          { label: "Medical", type: "medlm" },
        ]}
        align="right"
        isLoading={isLoading}
        onSwitchModel={(type) => {
          console.log("모델 변경", type);
          setActiveModel(type);
        }}
      />

      <div className="chat-list-wrapper">
        <ArkDefault>
          {fail ? (
            <ArkMessageBox>
              오류가 발생했습니다. 다시 업로드해주세요.
            </ArkMessageBox>
          ) : !isLoading && !audioSrc ? (
            <ArkMessageBox
              message="안녕하세요. 의료보험심사 Assistant 입니다. 음성파일을
              업로드해주시면 텍스트 추출 및 요약 작업을 진행합니다."
            />
          ) : isLoading ? (
            <DynamicSpinner currentMessage={loadingText} />
          ) : (
            <>
              <div className="audio-player-wrapper">
                <audio controls src={audioSrc!} />
              </div>
              <ArkMessageBox>
                {medicalRecord && (
                  <div className="medical-record-all markdown">
                    <ReactMarkdown>{medicalRecord}</ReactMarkdown>
                    <Button
                      onClick={showModal}
                      type="primary"
                      icon={<EyeOutlined className="icon" />}
                      style={{ height: "45px" }}
                    >
                      대화 전체보기
                    </Button>
                  </div>
                )}
              </ArkMessageBox>
            </>
          )}
        </ArkDefault>
      </div>

      <ScrollModal
        title="대화 전체보기"
        isVisible={isModalVisible}
        onClose={handleCancel}
      >
        <div className="chat-wrapper">
          {medicalChatMessages &&
            medicalChatMessages.map((chat, index) =>
              chat.sender === "Doctor" ? (
                <ArkDefault
                  key={index}
                  userName={chat.speaker}
                  time={chat.time}
                  avatarUrl="doctor"
                >
                  <ArkMessageBox type="medical">{chat.message}</ArkMessageBox>
                </ArkDefault>
              ) : (
                <UserMessage
                  key={index}
                  type="success"
                  sender="user"
                  userName={chat.speaker}
                  message={chat.message}
                  time={chat.time}
                />
              )
            )}
        </div>
      </ScrollModal>
    </div>
  );
};
