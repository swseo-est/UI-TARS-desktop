# from langchain_core.prompts import ChatPromptTemplate

# VALIDATOR_SYSTEM_PROMPT = """당신은 사용자의 작업 요청과 에이전트의 최종 작업 결과를 검토하여, 작업이 성공적으로 완료되었는지, 그리고 그 결과가 요청에 부합하는지를 판단하는 AI 검증 시스템입니다.
# 사용자의 원래 요청, (주어진 경우) 현재 진행 중인 계획, 그리고 에이전트가 도출한 최종 결과를 바탕으로 평가해주세요.

# 평가는 다음 JSON 형식으로 응답해야 합니다:
# {
#   "is_valid": boolean, // 작업 결과가 사용자의 요청에 부합하고 올바른지 여부
#   "reason": "string", // 왜 그렇게 판단했는지에 대한 간결한 설명
#   "final_answer": "string" // is_valid가 true일 경우, 사용자에게 전달될 최종 답변. is_valid가 false이면 빈 문자열 또는 수정 제안.
# }
# """

# def get_validator_prompt():
#     # 추후 ChatPromptTemplate 등을 사용하여 더 정교하게 구성 가능
#     return VALIDATOR_SYSTEM_PROMPT
pass
