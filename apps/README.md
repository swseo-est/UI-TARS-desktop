# `apps` 폴더 분석

이 `apps` 폴더는 최종 사용자에게 제공되는 실제 실행 가능한 애플리케이션들을 포함하는 것으로 보입니다. 모노레포 구조에서 최상위 애플리케이션 프로젝트들이 위치하는 일반적인 장소입니다.

## 주요 하위 폴더 및 역할

*   **`ui-tars/`**: 이 폴더는 `TARS`라는 이름의 UI 애플리케이션을 포함하고 있는 것으로 강력하게 추정됩니다.
    *   `electron-builder.yml`, `electron.vite.config.ts`: Electron 기반의 데스크톱 애플리케이션임을 시사합니다. Electron은 웹 기술(HTML, CSS, JavaScript/TypeScript)을 사용하여 크로스 플랫폼 데스크톱 앱을 만들 수 있게 해주는 프레임워크입니다.
    *   `package.json`: 이 애플리케이션의 의존성, 스크립트 등을 정의합니다.
    *   `src/`: 애플리케이션의 소스 코드가 위치합니다. (`main/`, `preload/`, `renderer/` 등의 하위 폴더 구조는 Electron 앱의 일반적인 구조입니다.)
        *   `main/`: Electron의 메인 프로세스 관련 코드를 포함합니다. (예: 윈도우 생성, 시스템 이벤트 처리)
        *   `preload/`: 메인 프로세스와 렌더러 프로세스 간의 안전한 통신을 위한 스크립트를 포함합니다.
        *   `renderer/`: 실제 사용자 인터페이스(UI)를 렌더링하는 코드를 포함합니다. (예: React, Vue, Angular 등의 UI 프레임워크 사용 가능)
    *   `resources/`: 아이콘, 이미지 등 애플리케이션에서 사용되는 정적 리소스 파일들이 위치합니다.
    *   `e2e/`: End-to-End 테스트 코드가 위치합니다.
    *   `static/`: 정적 파일들이 위치합니다. (예: dmg 배경 이미지)

## 예상되는 기능

*   `ui-tars` 애플리케이션은 프로젝트의 핵심 AI 에이전트(`TARS`로 추정)와 상호작용할 수 있는 그래픽 사용자 인터페이스(GUI)를 제공할 것으로 예상됩니다.
*   사용자는 이 앱을 통해 AI 에이전트에게 작업을 지시하고, 진행 상황을 모니터링하며, 결과를 확인할 수 있을 것입니다.
*   Electron 기반이므로 Windows, macOS, Linux 등 다양한 데스크톱 환경을 지원할 가능성이 높습니다.

## 의존성 관계 (추정)

*   `apps/ui-tars/`는 `packages/ui-tars/sdk` 또는 `multimodal/agent-tars/`와 같은 다른 패키지/모듈에 정의된 기능(SDK, 에이전트 로직 등)을 사용할 가능성이 매우 높습니다.
*   루트 `package.json` 및 `pnpm-workspace.yaml`을 통해 이러한 내부 패키지 의존성이 관리될 것입니다.

## 향후 분석 방향

*   `apps/ui-tars/package.json`을 분석하여 사용된 주요 프레임워크 및 라이브러리를 식별합니다.
*   `apps/ui-tars/src/` 내부의 소스 코드를 분석하여 UI 컴포넌트 구조, 상태 관리 방식, 백엔드(메인 프로세스)와의 통신 방법 등을 파악합니다.
*   `PROJECT_CORE_FEATURES.md`에서 언급된 다른 모듈(특히 `multimodal/agent-tars/` 및 `packages/ui-tars/`)과의 연관 관계를 구체적으로 파악합니다.
