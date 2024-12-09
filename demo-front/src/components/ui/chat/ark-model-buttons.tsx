import { Button } from "antd";
import { useState } from "react";
import { Spinner } from "../spinner/Spinner";

type ModelListType = {
  label: string;
  type: string;
};
type ArkModelButtonType = {
  model_list?: ModelListType[];
  current_model?: ModelListType["type"];
  disabled?: boolean;
  title?: string;
  align?: string;
  isLoading?: boolean;
  hideLoading?: boolean;
  onSwitchModel?: (model: string) => void;
};
export const ArkModelButtons = ({
  model_list = [
    { label: "Gem 1.5 Flash", type: "gemini" },
    { label: "Claude", type: "claude" },
  ],
  current_model,
  title,
  disabled = false,
  isLoading = false,
  hideLoading = false,
  align = "left",
  onSwitchModel,
}: ArkModelButtonType) => {
  const [selectedModel, setSelectedModel] = useState<string>(
    current_model || model_list[0]?.type || ""
  );
  const changeModelClick = (type: string) => {
    setSelectedModel(type);
    if (onSwitchModel) {
      onSwitchModel(type);
    }
  };
  return (
    <div className="button-wrapper ">
      {title && <h3>{title}</h3>}
      <div className={`button-group ${align}`}>
        {model_list.map((model) => (
          <div key={model.type} className="button-loading">
            <Button
              disabled={disabled || isLoading}
              className={`custom-button ${
                selectedModel === model.type ? "" : "none_active"
              } ${isLoading && selectedModel === model.type ? "loading" : ""}`}
              type="primary"
              shape="round"
              size="middle"
              onClick={() => changeModelClick(model.type)}
            >
              {model.label}
            </Button>
            {hideLoading && isLoading && selectedModel === model.type && (
              <Spinner key={model.type} type="llm" />
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
