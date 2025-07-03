from typing import Dict, Any, List

from ..state.agent_state import AgentState
from ..utils.browser_tools_mock import execute_browser_action # 임시 목업 도구

def action_executor_node(state: AgentState) -> Dict[str, Any]:
    """
    Navigator가 결정한 액션을 실제 브라우저 제어 도구를 통해 실행하고
    그 결과를 상태에 반영하는 노드.
    """
    print(">>> Action Executor Node 실행")

    action_to_perform = state.get("next_action")
    action_history: List[Dict[str, Any]] = state.get("action_history", [])
    current_url = state.get("current_url")
    current_page_content = state.get("current_page_content")

    if not action_to_perform:
        print("  [ActionExecutor] 수행할 액션이 없습니다.")
        return {
            "action_history": action_history + [{"action": None, "result": "수행할 액션 없음 (오류 가능성)"}],
            "error_message": "수행할 액션이 정의되지 않았습니다."
        }

    print(f"  [ActionExecutor] 수행할 액션: {action_to_perform}")

    # 사용자 제공 실제 브라우저 도구 호출 부분 (현재는 목업)
    # 실제 도구는 action_to_perform 딕셔너리를 해석하여 Playwright 등으로 브라우저 조작
    # 결과는 딕셔너리 형태로, 최소한 status ("success" 또는 "error") 를 포함해야 함
    # 추가로 current_url, page_summary, extracted_text, final_answer 등을 포함할 수 있음
    execution_result = execute_browser_action(action_to_perform)

    print(f"  [ActionExecutor] 액션 실행 결과: {execution_result}")

    # 액션 이력 업데이트
    updated_action_history = action_history + [{
        "action": action_to_perform,
        "result_status": execution_result.get("status"),
        "output": execution_result # 도구의 전체 반환 값 저장
    }]

    # 상태 업데이트 준비
    updated_fields: Dict[str, Any] = {
        "action_history": updated_action_history,
        "next_action": None, # 수행했으므로 다음 액션은 초기화
    }

    if execution_result.get("status") == "success":
        if "current_url" in execution_result:
            updated_fields["current_url"] = execution_result["current_url"]
        if "page_summary" in execution_result: # 목업 도구에서 page_summary를 제공한다고 가정
            updated_fields["current_page_content"] = execution_result["page_summary"]
        if "extracted_text" in execution_result:
            # 추출된 텍스트를 다음 LLM 호출을 위해 메시지 이력에 추가할 수 있음
            # 또는 특정 필드에 저장. 여기서는 간단히 출력만.
            print(f"  [ActionExecutor] 추출된 텍스트: {execution_result['extracted_text']}")
            # 예시: updated_fields["last_extracted_text"] = execution_result['extracted_text']
        if "final_answer" in execution_result: # 'finish' 액션의 경우
            updated_fields["final_answer"] = execution_result["final_answer"]
            updated_fields["done"] = True # 작업 완료 상태로 설정
    else:
        updated_fields["error_message"] = execution_result.get("message", "액션 실행 실패")
        # 실패 시 재시도를 위해 retry_count 등을 업데이트할 수 있음
        # updated_fields["retry_count"] = state.get("retry_count", 0) + 1

    return updated_fields
