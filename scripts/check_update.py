#!/usr/bin/env python3
"""
스킬 업데이트 확인 스크립트
GitHub 저장소의 최신 버전과 비교하여 업데이트가 필요한지 확인합니다.
"""

import os
import sys
import json
import requests
import argparse
from pathlib import Path


class UpdateChecker:
    def __init__(self, skill_path: str, repo_url: str = None):
        self.skill_path = Path(skill_path)
        self.repo_url = repo_url or "https://github.com/[사용자명]/zoom-slack-notifier"
        self.version_file = self.skill_path / ".version"
        self.current_version = self._get_current_version()

    def _get_current_version(self) -> str:
        """현재 설치된 버전 확인"""
        if self.version_file.exists():
            return self.version_file.read_text().strip()
        return "unknown"

    def check_for_updates(self) -> dict:
        """GitHub에서 최신 버전 확인"""
        try:
            # GitHub API로 최신 커밋 확인
            api_url = self.repo_url.replace("github.com", "api.github.com/repos")
            api_url = f"{api_url}/commits/master"

            response = requests.get(api_url)
            response.raise_for_status()

            latest_commit = response.json()
            latest_sha = latest_commit['sha'][:7]  # 짧은 SHA

            return {
                'has_update': latest_sha != self.current_version,
                'current': self.current_version,
                'latest': latest_sha,
                'message': latest_commit['commit']['message']
            }
        except Exception as e:
            return {
                'has_update': False,
                'error': str(e)
            }

    def update(self):
        """스킬 업데이트 수행"""
        print(f"🔄 {self.skill_path.name} 업데이트 중...")

        # GitHub에서 최신 버전 다운로드
        archive_url = f"{self.repo_url}/archive/refs/heads/master.tar.gz"

        try:
            # 임시 디렉토리에 다운로드
            import tempfile
            import tarfile

            with tempfile.TemporaryDirectory() as tmpdir:
                tmpfile = Path(tmpdir) / "update.tar.gz"

                # 다운로드
                response = requests.get(archive_url)
                response.raise_for_status()
                tmpfile.write_bytes(response.content)

                # 압축 해제
                with tarfile.open(tmpfile, 'r:gz') as tar:
                    tar.extractall(tmpdir)

                # 파일 복사
                import shutil
                extracted_dir = Path(tmpdir) / f"{self.skill_path.name}-master"

                if extracted_dir.exists():
                    # 기존 스킬 백업
                    backup_path = self.skill_path.parent / f"{self.skill_path.name}.backup"
                    if backup_path.exists():
                        shutil.rmtree(backup_path)
                    shutil.copytree(self.skill_path, backup_path)

                    # 새 버전으로 교체
                    shutil.rmtree(self.skill_path)
                    shutil.copytree(extracted_dir, self.skill_path)

                    print(f"✅ 업데이트 완료!")
                    print(f"📦 백업 위치: {backup_path}")
                    return True

        except Exception as e:
            print(f"❌ 업데이트 실패: {e}")
            return False

    def run(self, auto_update: bool = False, quiet: bool = False):
        """업데이트 확인 및 실행"""
        result = self.check_for_updates()

        if 'error' in result:
            if not quiet:
                print(f"⚠️  업데이트 확인 실패: {result['error']}")
            return

        if result['has_update']:
            if not quiet:
                print(f"🆕 새 버전이 있습니다!")
                print(f"   현재: {result['current']}")
                print(f"   최신: {result['latest']}")
                print(f"   변경사항: {result['message']}")

            if auto_update:
                self.update()
            else:
                if not quiet:
                    print(f"\n업데이트하려면 다음 명령을 실행하세요:")
                    print(f"python3 {__file__} --update")
        else:
            if not quiet:
                print(f"✅ 최신 버전입니다 ({result['current']})")


def main():
    parser = argparse.ArgumentParser(description='스킬 업데이트 확인')
    parser.add_argument('--update', action='store_true', help='자동 업데이트 수행')
    parser.add_argument('--auto', action='store_true', help='업데이트가 있으면 자동 실행')
    parser.add_argument('--quiet', action='store_true', help='최소한의 출력만 표시')
    parser.add_argument('--repo', type=str, help='GitHub 저장소 URL (기본값: 스킬 저장소)')

    args = parser.parse_args()

    # 스킬 경로 자동 감지
    script_path = Path(__file__).resolve()
    skill_path = script_path.parent.parent

    checker = UpdateChecker(skill_path, args.repo)

    if args.update:
        checker.update()
    else:
        checker.run(auto_update=args.auto, quiet=args.quiet)


if __name__ == '__main__':
    main()
