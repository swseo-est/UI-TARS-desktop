# `merge-yml.ts` 스크립트 분석

## 1. 스크립트 위치

`scripts/merge-yml/merge-yml.ts`

## 2. 스크립트 개요

이 TypeScript 스크립트는 동일한 디렉토리 내에 있는 두 개의 YAML 파일 (`latest-mac-x64.yml` 와 `latest-mac-arm64.yml`)을 읽어들여, 그 내용을 병합한 후 새로운 YAML 파일 (`latest-mac.yml`)을 생성하는 역할을 합니다.

주로 macOS 애플리케이션의 x64 (Intel) 아키텍처와 arm64 (Apple Silicon) 아키텍처 각각에 대한 업데이트 정보를 담고 있는 YAML 파일들을 하나로 합치는 데 사용되는 것으로 보입니다. Electron 애플리케이션의 자동 업데이트 기능과 관련하여 `electron-builder` 또는 `electron-updater`가 생성하는 `latest-mac.yml` 형식의 파일을 다루는 것으로 강력히 추정됩니다.

## 3. 주요 기능 및 로직

1.  **모듈 임포트**:
    *   `fs` (Node.js File System): 파일 읽기 및 쓰기 작업을 위해 사용됩니다.
    *   `path` (Node.js Path): 파일 경로를 다루기 위해 사용됩니다.
    *   `js-yaml`: YAML 데이터를 파싱하고 생성(dump)하기 위해 사용되는 외부 라이브러리입니다.

2.  **파일 읽기**:
    *   스크립트가 위치한 현재 디렉토리(`cwd`)를 기준으로 `latest-mac-x64.yml` 파일과 `latest-mac-arm64.yml` 파일의 내용을 동기적으로 읽어들입니다. UTF-8 인코딩을 사용합니다.

3.  **데이터 구조 정의 (Interface `YamlData`)**:
    *   YAML 파일 내의 데이터 구조를 TypeScript 인터페이스로 정의합니다.
        *   `version` (optional, string): 애플리케이션 버전.
        *   `files` (array of objects): 각 파일에 대한 정보를 담는 배열. 각 객체는 다음을 포함합니다:
            *   `url` (string): 파일 다운로드 URL.
            *   `sha512` (string): 파일의 SHA512 체크섬.
            *   `size` (number): 파일 크기.
        *   `releaseDate` (optional, string): 릴리스 날짜.

4.  **YAML 파싱**:
    *   읽어들인 `x64Content`와 `arm64Content` 문자열을 `yaml.load()`를 사용하여 `YamlData` 타입의 JavaScript 객체로 변환합니다.

5.  **데이터 병합**:
    *   `files` 필드: `x64Data.files` 배열과 `arm64Data.files` 배열을 합쳐서 `mergedFiles` 배열을 생성합니다. 각 원본 배열이 존재하지 않을 경우 빈 배열로 처리하여 오류를 방지합니다.
    *   `version` 필드: `x64Data.version` 값을 사용하며, 없을 경우 기본값으로 '0.0.0'을 사용합니다.
    *   `releaseDate` 필드: `x64Data.releaseDate` 값을 사용하며, 없을 경우 빈 문자열을 사용합니다.
    *   병합된 `files`와 다른 필드들을 조합하여 `combinedData` 객체를 생성합니다.

6.  **YAML 생성 및 파일 쓰기**:
    *   `yaml.dump()`를 사용하여 `combinedData` 객체를 YAML 형식의 문자열로 변환합니다. `lineWidth: 120` 옵션을 사용하여 줄 너비를 설정합니다.
    *   생성된 YAML 문자열을 `latest-mac.yml`이라는 이름의 파일로 현재 디렉토리에 동기적으로 저장합니다. UTF-8 인코딩을 사용합니다.

## 4. 예상되는 사용 시나리오

*   macOS 애플리케이션을 x64 및 arm64 두 가지 아키텍처로 빌드한 후, 각 빌드 결과물에 대한 업데이트 정보 파일(`latest-mac-x64.yml`, `latest-mac-arm64.yml`)이 생성됩니다.
*   이 스크립트는 이 두 파일을 하나로 합쳐, `electron-updater`가 두 아키텍처를 모두 지원하는 단일 업데이트 매니페스트 파일(`latest-mac.yml`)로 사용할 수 있도록 합니다.
*   이를 통해 사용자의 Mac 아키텍처에 맞는 애플리케이션 업데이트를 제공할 수 있습니다.

## 5. 의존성

*   `js-yaml`: YAML 처리를 위한 외부 라이브러리. 이 스크립트를 실행하기 전에 `npm install js-yaml @types/js-yaml` 또는 `pnpm add js-yaml @types/js-yaml` 등으로 설치해야 합니다. (프로젝트 전반의 `package.json`에 이미 포함되어 있을 가능성이 높습니다.)

## 6. 실행 방법 (추정)

프로젝트의 `package.json` 파일 내 `scripts` 섹션에 이 스크립트를 실행하는 명령이 정의되어 있거나, CI/CD 파이프라인의 일부로 실행될 수 있습니다.
직접 실행한다면 Node.js 환경에서 다음 명령으로 실행할 수 있습니다 (TypeScript 컴파일 과정이 필요할 수 있음):

```bash
# TypeScript를 JavaScript로 컴파일 (예시)
# npx tsc scripts/merge-yml/merge-yml.ts --outDir scripts/merge-yml/dist (설정에 따라 다름)

# 컴파일된 JavaScript 실행
node scripts/merge-yml/dist/merge-yml.js
# 또는 ts-node를 사용하여 직접 실행
# npx ts-node scripts/merge-yml/merge-yml.ts
```

## 7. 추가 고려 사항

*   스크립트는 `x64Data`의 `version`과 `releaseDate`를 우선적으로 사용합니다. 만약 `arm64Data`의 정보가 더 최신이거나 다른 값을 가져야 한다면, 병합 로직 수정이 필요할 수 있습니다.
*   오류 처리: 파일 읽기 실패, YAML 파싱 실패 등의 경우에 대한 명시적인 오류 처리는 코드에 포함되어 있지 않습니다. 스크립트 실행 환경에서 이러한 오류를 처리할 것으로 가정합니다.

이 스크립트는 macOS용 Electron 앱의 멀티 아키텍처 배포 및 업데이트 프로세스에서 중요한 역할을 수행하는 유틸리티로 보입니다.
