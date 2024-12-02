import { UserOutlined } from "@ant-design/icons";
import { Avatar } from "antd";
import ArkSvg from "@/assets/avatars/ark-base.svg";
import MedicalIcon from "@/assets/avatars/ARK AI Agent for medical.webp";
import DoctorIcon from "@/assets/avatars/doctor.png";
const sizes = {
  sm: 35,
  md: 40,
  lg: 45,
  xl: 96,
};

const avatars = {
  ark: ArkSvg,
  doctor: DoctorIcon,
  ark_medical: MedicalIcon,
};

const variants = {
  "chat-ark": {
    size: "lg" as keyof typeof sizes,
    shape: "square",
    backgroundColor: "#cce7ff",
  },
  "chat-user": {
    size: "lg" as keyof typeof sizes,
    shape: "square",
    backgroundColor: "#e0e0e0",
  },
  user: {
    size: "md" as keyof typeof sizes,
    shape: "circle",
    backgroundColor: "#e0e0e0",
  },
} as const;
export type AvatarProps = {
  size?: keyof typeof sizes;
  variant?: keyof typeof variants;
  shape?: "circle" | "square";
  icon?: string | React.ReactNode;
  avatar?: keyof typeof avatars | string;
  backgroundColor?: string;
  className?: string;
  onClick?: () => void;
};

export const AvatarCustom = ({
  variant,
  size,
  shape,
  icon,
  avatar,
  backgroundColor,
  className = "",
  onClick,
}: AvatarProps) => {
  const defaultStyle = {
    size: "lg" as keyof typeof sizes,
    shape: "square" as const,
    icon: <UserOutlined />,
    avatar: "ark",
    backgroundColor: "#d9d9d9",
  };

  // variant가 있는 경우 variant 스타일을 덮어씌움
  const variantStyles = variant
    ? { ...defaultStyle, ...variants[variant] }
    : defaultStyle;

  const finalSize = sizes[size || variantStyles.size];
  const finalShape = shape || variantStyles.shape;
  const finalIcon = avatar ? undefined : icon || variantStyles.icon;
  const finalAvatar =
    avatar && avatars[avatar as keyof typeof avatars]
      ? avatars[avatar as keyof typeof avatars]
      : avatar || variantStyles.avatar;
  const finalBackgroundColor = backgroundColor || variantStyles.backgroundColor;

  const additionalStyles =
    variant === "chat-ark" || variant === "chat-user"
      ? { marginTop: "10px" }
      : {};

  return (
    <div className={`avatar-custom ${className}`} style={additionalStyles}>
      <Avatar
        shape={finalShape}
        size={finalSize}
        src={finalAvatar}
        icon={finalIcon}
        style={{ backgroundColor: finalBackgroundColor }}
        onClick={onClick}
      />
    </div>
  );
};
