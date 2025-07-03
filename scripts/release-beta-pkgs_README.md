# `release-beta-pkgs.sh` 스크립트 분석

## 1. 스크립트 위치

`scripts/release-beta-pkgs.sh`

## 2. 스크립트 개요

이 셸 스크립트는 프로젝트의 패키지들을 "베타(beta)" 버전으로 릴리스(배포)하는 과정을 자동화합니다. 주로 모노레포 환경에서 `changeset` 도구와 `pnpm` 패키지 매니저를 사용하여 버전 관리, 변경 로그 생성, npm 레지스트리 게시 등의 작업을 수행합니다.

## 3. 주요 기능 및 로직

1.  **스크립트 설정**:
    *   `#!/usr/bin/env bash`: 스크립트를 bash 셸 환경에서 실행하도록 지정합니다.
    *   `set -e`: 스크립트 실행 중 오류가 발생하면 즉시 실행을 중단하도록 설정합니다. (오류에 강인한 스크립트 작성)

2.  **Changeset 사전 릴리스 모드 진입**:
    *   `pnpm changeset pre enter beta`: `changeset` 도구를 사용하여 "beta"라는 이름의 사전 릴리스 모드로 진입합니다. 이는 이후 버전 관리가 베타 버전에 맞게 이루어지도록 설정합니다.

3.  **릴리스 시작 메시지**:
    *   `echo "=== start release ==="`: 릴리스 프로세스 시작을 알리는 메시지를 출력합니다.

4.  **버전 업데이트 및 변경 로그 생성**:
    *   `echo "1. update version and generate CHANGELOG..."`: 작업 내용을 설명하는 메시지를 출력합니다.
    *   `pnpm changeset version`: `changeset`를 사용하여 패키지들의 버전을 업데이트하고, 변경 사항에 따라 `CHANGELOG.md` 파일을 생성/업데이트합니다. `.changeset` 폴더 내의 마크다운 파일들을 기반으로 작동합니다.

5.  **의존성 업데이트**:
    *   `echo "2. update dependencies..."`: 작업 내용을 설명하는 메시지를 출력합니다.
    *   `pnpm install`: `pnpm`을 사용하여 프로젝트의 의존성을 업데이트합니다. 이는 `package.json` 파일 및 `pnpm-lock.yaml` 파일이 `changeset version` 명령으로 인해 변경되었을 수 있으므로, 이를 반영하기 위함입니다.

6.  **npm에 패키지 게시 (Publish)**:
    *   `echo "3. publish to npm..."`: 작업 내용을 설명하는 메시지를 출력합니다.
    *   `pnpm publish -r --no-git-checks --access public --tag beta`:
        *   `pnpm publish -r`: 모노레포 내의 변경된 모든 패키지를 npm 레지스트리에 게시합니다. (`-r` 또는 `--recursive`)
        *   `--no-git-checks`: Git 저장소의 상태(예: 커밋되지 않은 변경 사항)를 확인하지 않고 게시를 진행합니다.
        *   `--access public`: 게시되는 패키지를 공개(public) 접근 권한으로 설정합니다.
        *   `--tag beta`: npm에 게시할 때 "beta"라는 태그를 사용하여 게시합니다. 이를 통해 `npm install package-name@beta`와 같이 특정 태그로 패키지를 설치할 수 있게 됩니다.

7.  **Changeset 사전 릴리스 모드 종료**:
    *   `echo "4. exit changeset..."`: 작업 내용을 설명하는 메시지를 출력합니다.
    *   `pnpm changeset pre exit`: `changeset`의 사전 릴리스 모드를 종료합니다.

8.  **Git 저장소에 변경 사항 푸시 (Push) - 사용자 확인 필요**:
    *   `echo "5. prepare to push to remote git repository..."`: 작업 내용을 설명하는 메시지를 출력합니다.
    *   `read -p "confirm push to remote git repository? (y/N) " confirm`: 사용자에게 원격 Git 저장소로 변경 사항을 푸시할 것인지 확인하는 프롬프트를 표시합니다.
    *   `if [[ $confirm == [yY] ]]; then ... else ... fi`: 사용자가 'y' 또는 'Y'를 입력하면 다음을 수행합니다:
        *   `git add .`: 모든 변경된 파일을 Git 스테이징 영역에 추가합니다.
        *   `git commit -m "release: publish beta packages"`: "release: publish beta packages"라는 커밋 메시지와 함께 변경 사항을 커밋합니다.
        *   `echo "pushing code and tag to remote git repository..."`: 작업 내용을 설명하는 메시지를 출력합니다.
        *   `git push --follow-tags`: 현재 브랜치의 커밋과 함께 로컬 태그(changeset version에 의해 생성된 버전 태그 등)를 원격 저장소로 푸시합니다.
        *   `echo "=== release-beta completed ==="`: 베타 릴리스 완료 메시지를 출력합니다.
    *   사용자가 다른 값을 입력하면:
        *   `echo "cancel pushing to remote git repository"`: 원격 저장소로의 푸시가 취소되었음을 알립니다.
        *   `echo "=== release-beta completed (not pushed to remote) ==="`: 원격 푸시 없이 베타 릴리스가 완료되었음을 알립니다.

## 4. 예상되는 사용 시나리오

*   개발팀이 새로운 기능 개발이나 버그 수정 후, 정식 릴리스 전에 테스트 목적으로 베타 버전을 배포하고자 할 때 이 스크립트를 사용합니다.
*   스크립트 실행자는 일반적으로 `.changeset` 폴더에 변경 사항에 대한 마크다운 파일을 미리 작성해 둡니다.
*   스크립트를 실행하면 버전 업데이트, 변경 로그 생성, npm 게시, Git 커밋 및 푸시(선택 사항)까지의 과정이 자동화됩니다.

## 5. 의존성

*   `bash`: 스크립트 실행 환경.
*   `pnpm`: 패키지 매니저 및 스크립트 실행기.
*   `@changesets/cli`: 버전 관리 및 변경 로그 생성을 위한 도구 (`changeset` 명령어).
*   `git`: 버전 관리 시스템.

이러한 도구들은 스크립트 실행 환경에 미리 설치되어 있어야 합니다.

## 6. 실행 방법 (추정)

프로젝트 루트 디렉토리에서 다음 명령으로 직접 실행할 수 있습니다:

```bash
bash scripts/release-beta-pkgs.sh
# 또는 실행 권한이 있다면
# ./scripts/release-beta-pkgs.sh
```

또는 `package.json`의 `scripts` 섹션에 이 스크립트를 실행하는 명령이 정의되어 있을 수 있습니다 (예: `pnpm run release:beta`).

## 7. 추가 고려 사항

*   **Git 상태**: 스크립트 실행 전에 현재 브랜치가 올바른지, 불필요한 변경 사항이 없는지 확인하는 것이 좋습니다. `--no-git-checks` 옵션이 사용되지만, 이는 npm 게시 시에만 적용될 수 있습니다.
*   **사용자 확인**: Git 푸시 전에 사용자 확인을 받는 것은 중요한 안전장치입니다. 실수로 원치 않는 변경 사항이 원격 저장소에 푸시되는 것을 방지합니다.
*   **오류 처리**: `set -e`로 기본적인 오류 처리를 하지만, 각 명령어의 실패 가능성에 대한 더 세밀한 오류 처리 로직은 포함되어 있지 않습니다.

이 스크립트는 프로젝트의 베타 릴리스 프로세스를 표준화하고 자동화하여 효율성을 높이는 데 중요한 역할을 합니다.
