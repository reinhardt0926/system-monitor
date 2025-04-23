#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SystemMonitor 애플리케이션 빌드 스크립트
PyInstaller를 사용하여 배포 가능한 실행 파일을 생성합니다.
"""

import os
import platform
import shutil
import subprocess
import sys

def ensure_resources():
    """리소스 디렉토리 구조가 올바른지 확인"""
    icon_dir = os.path.join("resources", "icons")
    os.makedirs(icon_dir, exist_ok=True)
    
    # 아이콘 파일이 없으면 경고
    icon_path = os.path.join(icon_dir, "system_image.ico")
    if not os.path.exists(icon_path):
        print(f"경고: 아이콘 파일이 없습니다. ({icon_path})")
        print("필요한 경우 아이콘 파일을 추가하세요.")

def clean_build_directories():
    """빌드 관련 디렉토리 정리"""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    
    for directory in dirs_to_clean:
        if os.path.exists(directory):
            print(f"정리 중: {directory}")
            shutil.rmtree(directory)
    
    # 모든 __pycache__ 디렉토리 제거
    for root, dirs, files in os.walk("."):
        for d in dirs:
            if d == "__pycache__":
                path = os.path.join(root, d)
                print(f"정리 중: {path}")
                shutil.rmtree(path)

def run_build():
    """PyInstaller를 사용하여 빌드 실행"""
    system = platform.system()
    print(f"운영체제: {system}")
    
    # PyInstaller 명령어 설정
    cmd = ["pyinstaller", "--clean", "main.spec"]
    
    try:
        subprocess.run(cmd, check=True)
        print("\n빌드 성공!")
        
        # 빌드 결과물 경로 표시
        exe_path = os.path.join("dist", "SystemMonitor")
        if system == "Windows":
            exe_path += ".exe"
        
        if os.path.exists(exe_path):
            print(f"실행 파일: {os.path.abspath(exe_path)}")
        else:
            print(f"실행 파일: {os.path.abspath(os.path.join('dist', 'SystemMonitor'))}")
        
    except subprocess.CalledProcessError as e:
        print(f"빌드 실패: {e}")
        return False
    
    return True

def main():
    # 작업 디렉토리가 프로젝트 루트인지 확인
    if not os.path.exists("mnt_src"):
        print("오류: 스크립트는 프로젝트 루트 디렉토리에서 실행해야 합니다.")
        print("예: python build.py")
        return False
    
    # PyInstaller 설치 확인
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller가 설치되어 있지 않습니다. 설치 중...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # 리소스 확인
    ensure_resources()
    
    # 이전 빌드 정리
    clean_build_directories()
    
    # 빌드 실행
    return run_build()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)