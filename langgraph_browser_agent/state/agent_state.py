from typing import TypedDict, List, Optional, Dict, Any
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    LangGraph 에이전트의 전체 실행 상태를 나타내는 객체입니다.
    워크플로우의 모든 노드 간에 이 상태 객체가 전달되고 업데이트됩니다.
    """
    # 초기 입력 및 작업 정의
    task_description: str

    # 대화 이력 (LLM과의 상호작용 기록)
    messages: List[BaseMessage]

    # 브라우저 및 페이지 상태 관련
    current_url: Optional[str]
    current_page_content: Optional[str] # 페이지의 텍스트 요약 또는 구조화된 DOM 정보

    # Planner 노드 관련
    plan: Optional[List[str]] # Planner가 생성한 작업 단계 목록

    # Navigator 및 Action Executor 노드 관련
    # Navigator가 결정한 다음 액션 (예: {"action_type": "click", "selector": "#button"})
    next_action: Optional[Dict[str, Any]]
    # Action Executor가 수행한 액션과 그 결과 기록
    # 각 항목 예시: {"action": next_action, "result": "성공", "output": "클릭 완료"}
    action_history: List[Dict[str, Any]]

    # Validator 노드 관련
    # 예: {"is_valid": True, "reason": "정보가 정확함", "final_answer": "서울 날씨는 맑음"}
    validation_result: Optional[Dict[str, Any]]

    # 최종 결과
    final_answer: Optional[str]

    # 오류 및 재시도 관리
    error_message: Optional[str]
    retry_count: int
    max_retries: int

# AgentState를 초기화하는 헬퍼 함수 (선택 사항이지만 유용할 수 있음)
def get_initial_state(task_description: str, max_retries: int = 3) -> AgentState:
    return AgentState(
        task_description=task_description,
        messages=[],
        current_url=None,
        current_page_content=None,
        plan=None,
        next_action=None,
        action_history=[],
        validation_result=None,
        final_answer=None,
        error_message=None,
        retry_count=0,
        max_retries=max_retries,
    )
