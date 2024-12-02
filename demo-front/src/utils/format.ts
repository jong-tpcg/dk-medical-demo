export const formatTime = (time: string): string => {
  // "오전"/"오후"가 포함된 경우 처리
  if (time.includes("오전") || time.includes("오후")) {
    const isAfternoon = time.startsWith("오후");
    const timePart = time.replace("오전 ", "").replace("오후 ", "");
    const [hoursStr, minutesStr, secondsStr] = timePart.split(":");

    let hours = Number(hoursStr);

    // 오후이고 12시가 아닌 경우 12시간 더함
    if (isAfternoon && hours !== 12) {
      hours += 12;
    }

    // 오전 12시는 0으로 변환
    if (!isAfternoon && hours === 12) {
      hours = 0;
    }

    // 12시간제 변환
    const formattedHours = hours % 12 || 12;
    const formattedMinutes = String(minutesStr).padStart(2, "0");
    const formattedSeconds = String(secondsStr || "0").padStart(2, "0");
    const period = isAfternoon ? "PM" : "AM";

    return `${formattedHours}:${formattedMinutes}:${formattedSeconds} ${period}`;
  }

  // "HH:MM:SS.sss" 형태 처리
  if (/^\d{2}:\d{2}:\d{2}(\.\d+)?$/.test(time)) {
    const [hoursStr, minutesStr, secondsStr] = time.split(":");
    const hours = Number(hoursStr);
    const minutes = Number(minutesStr);
    const seconds = Math.floor(Number(secondsStr)); // 소수점 이하 반올림

    const period = hours < 12 ? "AM" : "PM";
    const formattedHours = (hours % 12 || 12).toString();
    const formattedMinutes = String(minutes).padStart(2, "0");
    const formattedSeconds = String(seconds).padStart(2, "0");

    return `${formattedHours}:${formattedMinutes}:${formattedSeconds} ${period}`;
  }

  throw new Error("Invalid time format");
};

//00:00:50.070 -> 00:00:50 AM
export const formatTimecode = (timecode: string): string => {
  // 콜론으로 시간, 분, 초 구분
  const [hoursStr, minutesStr, secondsStr] = timecode.split(":");

  // 시간과 분 변환
  const hours = Number(hoursStr);
  const minutes = Number(minutesStr);

  // 초가 소수점 포함된 경우 반올림
  const seconds = secondsStr ? Math.round(Number(secondsStr)) : 0;

  // AM/PM 계산
  const period = hours < 12 ? "AM" : "PM";

  // 12시간제로 변환 (0시는 12로 표시)
  const formattedHours = hours % 12 || 12;
  const formattedMinutes = String(minutes).padStart(2, "0");
  const formattedSeconds = String(seconds).padStart(2, "0");

  return `${formattedHours}:${formattedMinutes}:${formattedSeconds} ${period}`;
};

// 오후 9:30:00 -> 9:30:00 PM
export const formatDefaultTime = (timecode: string): string => {
  // "오전" 또는 "오후"로 시작하는지 확인
  const isAfternoon = timecode.startsWith("오후");
  const isMorning = timecode.startsWith("오전");

  // "오전"/"오후"를 제거하고 시간, 분, 초 분리
  const timePart = timecode.replace("오전 ", "").replace("오후 ", "");
  const [hoursStr, minutesStr, secondsStr] = timePart.split(":");

  // 시간 변환
  let hours = Number(hoursStr);

  // 오후일 경우 PM 처리
  const period = isAfternoon ? "PM" : "AM";

  // 오후이면서 12시가 아닐 경우 12시간 더함
  if (isAfternoon && hours !== 12) {
    hours += 12;
  }

  // 오전 12시는 0시로 변환
  if (isMorning && hours === 12) {
    hours = 0;
  }

  // 시간, 분, 초 포맷팅
  const formattedHours = hours % 12 || 12; // 12시간제로 변환
  const formattedMinutes = String(minutesStr).padStart(2, "0");
  const formattedSeconds = String(secondsStr).padStart(2, "0");
  return `${formattedHours}:${formattedMinutes}:${formattedSeconds} ${period}`;
};
