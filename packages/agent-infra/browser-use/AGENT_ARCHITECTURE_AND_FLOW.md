# `@agent-infra/browser-use` 내부 에이전트 아키텍처 및 작업 흐름 분석

이 문서는 `packages/agent-infra/browser-use/src/agent/` 디렉토리 내의 에이전트 시스템 아키텍처, 각 에이전트의 역할, 에이전트 간 협력 방식 및 전체적인 작업 처리 흐름에 대한 상세 분석을 제공합니다.

## 1. 주요 컴포넌트

에이전트 시스템은 다음과 같은 주요 컴포넌트로 구성됩니다:

*   **`Executor` (`executor.ts`)**: 전체 작업 흐름의 중앙 오케스트레이터입니다. 사용자로부터 태스크를 받아 Planner, Navigator, Validator 에이전트를 조율하고, 작업 루프를 관리합니다.
*   **`AgentContext` (`types.ts`, `executor.ts`에서 주로 생성 및 사용)**: 모든 에이전트가 공유하는 실행 컨텍스트입니다. 다음을 포함합니다:
    *   `taskId`: 현재 작업의 고유 ID.
    *   `browserContext`: 브라우저와 상호작용하기 위한 `BrowserContext` 인스턴스 (`../browser/context.ts`).
    *   `messageManager`: 대화 이력(메모리)을 관리하는 `MessageManager` 인스턴스 (`messages/service.ts`).
    *   `eventManager`: 에이전트 실행 중 발생하는 이벤트를 관리하고 외부로 전달하는 `EventManager` 인스턴스 (`event/manager.ts`).
    *   `options`: 에이전트 실행 관련 옵션 (예: `maxSteps`, `planningInterval`, `useVision`).
    *   `actionResults`: `NavigatorAgent`가 수행한 액션의 결과(`ActionResult`) 목록.
    *   기타 상태 정보: `nSteps` (현재 스텝 수), `consecutiveFailures` (연속 실패 횟수), `stopped`, `paused` 플래그 등.
*   **`BaseAgent` (`agents/base.ts`)**: 모든 특정 에이전트(Planner, Navigator, Validator)의 부모 추상 클래스입니다. LLM과의 공통 상호작용 로직 (프롬프트 기반 호출, 응답 파싱 및 검증, 대화 이력 추가 등)을 제공합니다.
*   **`PlannerAgent` (`agents/planner.ts`)**: `BaseAgent`를 상속하며, 고수준의 계획을 수립합니다. 현재 대화 이력과 상태를 바탕으로 LLM을 호출하여 다음 행동 계획, 관찰, 작업 완료 여부 등을 결정합니다.
*   **`NavigatorAgent` (`agents/navigator.ts`)**: `BaseAgent`를 상속하며, `PlannerAgent`의 계획이나 현재 상태를 바탕으로 실제 웹 브라우저에서 구체적인 액션을 수행합니다. LLM을 호출하여 수행할 액션(들)을 결정하고, `NavigatorActionRegistry`를 통해 해당 액션을 실행합니다.
*   **`ValidatorAgent` (`agents/validator.ts`)**: `BaseAgent`를 상속하며, 작업 수행 결과가 사용자의 초기 목표나 주어진 계획에 부합하는지 LLM을 통해 검증합니다.
*   **Prompts (`prompts/`)**: 각 에이전트(Planner, Navigator, Validator)가 LLM과 상호작용할 때 사용하는 프롬프트 템플릿 및 생성 로직을 포함합니다. (예: `PlannerPrompt`, `NavigatorPrompt`, `ValidatorPrompt`)
*   **Actions (`actions/`)**: `NavigatorAgent`가 수행할 수 있는 구체적인 브라우저 조작 행위들입니다. `ActionBuilder`를 통해 생성되고 `NavigatorActionRegistry`에 등록되어 관리됩니다. 각 액션은 `Page` 객체(`../../browser/page.ts`)의 메서드를 사용하여 브라우저를 제어합니다.

## 2. 에이전트 아키텍처

이 시스템은 단일 에이전트가 모든 것을 처리하는 방식이 아니라, **역할 기반으로 전문화된 여러 에이전트 컴포넌트들이 `Executor`라는 중앙 오케스트레이터에 의해 조율되는 계층적 또는 파이프라인 형태의 아키텍처**를 가지고 있습니다.

