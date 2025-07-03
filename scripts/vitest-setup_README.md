# `vitest-setup.ts` 스크립트 분석

## 1. 스크립트 위치

`scripts/vitest-setup.ts`

## 2. 스크립트 개요

이 TypeScript 스크립트는 `Vitest` 테스트 프레임워크를 위한 전역 설정 파일입니다. Vitest 테스트가 실행되기 전에 특정 모듈을 모킹(mocking)하거나, 테스트 환경에 필요한 다른 전역 설정을 수행하는 역할을 합니다.

이 파일은 일반적으로 `vitest.config.ts` 또는 `vitest.workspace.mts` 파일의 `setupFiles` 옵션을 통해 Vitest에 등록되어, 모든 테스트 파일 실행에 앞서 한 번 실행됩니다.

## 3. 주요 기능 및 로직

1.  **모듈 임포트**:
    *   `import { vi } from 'vitest';`: Vitest의 유틸리티 객체 `vi`를 임포트합니다. `vi`는 모킹, 스파이(spy), 타이머 조작 등 테스트에 필요한 다양한 기능을 제공합니다.

2.  **`electron-log` 모듈 모킹**:
    *   `vi.mock('electron-log', () => ({ ... }));`: `electron-log`라는 모듈을 모킹합니다.
        *   **목적**: `electron-log`는 Electron 애플리케이션에서 사용되는 로깅 라이브러리입니다. 테스트 환경에서는 실제 파일 시스템에 로그를 쓰거나 복잡한 전송(transport) 설정을 초기화하는 것을 원치 않을 수 있습니다. 따라서 이 모듈을 모킹하여 테스트 중에는 실제 로직 대신 단순화된 가짜 구현(console 출력 등)을 사용하도록 합니다.
        *   **모킹 내용**:
            *   `default.scope()`: `electron-log`의 스코프 함수를 모킹하여, `info`, `error`, `warn`, `debug` 메서드가 각각 `console.info`, `console.error`, `console.warn`, `console.debug`를 호출하도록 합니다. 즉, 로그가 실제 파일이 아닌 콘솔에 출력됩니다.
            *   `default.initialize`: `initialize` 함수를 `vi.fn()`으로 모킹하여, 호출 여부만 추적할 수 있는 빈 함수로 만듭니다.
            *   `default.transports.file.level`: 파일 전송 레벨을 'info'로 설정하는 것처럼 보이게 하지만, 실제 파일 로깅은 `scope()` 모킹으로 인해 발생하지 않을 것입니다.

3.  **`electron` 모듈 모킹**:
    *   `vi.mock('electron', () => ({ ... }));`: Electron의 핵심 모듈인 `electron` 자체를 모킹합니다.
        *   **목적**: Electron 모듈은 실제 Electron 환경(예: GUI 애플리케이션 실행)에서만 제대로 작동하는 API들을 많이 포함하고 있습니다. 일반적인 Node.js 기반의 Vitest 테스트 환경에서는 이러한 API를 직접 호출할 수 없거나 예기치 않은 동작을 유발할 수 있습니다. 따라서 테스트 중에는 이러한 API들을 가짜 함수로 대체합니다.
        *   **모킹 내용**:
            *   `app.on`: Electron의 `app` 객체에서 이벤트를 구독하는 `on` 메서드를 `vi.fn()`으로 모킹합니다.
            *   `shell.openPath`: 시스템의 기본 프로그램으로 특정 경로(파일, URL 등)를 여는 `shell.openPath` 메서드를 `vi.fn()`으로 모킹합니다.

## 4. 예상되는 사용 시나리오

*   이 설정 파일은 Electron 애플리케이션의 일부 로직(특히 메인 프로세스나 `electron-log`를 사용하는 유틸리티 함수)을 테스트할 때 사용됩니다.
*   테스트 코드가 `electron-log`를 사용하여 로그를 남기려고 하거나, `electron` 모듈의 `app` 또는 `shell` 객체의 특정 메서드를 호출하려고 할 때, 실제 모듈 대신 여기서 정의한 가짜 구현이 사용됩니다.
*   이를 통해 테스트 환경을 실제 Electron 실행 환경과 분리하여, 더 빠르고 안정적이며 예측 가능한 단위 테스트 및 통합 테스트를 수행할 수 있습니다.

## 5. 의존성

*   `vitest`: 테스트 프레임워크.
*   `electron-log` (모킹 대상): 프로젝트의 의존성으로 설치되어 있어야 합니다.
*   `electron` (모킹 대상): 프로젝트의 의존성으로 설치되어 있어야 합니다.

## 6. Vitest 설정과의 연동

이 파일은 단독으로 실행되기보다는, 프로젝트의 Vitest 설정 파일(예: `vitest.config.ts`, `vitest.workspace.mts`) 내의 `test.setupFiles` 배열에 경로가 지정되어 Vitest에 의해 자동으로 로드되고 실행됩니다.

예시 (`vitest.config.ts`):

```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    setupFiles: ['./scripts/vitest-setup.ts'], // 이 파일의 경로
    // ... other test configurations
  },
});
```

## 7. 추가 고려 사항

*   **모킹의 상세 수준**: 현재 모킹은 `electron-log`와 `electron`의 일부 기능에 대해서만 이루어져 있습니다. 프로젝트의 테스트 범위가 넓어지면서 다른 Electron API나 외부 모듈에 대한 모킹이 추가될 수 있습니다.
*   **테스트 대상**: 이 설정은 주로 Node.js 환경에서 실행되는 코드(예: Electron 메인 프로세스 로직, 유틸리티 함수)의 테스트에 영향을 미칩니다. Electron 렌더러 프로세스 코드(UI 관련)는 별도의 테스트 환경 설정(예: JSDOM, Playwright)을 가질 수 있습니다.

이 `vitest-setup.ts` 파일은 프로젝트의 테스트 환경을 구성하고, 외부 의존성 및 Electron 관련 API를 효과적으로 모킹하여 안정적인 테스트 실행을 보장하는 중요한 역할을 합니다.
