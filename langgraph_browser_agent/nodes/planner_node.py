from typing import Dict, Any
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from ..state.agent_state import AgentState
from ..prompts.planner_prompts import get_planner_prompt_template # 프롬프트 템플릿 임포트

def planner_node(state: AgentState, llm: BaseChatModel) -> Dict[str, Any]:
    """
    LLM을 사용하여 계획을 수립하고 상태를 업데이트하는 노드.
    """
    print(">>> Planner Node 실행")

    messages = state.get("messages", [])
    task_description = state["task_description"]

    # 현재까지의 대화 내용과 작업 설명을 바탕으로 LLM에 전달할 입력 구성
    # 간단하게 마지막 메시지나 요약된 정보를 사용할 수도 있음
    # 여기서는 단순화를 위해 태스크 설명과 최근 메시지만 사용
    current_plan_str = "\n".join(state.get("plan", [])) if state.get("plan") else "아직 계획 없음"

    input_messages = [
        SystemMessage(content=get_planner_prompt_template()), # 시스템 프롬프트
        HumanMessage(content=f"""
        현재까지의 대화 요약:
        {messages[-1].content if messages else "없음"}

        원래 작업 지시: {task_description}

        현재까지의 계획:
        {current_plan_str}

        액션 이력 마지막 항목:
        {state.get("action_history")[-1] if state.get("action_history") else "없음"}

        검증 결과 (이전 스텝):
        {state.get("validation_result")}

        위 정보를 바탕으로 다음 계획을 JSON 형식으로 생성해주세요.
        만약 작업이 완료되었다고 판단되면 'done: true'로 설정하고, 'next_steps'에 최종 답변이나 요약을 포함해주세요.
        웹 작업이 더 이상 필요 없다면 'web_task: false'로 설정해주세요.
        """)
    ]

    print(f"  [Planner] LLM 입력 메시지: {input_messages}")

    ai_response = llm.invoke(input_messages)

    print(f"  [Planner] LLM 응답: {ai_response.content}")

    try:
        # LLM 응답이 JSON 문자열이라고 가정하고 파싱
        # 실제로는 BaseAgent의 extractJsonFromModelOutput 와 유사한 파싱/검증 로직 필요
        import json
        parsed_response = json.loads(ai_response.content)

        new_plan_steps = parsed_response.get("next_steps", "계획 없음")
        # next_steps가 문자열일 경우 리스트로 변환 (LLM 응답 형식에 따라 유연하게)
        if isinstance(new_plan_steps, str):
            new_plan_list = [step.strip() for step in new_plan_steps.split('\n') if step.strip()]
        elif isinstance(new_plan_steps, list):
            new_plan_list = new_plan_steps
        else:
            new_plan_list = []

        updated_state = {
            "plan": new_plan_list,
            "messages": messages + [ai_response], # LLM 응답을 메시지 이력에 추가
            "current_page_content": state.get("current_page_content"), # 이전 상태 유지
            "task_description": task_description # 이전 상태 유지
        }

        # 'done' 과 'web_task' 필드도 상태에 추가 (그래프의 조건부 엣지에서 사용 가능)
        if 'done' in parsed_response:
            updated_state['done'] = parsed_response['done']
        if 'web_task' in parsed_response:
            updated_state['web_task'] = parsed_response['web_task']
        if 'observation' in parsed_response: # 관찰 내용도 메시지 이력에 추가할 수 있음
            # 예: messages.append(AIMessage(content=f"관찰: {parsed_response['observation']}"))
            pass

        print(f"  [Planner] 새로운 계획: {updated_state['plan']}")
        if 'done' in updated_state: print(f"  [Planner] 작업 완료 여부: {updated_state['done']}")
        if 'web_task' in updated_state: print(f"  [Planner] 웹 작업 필요 여부: {updated_state['web_task']}")

        return updated_state

    except json.JSONDecodeError as e:
        print(f"  [Planner] LLM 응답 파싱 오류: {e}")
        print(f"  [Planner] 원본 응답: {ai_response.content}")
        return {
            "error_message": "Planner 응답 파싱 실패",
            "messages": messages + [ai_response] # 오류가 발생해도 LLM 응답은 기록
        }
    except Exception as e:
        print(f"  [Planner] 예외 발생: {e}")
        return {
            "error_message": f"Planner 실행 중 예외 발생: {str(e)}",
            "messages": messages + [ai_response]
        }
