# zoom-slack-notifier

매일 아침 오늘 예정된 줌 회의 목록을 자동으로 확인하여 슬랙 채널에 알림을 보내는 Claude Code 스킬입니다.

## 기능

- 줌 API를 통해 오늘 예정된 회의 목록 자동 조회
- 회의 정보(제목, 시간, 링크)를 슬랙 채널에 전송
- 크론잡으로 매일 아침 자동 실행 가능
- Claude에게 요청만 하면 즉시 확인 가능

## 설치

### 한 줄 설치 (GitHub에서)

```bash
mkdir -p .claude/skills && curl -sL https://github.com/[사용자명]/zoom-slack-notifier/archive/refs/heads/master.tar.gz | tar -xz -C /tmp && mv /tmp/zoom-slack-notifier-master .claude/skills/zoom-slack-notifier
```

### 수동 설치

```bash
mkdir -p .claude/skills
cd .claude/skills
git clone https://github.com/[사용자명]/zoom-slack-notifier.git
```

## 환경 설정

### 1. 필수 API 키 발급

다음 서비스의 API 키가 필요합니다:

- **줌 API**: Server-to-Server OAuth 앱 생성
- **슬랙 웹훅**: Incoming Webhook 설정

자세한 발급 방법은 [references/SETUP.md](references/SETUP.md)를 참고하세요.

### 2. 환경변수 설정

프로젝트 루트에 `.env` 파일을 생성하세요:

```bash
ZOOM_CLIENT_ID=your_zoom_client_id
ZOOM_CLIENT_SECRET=your_zoom_client_secret
ZOOM_ACCOUNT_ID=your_zoom_account_id
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
SLACK_CHANNEL=#meetings
```

### 3. 의존성 설치

```bash
pip install requests python-dotenv
```

## 사용 방법

### Claude에게 요청하기

```
오늘 줌 회의 슬랙으로 알려줘
```

또는

```
오늘 미팅 있어?
```

### 수동 실행

```bash
python3 .claude/skills/zoom-slack-notifier/scripts/notify_meetings.py
```

### 자동 실행 (크론잡)

매일 오전 9시에 자동으로 실행:

```bash
crontab -e

# 다음 줄 추가
0 9 * * * cd /path/to/project && python3 .claude/skills/zoom-slack-notifier/scripts/notify_meetings.py
```

## 슬랙 알림 예시

```
📅 오늘의 줌 회의 (2025-12-24)

🔹 주간 스프린트 리뷰
   ⏰ 10:00 - 11:00
   🔗 https://zoom.us/j/123456789

🔹 클라이언트 미팅
   ⏰ 14:00 - 15:00
   🔗 https://zoom.us/j/987654321

총 2개의 회의가 예정되어 있습니다.
```

## 스킬 구조

```
zoom-slack-notifier/
├── README.md                    # GitHub 배포용 문서
├── SKILL.md                     # AI용 스킬 정의
├── scripts/
│   ├── notify_meetings.py       # 메인 스크립트
│   └── check_update.py          # 업데이트 확인
└── references/
    └── SETUP.md                 # 환경 설정 가이드
```

## 요구사항

- Python 3.7+
- `requests` 라이브러리
- `python-dotenv` 라이브러리
- 줌 계정 및 API 액세스 권한
- 슬랙 워크스페이스 및 웹훅 권한

## 문제 해결

### API 연결 실패

- 환경변수가 올바르게 설정되었는지 확인
- 줌 앱이 활성화되었는지 확인
- 슬랙 웹훅 URL이 유효한지 확인

### 회의가 표시되지 않음

- 줌 API 권한(Scopes)이 올바른지 확인
- 회의가 실제로 오늘 예정되어 있는지 확인
- 시간대 설정 확인 (기본: UTC+9 한국 시간)

자세한 문제 해결 방법은 [references/SETUP.md](references/SETUP.md#문제-해결)를 참고하세요.

## 라이선스

MIT License

## 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요. PR도 환영합니다!

## 관련 링크

- [줌 API 문서](https://developers.zoom.us/docs/api/)
- [슬랙 웹훅 가이드](https://api.slack.com/messaging/webhooks)
- [Claude Code 문서](https://github.com/anthropics/claude-code)
