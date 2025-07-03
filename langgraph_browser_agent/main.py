from dotenv import load_dotenv

# .env 파일로부터 환경 변수 로드 (예: API 키)
# 실행 전에 .env 파일에 OPENAI_API_KEY="your_key_here" 와 같이 설정 필요
load_dotenv()

def run_agent():
    """
    에이전트 실행을 위한 메인 함수 (추후 구현)
    """
    print("LangGraph Browser Agent - 실행 시작 (구현 예정)")

    # TODO: 1. 상태(State) 객체 초기화
    # TODO: 2. LangGraph 워크플로우 컴파일
    # TODO: 3. 초기 작업 입력 설정
    # TODO: 4. 워크플로우 실행 및 결과 스트리밍/출력

    # 예시 작업
    initial_task = "오늘 서울의 날씨를 찾아서 알려줘."
    print(f"초기 작업: {initial_task}")

    print("LangGraph Browser Agent - 실행 종료 (구현 예정)")

if __name__ == "__main__":
    run_agent()
