def byte_to_char_offset(text, byte_offset):
    """
    주어진 텍스트에서 바이트 오프셋을 문자 인덱스로 변환합니다.

    :param text: 원본 텍스트 (str)
    :param byte_offset: 바이트 오프셋 (int)
    :return: 문자 인덱스 (int)
    """
    cumulative_bytes = 0
    for idx, char in enumerate(text):
        char_bytes = char.encode('utf-8')
        cumulative_bytes += len(char_bytes)
        if cumulative_bytes > byte_offset:
            return idx
    return len(text)  # 바이트 오프셋이 텍스트 길이를 초과하는 경우

def verify_claim_position(text, start_byte, end_byte, claim_text):
    """
    주어진 바이트 오프셋이 텍스트 내에서 claim_text와 일치하는지 확인하고,
    문자 인덱스 범위를 반환합니다.
    """
    # 바이트 오프셋을 문자 인덱스로 변환
    char_start = byte_to_char_offset(text, start_byte)
    char_end = byte_to_char_offset(text, end_byte)

    # 검증할 범위 추출
    extracted_text = text[char_start:char_end]
    
    # 디버깅용 출력
    print(f"Extracted text: '{extracted_text}'")
    print(f"Expected text: '{claim_text}'")
    print(f"Character Index: start={char_start}, end={char_end}")
    
    # claim_text와 일치하는지 검증
    if extracted_text == claim_text:
        return char_start, char_end
    else:
        raise ValueError(
            f"Claim text does not match the text at the specified byte positions.\n"
            f"Expected: '{claim_text}'\n"
            f"Found: '{extracted_text}'"
        )



import urllib.parse

def insert_sources(answer_text, result_parse):
    source_list = result_parse["citedChunks"]
    offset = 0  # 위치 변화 추적 변수

    for claim in result_parse.get("claims", []):
        if claim.get("citationIndices"):
            source_text = ""
            sorted_indices = sorted(claim["citationIndices"])

            # URL 병합
            for index in sorted_indices:
                source_index = int(index) + 1
                source_url = source_list[int(index)]["reference_url_page"]

                # URL 파싱 및 경로 인코딩
                parsed_url = urllib.parse.urlparse(source_url)
                encoded_path = urllib.parse.quote(parsed_url.path)
                encoded_url = urllib.parse.urlunparse((
                    parsed_url.scheme,    # http or https
                    parsed_url.netloc,    # example.com
                    encoded_path,         # /path/to/resource
                    parsed_url.params,    # URL params
                    parsed_url.query,     # query 그대로
                    parsed_url.fragment   # fragment 그대로 유지
                ))

                url = f"[{source_index}]({encoded_url})"
                source_text += url + " "  # URL 사이에 공백 추가

            # 오프셋을 반영한 현재 위치 재계산
            adjusted_start = claim["startPos"] + offset
            adjusted_end = claim["endPos"] + offset

            # claim 위치 확인 및 텍스트 삽입
            try:
                _, end_pos = verify_claim_position(
                    answer_text, adjusted_start, adjusted_end, claim["claimText"]
                )
                # 링크 삽입
                answer_text = answer_text[:end_pos] + " " + source_text.strip() + answer_text[end_pos:]

                # 삽입된 텍스트 길이만큼 오프셋 업데이트
                offset += len(source_text.strip()) + 1  # 공백 포함 길이 추가
            except ValueError as e:
                print(f"Error verifying claim: {e}")
                continue  # 다음 claim으로 넘어감

    return answer_text