*   **중앙 오케스트레이션**: `Executor`가 전체 작업의 생명주기를 관리하며, 각 단계에서 필요한 에이전트를 호출하고 결과를 다음 에이전트나 로직으로 전달합니다.
*   **정보 공유 허브 (`AgentContext`)**: 모든 에이전트는 동일한 `AgentContext` 인스턴스를 공유합니다. 이를 통해 대화 이력, 현재 브라우저 상태, 이전 액션 결과, 실행 옵션 등 작업 수행에 필요한 모든 정보를 일관되게 접근하고 업데이트할 수 있습니다. 이것이 에이전트 간 협력의 핵심 메커니즘입니다.
*   **LLM 활용의 역할 분담**:
    *   `PlannerAgent`의 LLM: 전략적 계획 수립, 목표 분해, 다음 단계의 고수준 방향 설정.
    *   `NavigatorAgent`의 LLM: 현재 구체적인 브라우저 상태와 단기 목표(또는 Planner의 지시)를 바탕으로, 실행 가능한 가장 적절한 브라우저 액션(도구 사용)을 결정.
    *   `ValidatorAgent`의 LLM: 최종 결과 또는 중간 결과물의 정합성, 완전성, 목표 부합 여부 판단.
*   **모듈성 및 확장성**: 각 에이전트와 액션이 분리되어 있어 새로운 에이전트 유형이나 액션을 추가하기 용이한 구조입니다.

## 3. 전체 작업 흐름 (Flow)

다음은 `Executor.execute()` 메서드를 중심으로 한 일반적인 작업 흐름입니다:

1.  **초기화 단계**:
    *   사용자가 `Agent` 서비스(`../service.ts`)의 `run(task)`를 호출하면, `Executor` 인스턴스가 생성됩니다.
    *   `Executor` 생성자 내에서 `AgentContext`, `MessageManager`, `EventManager` 및 각 전문 에이전트(Planner, Navigator, Validator)와 해당 프롬프트가 초기화됩니다.
    *   `NavigatorAgent`를 위한 액션들이 `ActionBuilder`에 의해 생성되어 `NavigatorActionRegistry`에 등록됩니다.
    *   초기 시스템 메시지와 사용자의 첫 번째 태스크가 `MessageManager`에 추가됩니다.

2.  **실행 루프 시작 (`Executor.execute`)**:
    *   "TASK_START" 이벤트가 발생합니다.
    *   미리 설정된 최대 스텝 수(`options.maxSteps`)까지 메인 루프가 반복됩니다.
    *   매 스텝 시작 시, 작업 중단(`stopped`), 일시정지(`paused`), 또는 최대 연속 실패 횟수(`maxFailures`) 도달 여부를 `shouldStop()`을 통해 확인합니다.

3.  **계획 단계 (조건부 실행 - `PlannerAgent`)**:
    *   다음 조건 중 하나라도 만족하면 `planner.execute()`가 호출됩니다:
        *   현재 스텝(`context.nSteps`)이 설정된 계획 주기(`options.planningInterval`)에 도달했을 때.
        *   이전 스텝에서 `ValidatorAgent`의 검증이 실패했을 때 (`validatorFailed = true`).
    *   `PlannerAgent`는 현재 `AgentContext`의 메시지 이력 (및 옵션에 따라 브라우저 상태)을 바탕으로 LLM을 호출합니다.
    *   LLM은 다음 계획(`next_steps`), 현재 상황에 대한 관찰(`observation`), 작업 완료 여부(`done`), 현재 작업이 웹과 관련된 작업인지(`web_task`) 등을 포함하는 `PlannerOutput` 형식의 응답을 반환합니다.
    *   이 계획 결과는 `MessageManager`에 추가 기록되며, `ValidatorAgent`의 `setPlan()`을 통해 현재 진행 중인 계획으로 설정됩니다.
    *   만약 Planner가 `done: true`를 반환하고 동시에 `web_task: false` (웹 작업이 아님)를 반환하면, 더 이상 브라우저 조작이 필요 없다고 판단하여 메인 루프를 종료할 수 있습니다.

4.  **액션 수행 단계 (`NavigatorAgent`)**:
    *   만약 Planner가 작업을 완료했다고 판단하지 않았다면 (`done` 플래그가 `false`), `Executor`는 내부적으로 `navigate()` 메서드를 호출하고, 이 메서드 내에서 `navigator.execute()`가 호출됩니다.
    *   `NavigatorAgent.execute()` 내부에서는:
        *   `addStateMessageToMemory()`: 현재 브라우저의 상세 상태(DOM 구조, 스크린샷 등)를 `AgentContext`를 통해 가져와 `MessageManager`에 추가합니다. 이는 LLM이 현재 상황을 정확히 인지하도록 하기 위함입니다.
        *   LLM 호출 (`invoke`): `NavigatorAgent`는 현재까지의 전체 대화 이력(사용자 요청, 이전 액션 결과, Planner의 계획, 현재 브라우저 상태 등)을 바탕으로 LLM을 호출합니다.
        *   LLM은 `NavigatorActionRegistry`에 정의된 액션 스키마에 따라, 현재 상황에서 가장 적절하다고 판단되는 하나 이상의 브라우저 액션(예: `click`, `inputText`)과 그 인자들을 반환합니다.
        *   `doMultiAction()`: LLM이 반환한 액션 지시들을 순차적으로 실행합니다. 각 액션은 `NavigatorActionRegistry`에서 해당 이름의 `Action` 객체를 찾아 `call()` 메서드를 실행하고, 이 `Action` 객체는 내부적으로 `Page` 객체(`../../browser/page.ts`)의 메서드들을 사용하여 실제 브라우저를 조작합니다.
        *   각 액션의 실행 결과(`ActionResult`)는 `AgentContext.actionResults`에 저장됩니다. 이 결과에는 성공 여부, 추출된 데이터, 오류 메시지, 그리고 해당 결과를 다음 LLM 호출 시 메모리에 포함할지 여부(`includeInMemory`) 등이 담깁니다.
    *   `NavigatorAgent`가 반환한 결과에 `done: true`가 포함되어 있다면 (예: `finish` 액션 호출 등), `Executor`는 현재 작업 단위가 완료되었다고 간주하는 `done` 플래그를 설정합니다.
    *   액션 수행 중 오류 발생 시 `context.consecutiveFailures`가 증가하며, 최대 허용치를 넘으면 작업이 실패 처리될 수 있습니다.

