#!/usr/bin/env python3
"""
줌 회의 목록을 가져와 슬랙으로 알림을 보내는 스크립트
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import base64


class ZoomSlackNotifier:
    def __init__(self):
        self.zoom_client_id = os.getenv('ZOOM_CLIENT_ID')
        self.zoom_client_secret = os.getenv('ZOOM_CLIENT_SECRET')
        self.zoom_account_id = os.getenv('ZOOM_ACCOUNT_ID')
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        self.slack_channel = os.getenv('SLACK_CHANNEL', '#general')

        self.validate_env()
        self.access_token = None

    def validate_env(self):
        """환경변수 검증"""
        missing = []
        if not self.zoom_client_id:
            missing.append('ZOOM_CLIENT_ID')
        if not self.zoom_client_secret:
            missing.append('ZOOM_CLIENT_SECRET')
        if not self.zoom_account_id:
            missing.append('ZOOM_ACCOUNT_ID')
        if not self.slack_webhook_url:
            missing.append('SLACK_WEBHOOK_URL')

        if missing:
            print(f"❌ 환경변수가 설정되지 않았습니다: {', '.join(missing)}")
            print("\n.env 파일을 생성하거나 환경변수를 설정해주세요.")
            print("자세한 내용은 references/SETUP.md를 참고하세요.")
            sys.exit(1)

    def get_access_token(self) -> str:
        """줌 API 액세스 토큰 발급 (Server-to-Server OAuth)"""
        url = "https://zoom.us/oauth/token"

        # Base64 인코딩
        credentials = f"{self.zoom_client_id}:{self.zoom_client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": "account_credentials",
            "account_id": self.zoom_account_id
        }

        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            token_data = response.json()
            return token_data['access_token']
        except requests.exceptions.RequestException as e:
            print(f"❌ 줌 API 토큰 발급 실패: {e}")
            sys.exit(1)

    def get_todays_meetings(self) -> List[Dict]:
        """오늘 예정된 줌 회의 목록 조회"""
        if not self.access_token:
            self.access_token = self.get_access_token()

        # 오늘 날짜 범위 설정
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)

        url = "https://api.zoom.us/v2/users/me/meetings"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        params = {
            "type": "scheduled",
            "page_size": 100
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            all_meetings = response.json().get('meetings', [])

            # 오늘 날짜의 회의만 필터링
            todays_meetings = []
            for meeting in all_meetings:
                meeting_time = datetime.strptime(meeting['start_time'], '%Y-%m-%dT%H:%M:%SZ')
                meeting_date = meeting_time.date()

                if meeting_date == today:
                    todays_meetings.append({
                        'topic': meeting['topic'],
                        'start_time': meeting['start_time'],
                        'duration': meeting['duration'],
                        'join_url': meeting['join_url']
                    })

            # 시간순 정렬
            todays_meetings.sort(key=lambda x: x['start_time'])
            return todays_meetings

        except requests.exceptions.RequestException as e:
            print(f"❌ 줌 회의 목록 조회 실패: {e}")
            return []

    def format_slack_message(self, meetings: List[Dict]) -> Dict:
        """슬랙 메시지 포맷팅"""
        today_str = datetime.now().strftime('%Y-%m-%d')

        if not meetings:
            return {
                "channel": self.slack_channel,
                "text": f"📅 오늘의 줌 회의 ({today_str})\n\n오늘 예정된 회의가 없습니다. 😊"
            }

        message_blocks = [f"📅 오늘의 줌 회의 ({today_str})\n"]

        for meeting in meetings:
            # UTC 시간을 로컬 시간으로 변환
            start_time = datetime.strptime(meeting['start_time'], '%Y-%m-%dT%H:%M:%SZ')
            # 한국 시간대로 변환 (UTC+9)
            local_time = start_time + timedelta(hours=9)
            time_str = local_time.strftime('%H:%M')

            end_time = local_time + timedelta(minutes=meeting['duration'])
            end_str = end_time.strftime('%H:%M')

            message_blocks.append(
                f"\n🔹 {meeting['topic']}\n"
                f"   ⏰ {time_str} - {end_str}\n"
                f"   🔗 {meeting['join_url']}"
            )

        message_blocks.append(f"\n\n총 {len(meetings)}개의 회의가 예정되어 있습니다.")

        return {
            "channel": self.slack_channel,
            "text": "".join(message_blocks)
        }

    def send_to_slack(self, message: Dict) -> bool:
        """슬랙으로 메시지 전송"""
        try:
            response = requests.post(
                self.slack_webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ 슬랙 메시지 전송 실패: {e}")
            return False

    def run(self):
        """메인 실행 함수"""
        print("🔍 오늘의 줌 회의를 확인하는 중...")

        # 줌 회의 목록 조회
        meetings = self.get_todays_meetings()

        # 슬랙 메시지 포맷팅
        slack_message = self.format_slack_message(meetings)

        # 슬랙으로 전송
        print("📤 슬랙으로 알림을 보내는 중...")
        success = self.send_to_slack(slack_message)

        if success:
            print("✅ 슬랙 알림이 성공적으로 전송되었습니다!")
            if meetings:
                print(f"📊 오늘 예정된 회의: {len(meetings)}개")
            else:
                print("📊 오늘 예정된 회의가 없습니다.")
        else:
            print("❌ 슬랙 알림 전송에 실패했습니다.")
            sys.exit(1)


def main():
    """CLI 진입점"""
    # .env 파일이 있으면 로드 (python-dotenv 사용 시)
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    notifier = ZoomSlackNotifier()
    notifier.run()


if __name__ == '__main__':
    main()
