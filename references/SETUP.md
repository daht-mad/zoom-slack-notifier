# 환경 설정 가이드

zoom-slack-notifier 스킬을 사용하기 위한 환경 설정 방법입니다.

## 1. 줌 API 설정

### 1.1 줌 앱 생성

1. [줌 마켓플레이스](https://marketplace.zoom.us/)에 접속
2. 우측 상단 **Develop** > **Build App** 클릭
3. **Server-to-Server OAuth** 선택
4. 앱 이름 입력 (예: "Meeting Notifier")
5. **Create** 클릭

### 1.2 필수 정보 수집

앱 생성 후 다음 정보를 메모해두세요:

- **Account ID**: App Credentials 탭에서 확인
- **Client ID**: App Credentials 탭에서 확인
- **Client Secret**: App Credentials 탭에서 확인

### 1.3 권한 설정 (Scopes)

**Scopes** 탭에서 다음 권한을 추가하세요:

- `meeting:read:admin` - 회의 정보 읽기
- `user:read:admin` - 사용자 정보 읽기

권한 추가 후 **Continue** 클릭

### 1.4 앱 활성화

**Activation** 탭에서 앱을 활성화하세요.

## 2. 슬랙 봇 설정

### 2.1 슬랙 앱 생성

1. [슬랙 API](https://api.slack.com/apps)에 접속
2. **Create New App** 클릭
3. **From scratch** 선택
4. 앱 이름 입력 (예: "Zoom Meeting Notifier")
5. 워크스페이스 선택 후 **Create App** 클릭

### 2.2 봇 토큰 권한 설정

1. 좌측 메뉴에서 **OAuth & Permissions** 클릭
2. **Scopes** 섹션으로 스크롤
3. **Bot Token Scopes**에서 다음 권한 추가:
   - `chat:write` - 메시지 전송
   - `chat:write.public` - 공개 채널에 메시지 전송

### 2.3 워크스페이스에 앱 설치

1. 페이지 상단의 **Install to Workspace** 클릭
2. **Allow** 클릭하여 권한 승인

### 2.4 봇 토큰 복사

**OAuth & Permissions** 페이지에서 **Bot User OAuth Token**을 복사해두세요. 형식:
```
xoxb-[숫자]-[숫자]-[영문/숫자 조합]
```

## 3. 환경변수 설정

### 3.1 .env 파일 생성

**프로젝트 루트 디렉토리**에 `.env` 파일을 생성하세요:

```bash
# .env (프로젝트 루트에 위치)
ZOOM_CLIENT_ID=your_zoom_client_id_here
ZOOM_CLIENT_SECRET=your_zoom_client_secret_here
ZOOM_ACCOUNT_ID=your_zoom_account_id_here
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_CHANNEL=#meetings
```

**중요**:
- `.env` 파일은 **프로젝트 루트**에 위치해야 합니다 (여러 스킬에서 공용으로 사용)
- `.env` 파일은 절대 Git에 커밋하지 마세요! `.gitignore`에 추가하세요.

### 3.2 시스템 환경변수로 설정 (대안)

`.env` 파일 대신 시스템 환경변수로 설정할 수도 있습니다:

**macOS/Linux**:
```bash
export ZOOM_CLIENT_ID="your_zoom_client_id_here"
export ZOOM_CLIENT_SECRET="your_zoom_client_secret_here"
export ZOOM_ACCOUNT_ID="your_zoom_account_id_here"
export SLACK_BOT_TOKEN="xoxb-your-bot-token-here"
export SLACK_CHANNEL="#meetings"
```

**Windows (PowerShell)**:
```powershell
$env:ZOOM_CLIENT_ID="your_zoom_client_id_here"
$env:ZOOM_CLIENT_SECRET="your_zoom_client_secret_here"
$env:ZOOM_ACCOUNT_ID="your_zoom_account_id_here"
$env:SLACK_BOT_TOKEN="xoxb-your-bot-token-here"
$env:SLACK_CHANNEL="#meetings"
```

## 4. 의존성 설치

### 4.1 필수 Python 패키지 설치

```bash
pip install requests python-dotenv
```

또는 requirements.txt를 사용하는 경우:

```bash
pip install -r requirements.txt
```

### 4.2 requirements.txt 생성 (선택사항)

```bash
# requirements.txt
requests>=2.31.0
python-dotenv>=1.0.0
```

## 5. 테스트

설정이 완료되었으면 스크립트를 테스트해보세요:

```bash
python3 .claude/skills/zoom-slack-notifier/scripts/notify_meetings.py
```

성공 메시지가 나타나고 슬랙 채널에 알림이 도착하면 설정 완료입니다!

## 6. 자동화 설정 (선택사항)

### 6.1 크론잡으로 매일 아침 자동 실행

**macOS/Linux**:

```bash
# 크론탭 편집
crontab -e

# 매일 오전 9시에 실행
0 9 * * * cd /path/to/your/project && /usr/bin/python3 .claude/skills/zoom-slack-notifier/scripts/notify_meetings.py >> /tmp/zoom-notifier.log 2>&1
```

**주의**:
- `/path/to/your/project`를 실제 프로젝트 경로로 변경하세요
- Python 경로 확인: `which python3`

### 6.2 Windows 작업 스케줄러

1. **작업 스케줄러** 실행
2. **기본 작업 만들기** 클릭
3. 이름 입력: "Zoom Meeting Notifier"
4. 트리거: **매일**
5. 시작 시간: **09:00**
6. 작업: **프로그램 시작**
7. 프로그램/스크립트: `python`
8. 인수 추가: `.claude/skills/zoom-slack-notifier/scripts/notify_meetings.py`
9. 시작 위치: 프로젝트 경로

## 문제 해결

### 줌 API 토큰 발급 실패

- Client ID, Client Secret, Account ID가 정확한지 확인
- 줌 앱이 활성화되었는지 확인
- 인터넷 연결 확인

### 슬랙 메시지 전송 실패

- Bot Token이 정확한지 확인 (`xoxb-`로 시작해야 함)
- 채널 이름이 `#`으로 시작하는지 확인
- 슬랙 앱이 워크스페이스에 설치되어 있는지 확인
- 봇이 `chat:write` 및 `chat:write.public` 권한을 가지고 있는지 확인
- 채널이 private일 경우, 봇을 채널에 초대했는지 확인 (`/invite @앱이름`)

### 환경변수를 찾을 수 없음

- `.env` 파일이 **프로젝트 루트**에 있는지 확인
- 환경변수 이름이 정확한지 확인 (대소문자 구분)
  - `SLACK_WEBHOOK_URL` ❌ → `SLACK_BOT_TOKEN` ✅
- `python-dotenv`가 설치되어 있는지 확인

### 시간대 문제

현재 스크립트는 UTC 시간을 한국 시간(UTC+9)으로 변환합니다. 다른 시간대를 사용하는 경우 `notify_meetings.py`의 `format_slack_message()` 함수에서 시간대를 수정하세요.

## 보안 주의사항

- `.env` 파일을 절대 Git에 커밋하지 마세요
- API 키와 시크릿을 공개 저장소에 업로드하지 마세요
- 정기적으로 API 키를 갱신하세요
- 불필요한 권한(Scope)은 제거하세요