5.  **검증 단계 (조건부 실행 - `ValidatorAgent`)**:
    *   `done` 플래그가 `true`로 설정되어 있고 (즉, Planner 또는 Navigator가 현재 작업 단위를 완료했다고 판단), `options.validateOutput`이 `true`로 설정되어 있으며, 작업이 중단/일시정지 상태가 아니라면 `validator.execute()`가 호출됩니다.
    *   `ValidatorAgent`는 `AgentContext`의 메시지 이력, 현재 브라우저 상태, 그리고 `Executor`가 `setPlan()`을 통해 전달한 현재 작업 계획을 종합하여 LLM을 호출합니다.
    *   LLM은 작업 결과가 유효한지(`is_valid`), 그 이유는 무엇인지(`reason`), 그리고 만약 유효하다면 최종적인 답변은 무엇인지(`answer`)를 포함하는 `ValidatorOutput` 형식의 응답을 반환합니다.
    *   만약 `is_valid: true`이면, 작업이 성공적으로 완료된 것으로 간주하고 메인 루프를 종료합니다.
    *   만약 `is_valid: false`이면, `validatorFailed = true`로 설정하고, 실패 이유를 `ActionResult`로 변환하여 `AgentContext.actionResults`에 추가합니다. 이렇게 하면 다음 루프의 계획 단계에서 `PlannerAgent`가 이 실패 정보를 참고하여 더 나은 계획을 수립하려고 시도할 수 있습니다.

6.  **루프 반복 또는 종료**:
    *   메인 루프는 다음 조건 중 하나가 만족될 때까지 3~5단계를 반복합니다:
        *   `ValidatorAgent`가 `is_valid: true`를 반환 (최종 성공).
        *   `PlannerAgent`가 `done: true`이고 `web_task: false`를 반환 (웹 작업 없이 완료).
        *   설정된 최대 스텝 수(`options.maxSteps`)에 도달 (실패).
        *   작업이 명시적으로 중단(`stopped`)됨.
        *   최대 연속 실패 횟수(`options.maxFailures`)에 도달 (실패).

7.  **최종 처리 및 이벤트 발생**:
    *   루프가 종료되면, `Executor`는 작업의 최종 상태(TASK_OK, TASK_FAIL, TASK_CANCEL, TASK_PAUSE)에 따라 적절한 시스템 이벤트를 발생시킵니다.
    *   필요한 경우 `cleanup()` 메서드가 호출되어 브라우저 컨텍스트 등을 정리합니다.

## 4. 이벤트 기반 아키텍처

`EventManager`와 `AgentContext.emitEvent`를 통해 시스템 내의 주요 상태 변화나 에이전트 활동이 이벤트로 발행됩니다. 외부에서는 `Executor.subscribeExecutionEvents`를 통해 이러한 이벤트들을 구독하여 UI 업데이트, 로깅, 디버깅 등 다양한 용도로 활용할 수 있습니다. 이벤트에는 발생 주체(Actor: SYSTEM, PLANNER, NAVIGATOR, VALIDATOR), 상태(ExecutionState: TASK_START, STEP_OK, ACT_FAIL 등), 관련 데이터 등이 포함됩니다.

## 5. 결론

`@agent-infra/browser-use` 패키지의 에이전트 시스템은 `Executor`를 중심으로 잘 정의된 역할을 가진 Planner, Navigator, Validator 에이전트들이 `AgentContext`라는 공유된 정보 허브를 통해 협력하는 정교한 구조를 가지고 있습니다. LLM을 활용하여 각 단계(계획, 실행, 검증)를 지능적으로 처리하며, 이벤트 기반 아키텍처와 유연한 제어 메커니즘을 통해 복잡한 웹 기반 작업을 자율적으로 수행할 수 있는 잠재력을 보여줍니다. 이는 ReAct와 유사한 에이전트 패러다임을 실제 브라우저 환경에 적용한 구현체로 볼 수 있습니다.
