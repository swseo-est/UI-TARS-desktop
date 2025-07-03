from typing import Dict, Any
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from ..state.agent_state import AgentState
from ..prompts.navigator_prompts import get_navigator_prompt_template # 프롬프트 템플릿 임포트

def navigator_node(state: AgentState, llm: BaseChatModel) -> Dict[str, Any]:
    """
    LLM을 사용하여 다음 브라우저 액션을 결정하고 상태를 업데이트하는 노드.
    """
    print(">>> Navigator Node 실행")

    messages = state.get("messages", [])
    task_description = state["task_description"]
    current_plan = state.get("plan", ["계획 없음"])
    current_url = state.get("current_url", "알 수 없음")
    current_page_content = state.get("current_page_content", "현재 페이지 내용 없음")
    action_history = state.get("action_history", [])

    # LLM에 전달할 입력 구성
    # 현재 계획, 페이지 내용, 이전 액션 이력 등을 포함
    plan_str = "\n".join(current_plan)
    history_str = "\n".join([f"- {item['action']}: {item.get('result', '결과 없음')}" for item in action_history[-3:]]) # 최근 3개 이력

    input_content = f"""
    원래 작업 지시: {task_description}
    현재 URL: {current_url}
    현재 페이지 내용 요약: {current_page_content}
    현재까지의 계획:
    {plan_str}
    최근 액션 이력:
    {history_str if history_str else "없음"}

    위 정보를 바탕으로, 현재 계획 단계를 수행하기 위한 다음 브라우저 액션을 JSON 형식으로 결정해주세요.
    사용 가능한 액션 타입은 "navigate_url", "type_text", "click", "extract_text", "finish" 입니다.
    만약 작업을 완료할 수 있다면 "finish" 액션과 함께 최종 답변을 제공해주세요.
    """

    input_messages = [
        SystemMessage(content=get_navigator_prompt_template()), # 시스템 프롬프트
        HumanMessage(content=input_content)
    ]

    print(f"  [Navigator] LLM 입력 메시지: {input_messages}")

    ai_response = llm.invoke(input_messages)

    print(f"  [Navigator] LLM 응답: {ai_response.content}")

    try:
        # LLM 응답이 JSON 문자열이라고 가정하고 파싱
        import json
        # BaseAgent의 extractJsonFromModelOutput 와 유사한 로직이 필요할 수 있음 (예: ```json ... ``` 제거)
        action_content = ai_response.content
        if action_content.startswith("```json"):
            action_content = action_content.split("```json\n", 1)[1].rsplit("\n```", 1)[0]
        elif action_content.startswith("```"):
             action_content = action_content.split("```\n", 1)[1].rsplit("\n```", 1)[0]

        parsed_action = json.loads(action_content)

        # 액션 유효성 검사 (간단하게)
        if "action_type" not in parsed_action:
            raise ValueError("LLM 응답에 'action_type' 필드가 없습니다.")

        print(f"  [Navigator] 결정된 액션: {parsed_action}")

        return {
            "next_action": parsed_action,
            "messages": messages + [ai_response] # LLM 응답을 메시지 이력에 추가
        }

    except json.JSONDecodeError as e:
        print(f"  [Navigator] LLM 응답 파싱 오류: {e}")
        print(f"  [Navigator] 원본 응답: {ai_response.content}")
        return {
            "error_message": "Navigator 응답 파싱 실패",
            "messages": messages + [ai_response]
        }
    except ValueError as e:
        print(f"  [Navigator] LLM 응답 유효성 오류: {e}")
        print(f"  [Navigator] 원본 응답: {ai_response.content}")
        return {
            "error_message": f"Navigator 응답 유효성 오류: {str(e)}",
            "messages": messages + [ai_response]
        }
    except Exception as e:
        print(f"  [Navigator] 예외 발생: {e}")
        return {
            "error_message": f"Navigator 실행 중 예외 발생: {str(e)}",
            "messages": messages + [ai_response]
        }
