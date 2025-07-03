from typing import Dict, Any
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from ..state.agent_state import AgentState
from ..prompts.validator_prompts import get_validator_prompt_template # 프롬프트 템플릿 임포트

def validator_node(state: AgentState, llm: BaseChatModel) -> Dict[str, Any]:
    """
    LLM을 사용하여 작업 결과의 유효성을 검증하고 상태를 업데이트하는 노드.
    """
    print(">>> Validator Node 실행")

    messages = state.get("messages", [])
    task_description = state["task_description"]
    current_plan_str = "\n".join(state.get("plan", [])) if state.get("plan") else "계획 없음"
    action_history = state.get("action_history", [])

    # 검증을 위해 LLM에 전달할 정보 구성
    # 작업 설명, 최종 액션 결과, 계획 등을 포함할 수 있음
    last_action_output = action_history[-1].get("output") if action_history else {"message": "액션 이력 없음"}

    input_content = f"""
    원래 작업 지시: {task_description}
    현재까지의 계획:
    {current_plan_str}
    마지막으로 수행된 액션의 결과:
    {last_action_output}

    위 정보를 바탕으로, 에이전트가 원래 작업 지시를 성공적으로 완료했는지,
    그리고 그 결과가 요청에 부합하는지를 판단해주세요.
    판단 결과는 JSON 형식으로 제공되어야 하며, 'is_valid', 'reason', 'final_answer' 필드를 포함해야 합니다.
    'is_valid'가 true이면, 'final_answer'에 사용자에게 전달될 최종 답변을 포함해주세요.
    'is_valid'가 false이면, 'final_answer'는 비워두거나 수정/재시도 방향을 제시할 수 있습니다.
    """

    input_messages = [
        SystemMessage(content=get_validator_prompt_template()), # 시스템 프롬프트
        HumanMessage(content=input_content)
    ]

    print(f"  [Validator] LLM 입력 메시지: {input_messages}")

    ai_response = llm.invoke(input_messages)

    print(f"  [Validator] LLM 응답: {ai_response.content}")

    try:
        import json
        # BaseAgent의 extractJsonFromModelOutput 와 유사한 로직이 필요할 수 있음
        validation_content = ai_response.content
        if validation_content.startswith("```json"):
            validation_content = validation_content.split("```json\n", 1)[1].rsplit("\n```", 1)[0]
        elif validation_content.startswith("```"):
            validation_content = validation_content.split("```\n", 1)[1].rsplit("\n```", 1)[0]

        parsed_validation = json.loads(validation_content)

        if "is_valid" not in parsed_validation or "reason" not in parsed_validation or "final_answer" not in parsed_validation:
            raise ValueError("Validator 응답에 필수 필드(is_valid, reason, final_answer)가 누락되었습니다.")

        print(f"  [Validator] 검증 결과: {parsed_validation}")

        updated_fields: Dict[str, Any] = {
            "validation_result": parsed_validation,
            "messages": messages + [ai_response] # LLM 응답을 메시지 이력에 추가
        }

        if parsed_validation.get("is_valid"):
            updated_fields["final_answer"] = parsed_validation.get("final_answer")
            updated_fields["done"] = True # 최종적으로 작업 완료 처리
        else:
            # 검증 실패 시, 다음 계획 수립에 참고할 수 있도록 메시지 추가 또는 특정 상태 업데이트
            # 예: messages.append(HumanMessage(content=f"검증 실패: {parsed_validation.get('reason')}"))
            # 또는 error_message 필드 업데이트
            updated_fields["error_message"] = f"검증 실패: {parsed_validation.get('reason')}"
            updated_fields["done"] = False # 작업 미완료

        return updated_fields

    except json.JSONDecodeError as e:
        print(f"  [Validator] LLM 응답 파싱 오류: {e}")
        print(f"  [Validator] 원본 응답: {ai_response.content}")
        return {
            "error_message": "Validator 응답 파싱 실패",
            "messages": messages + [ai_response],
            "done": False
        }
    except ValueError as e:
        print(f"  [Validator] LLM 응답 유효성 오류: {e}")
        print(f"  [Validator] 원본 응답: {ai_response.content}")
        return {
            "error_message": f"Validator 응답 유효성 오류: {str(e)}",
            "messages": messages + [ai_response],
            "done": False
        }
    except Exception as e:
        print(f"  [Validator] 예외 발생: {e}")
        return {
            "error_message": f"Validator 실행 중 예외 발생: {str(e)}",
            "messages": messages + [ai_response],
            "done": False
        }
