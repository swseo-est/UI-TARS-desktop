import json

# 임시 목업 데이터 저장소
mock_page_content = {
    "https://www.google.com": "Google 검색 페이지입니다. '오늘 날씨'를 검색할 수 있습니다.",
    "https://www.weather.com/seoul": "서울의 현재 날씨는 맑음, 25도입니다.",
}
current_mock_url = "https://www.google.com"

def execute_browser_action(action: dict):
    """
    브라우저 액션을 흉내 내는 목업 함수.
    사용자님이 실제 Playwright 도구를 제공하면 이 함수는 교체될 것입니다.
    """
    global current_mock_url
    action_type = action.get("action_type")
    print(f" [목업 브라우저] 액션 실행 시도: {action}")

    if action_type == "navigate_url":
        url = action.get("url")
        if url:
            current_mock_url = url
            page_summary = mock_page_content.get(url, f"{url} 페이지의 내용을 찾을 수 없습니다.")
            print(f" [목업 브라우저] {url}로 이동했습니다. 페이지 요약: {page_summary}")
            return {"status": "success", "current_url": url, "page_summary": page_summary}
        else:
            return {"status": "error", "message": "URL이 제공되지 않았습니다."}

    elif action_type == "type_text":
        selector = action.get("selector")
        text = action.get("text")
        print(f" [목업 브라우저] 요소 '{selector}'에 '{text}' 입력 시도 (목업에서는 실제 동작 없음)")
        # 실제로는 검색 결과 페이지 등으로 URL이 변경될 수 있음을 시뮬레이션
        if "google.com" in current_mock_url and "날씨" in text:
            # 검색 결과 페이지로 이동했다고 가정
            new_url = f"https://www.google.com/search?q={text.replace(' ', '+')}"
            page_summary = f"'{text}' 검색 결과입니다. 첫 번째 결과는 weather.com 일 수 있습니다."
            # current_mock_url = new_url # 실제로는 URL 변경이 발생할 수 있음
            print(f" [목업 브라우저] '{text}' 입력 후, 검색 결과 페이지로 이동했을 수 있습니다.")
            return {"status": "success", "message": f"'{selector}'에 '{text}' 입력 완료.", "current_url": current_mock_url, "page_summary": page_summary}
        return {"status": "success", "message": f"'{selector}'에 '{text}' 입력 완료.", "current_url": current_mock_url}

    elif action_type == "click":
        selector = action.get("selector")
        print(f" [목업 브라우저] 요소 '{selector}' 클릭 시도 (목업에서는 실제 동작 없음)")
        # 예시: 특정 버튼 클릭 시 날씨 페이지로 이동한다고 가정
        if "google.com" in current_mock_url and "search_button" in selector: # 가상의 선택자
            if "날씨" in mock_page_content.get(current_mock_url, "") : # 이전 type_text 결과에 따라
                 new_url = "https://www.weather.com/seoul" # 날씨 검색 결과 페이지로 이동했다고 가정
                 current_mock_url = new_url
                 page_summary = mock_page_content.get(new_url, "")
                 print(f" [목업 브라우저] 검색 버튼 클릭 후, {new_url}로 이동했습니다.")
                 return {"status": "success", "current_url": new_url, "page_summary": page_summary}
        return {"status": "success", "message": f"'{selector}' 클릭 완료.", "current_url": current_mock_url}

    elif action_type == "extract_text":
        selector = action.get("selector")
        # 현재 URL의 내용에서 텍스트 추출 시도 (목업)
        content_summary = mock_page_content.get(current_mock_url, "")
        extracted_text = ""
        if "weather.com" in current_mock_url and ("weather_result" in selector or "temperature" in selector): # 가상의 선택자
            if "맑음, 25도" in content_summary:
                 extracted_text = "맑음, 25도" # 실제로는 더 구체적인 내용 추출
        elif "google.com" in current_mock_url and "search_result_summary" in selector:
            extracted_text = "검색 결과 요약입니다. (목업)"
        else:
            extracted_text = f"'{selector}'에서 텍스트 추출 (목업): 현재 페이지 내용의 일부 - '{content_summary[:50]}...'"

        print(f" [목업 브라우저] 요소 '{selector}'에서 텍스트 추출: {extracted_text}")
        return {"status": "success", "extracted_text": extracted_text, "current_url": current_mock_url}

    elif action_type == "finish":
        final_answer = action.get("final_answer")
        print(f" [목업 브라우저] 작업 완료. 최종 답변: {final_answer}")
        return {"status": "success", "message": "작업 완료됨.", "final_answer": final_answer}

    else:
        print(f" [목업 브라우저] 알 수 없는 액션 타입: {action_type}")
        return {"status": "error", "message": f"알 수 없는 액션 타입: {action_type}"}

if __name__ == '__main__':
    # 간단한 테스트
    print(execute_browser_action({"action_type": "navigate_url", "url": "https://www.google.com"}))
    print(execute_browser_action({"action_type": "type_text", "selector": "input[name='q']", "text": "오늘 서울 날씨"}))
    # 실제로는 위 type_text 후 LLM이 검색 버튼 클릭을 지시할 것임
    print(execute_browser_action({"action_type": "click", "selector": "button#search_button"})) # 가상
    print(execute_browser_action({"action_type": "extract_text", "selector": "div#weather_result"})) # 가상
    print(execute_browser_action({"action_type": "finish", "final_answer": "오늘 서울의 날씨는 맑음, 25도입니다."}))
