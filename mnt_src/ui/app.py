import sys
import psutil
import GPUtil
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QProgressBar, QGroupBox, 
                             QPushButton, QSpinBox, QCheckBox)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon

class SystemMonitor(QMainWindow):
    def __init__(self, icon_path):
        super().__init__()
        self.setWindowTitle("System resource monitor")
        self.setMinimumSize(700, 500)
        
        self.setWindowIcon(QIcon(icon_path)) # icon 
        # 다크 테마 배경 설정
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(18, 18, 18))
        palette.setColor(QPalette.WindowText, QColor(238, 238, 238))
        self.setPalette(palette)
        
        
        # 메인 위젯 및 레이아웃 설정
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # CPU 모니터링 섹션
        self.cpu_group = QGroupBox("CPU 사용량")
        self.cpu_layout = QVBoxLayout()
        self.cpu_group.setLayout(self.cpu_layout)
        
        # 전체 CPU 사용량
        self.cpu_total_layout = QHBoxLayout()
        self.cpu_total_label = QLabel("전체 CPU:")
        self.cpu_total_progress = QProgressBar()
        self.cpu_total_progress.setRange(0, 100)
        self.cpu_total_value = QLabel("0%")
        self.cpu_total_layout.addWidget(self.cpu_total_label)
        self.cpu_total_layout.addWidget(self.cpu_total_progress)
        self.cpu_total_layout.addWidget(self.cpu_total_value)
        self.cpu_layout.addLayout(self.cpu_total_layout)
        
        # 개별 CPU 코어 사용량
        self.cpu_cores = {}
        for i in range(psutil.cpu_count()):
            core_layout = QHBoxLayout()
            core_label = QLabel(f"코어 {i}:")
            core_progress = QProgressBar()
            core_progress.setRange(0, 100)
            core_value = QLabel("0%")
            
            core_layout.addWidget(core_label)
            core_layout.addWidget(core_progress)
            core_layout.addWidget(core_value)
            
            self.cpu_cores[i] = {
                "layout": core_layout,
                "progress": core_progress,
                "value": core_value
            }
            self.cpu_layout.addLayout(core_layout)
        
        # RAM 모니터링 섹션
        self.ram_group = QGroupBox("메모리 사용량")
        self.ram_layout = QVBoxLayout()
        self.ram_group.setLayout(self.ram_layout)
        
        self.ram_bar_layout = QHBoxLayout()
        self.ram_label = QLabel("RAM:")
        self.ram_progress = QProgressBar()
        self.ram_progress.setRange(0, 100)
        self.ram_value = QLabel("0/0 GB (0%)")
        
        self.ram_bar_layout.addWidget(self.ram_label)
        self.ram_bar_layout.addWidget(self.ram_progress)
        self.ram_bar_layout.addWidget(self.ram_value)
        self.ram_layout.addLayout(self.ram_bar_layout)
        
        # GPU 모니터링 섹션
        self.gpu_group = QGroupBox("GPU 사용량")
        self.gpu_layout = QVBoxLayout()
        self.gpu_group.setLayout(self.gpu_layout)
        
        # GPU 정보 동적 추가
        self.gpus = {}
        self.update_gpu_widgets()
        
        # 설정 섹션
        self.settings_group = QGroupBox("설정")
        self.settings_layout = QHBoxLayout()
        self.settings_group.setLayout(self.settings_layout)
        
        self.refresh_label = QLabel("갱신 주기(초):")
        self.refresh_spinbox = QSpinBox()
        self.refresh_spinbox.setRange(1, 60)
        self.refresh_spinbox.setValue(2)
        self.refresh_spinbox.valueChanged.connect(self.update_refresh_rate)
        
        self.show_cores_checkbox = QCheckBox("CPU 코어 상세 표시")
        self.show_cores_checkbox.setChecked(True)
        self.show_cores_checkbox.stateChanged.connect(self.toggle_cpu_cores)
        
        self.settings_layout.addWidget(self.refresh_label)
        self.settings_layout.addWidget(self.refresh_spinbox)
        self.settings_layout.addWidget(self.show_cores_checkbox)
        self.settings_layout.addStretch()
        
        # 실행/중지 버튼 영역
        self.control_layout = QHBoxLayout()
        
        self.run_button = QPushButton("실행")
        self.run_button.setFixedSize(100, 30)
        self.run_button.clicked.connect(self.start_monitoring)
        
        self.stop_button = QPushButton("중지")
        self.stop_button.setFixedSize(100, 30)
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.stop_button.setEnabled(False)
        
        self.status_label = QLabel("상태: 대기 중")
        
        self.control_layout.addWidget(self.run_button)
        self.control_layout.addWidget(self.stop_button)
        self.control_layout.addWidget(self.status_label)
        self.control_layout.addStretch()
        
        # 메인 레이아웃에 위젯 추가
        self.main_layout.addWidget(self.cpu_group)
        self.main_layout.addWidget(self.ram_group)
        self.main_layout.addWidget(self.gpu_group)
        self.main_layout.addWidget(self.settings_group)
        self.main_layout.addLayout(self.control_layout)
        
        # 타이머 설정
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        
        # 스타일 적용
        self.apply_styles()
    
    def apply_styles(self):
        # 다크 테마 스타일 설정
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #121212;
                color: #EEEEEE;
            }
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 3px;
                text-align: center;
                height: 20px;
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;  /* 기본 색상 */
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #1E1E1E;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #EEEEEE;
            }
            QLabel {
                color: #EEEEEE;
            }
            QSpinBox, QCheckBox {
                background-color: #2D2D2D;
                color: #EEEEEE;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 2px;
            }
            QPushButton {
                background-color: #2D2D2D;
                color: #EEEEEE;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #3D3D3D;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
            QPushButton:disabled {
                background-color: #1E1E1E;
                color: #666666;
            }
        """)
    
    def update_gpu_widgets(self):
        # 기존 GPU 위젯 제거
        for i in reversed(range(self.gpu_layout.count())): 
            item = self.gpu_layout.itemAt(i)
            if item.layout():
                self.gpu_layout.removeItem(item)
        
        # GPU 없는 경우
        gpus = GPUtil.getGPUs()
        if not gpus:
            no_gpu_label = QLabel("GPU를 찾을 수 없습니다.")
            self.gpu_layout.addWidget(no_gpu_label)
            return
        
        # GPU 정보 위젯 생성
        self.gpus = {}
        for gpu in gpus:
            gpu_id = gpu.id
            self.gpus[gpu_id] = {}
            
            # GPU 이름 및 ID
            gpu_header = QLabel(f"GPU {gpu_id}: {gpu.name}")
            gpu_header.setFont(QFont("Arial", 10, QFont.Bold))
            self.gpu_layout.addWidget(gpu_header)
            
            # GPU 사용량
            usage_layout = QHBoxLayout()
            usage_label = QLabel("사용량:")
            usage_progress = QProgressBar()
            usage_progress.setRange(0, 100)
            usage_value = QLabel("0%")
            
            usage_layout.addWidget(usage_label)
            usage_layout.addWidget(usage_progress)
            usage_layout.addWidget(usage_value)
            
            self.gpus[gpu_id]["usage"] = {
                "layout": usage_layout,
                "progress": usage_progress,
                "value": usage_value
            }
            self.gpu_layout.addLayout(usage_layout)
            
            # GPU 메모리
            memory_layout = QHBoxLayout()
            memory_label = QLabel("메모리:")
            memory_progress = QProgressBar()
            memory_progress.setRange(0, 100)
            memory_value = QLabel("0/0 MB (0%)")
            
            memory_layout.addWidget(memory_label)
            memory_layout.addWidget(memory_progress)
            memory_layout.addWidget(memory_value)
            
            self.gpus[gpu_id]["memory"] = {
                "layout": memory_layout,
                "progress": memory_progress,
                "value": memory_value
            }
            self.gpu_layout.addLayout(memory_layout)
            
            # GPU 온도
            temp_layout = QHBoxLayout()
            temp_label = QLabel("온도:")
            temp_progress = QProgressBar()
            temp_progress.setRange(0, 100)
            temp_value = QLabel("0°C")
            
            temp_layout.addWidget(temp_label)
            temp_layout.addWidget(temp_progress)
            temp_layout.addWidget(temp_value)
            
            self.gpus[gpu_id]["temp"] = {
                "layout": temp_layout,
                "progress": temp_progress,
                "value": temp_value
            }
            self.gpu_layout.addLayout(temp_layout)
    
    def update_stats(self):
        # CPU 업데이트
        cpu_percent = psutil.cpu_percent()
        self.cpu_total_progress.setValue(int(cpu_percent))
        self.cpu_total_value.setText(f"{cpu_percent:.1f}%")
        
        # 프로그레스바 색상 동적 변경
        self.update_progress_color(self.cpu_total_progress, cpu_percent)
        
        # CPU 코어 업데이트
        if self.show_cores_checkbox.isChecked():
            per_cpu = psutil.cpu_percent(percpu=True)
            for i, percent in enumerate(per_cpu):
                if i in self.cpu_cores:
                    self.cpu_cores[i]["progress"].setValue(int(percent))
                    self.cpu_cores[i]["value"].setText(f"{percent:.1f}%")
                    self.update_progress_color(self.cpu_cores[i]["progress"], percent)
        
        # RAM 업데이트
        ram = psutil.virtual_memory()
        ram_percent = ram.percent
        ram_used = ram.used / (1024**3)
        ram_total = ram.total / (1024**3)
        
        self.ram_progress.setValue(int(ram_percent))
        self.ram_value.setText(f"{ram_used:.2f}/{ram_total:.2f} GB ({ram_percent:.1f}%)")
        self.update_progress_color(self.ram_progress, ram_percent)
        
        # GPU 업데이트
        try:
            gpus = GPUtil.getGPUs()
            for gpu in gpus:
                gpu_id = gpu.id
                if gpu_id in self.gpus:
                    # GPU 사용량
                    gpu_load = gpu.load * 100
                    self.gpus[gpu_id]["usage"]["progress"].setValue(int(gpu_load))
                    self.gpus[gpu_id]["usage"]["value"].setText(f"{gpu_load:.1f}%")
                    self.update_progress_color(self.gpus[gpu_id]["usage"]["progress"], gpu_load)
                    
                    # GPU 메모리
                    mem_used = gpu.memoryUsed
                    mem_total = gpu.memoryTotal
                    mem_percent = (mem_used / mem_total * 100) if mem_total > 0 else 0
                    
                    self.gpus[gpu_id]["memory"]["progress"].setValue(int(mem_percent))
                    self.gpus[gpu_id]["memory"]["value"].setText(
                        f"{mem_used:.0f}/{mem_total:.0f} MB ({mem_percent:.1f}%)")
                    self.update_progress_color(self.gpus[gpu_id]["memory"]["progress"], mem_percent)
                    
                    # GPU 온도
                    temp = gpu.temperature
                    temp_percent = min(100, (temp / 100) * 100)  # 온도를 0-100 스케일로 변환
                    
                    self.gpus[gpu_id]["temp"]["progress"].setValue(int(temp_percent))
                    self.gpus[gpu_id]["temp"]["value"].setText(f"{temp:.1f}°C")
                    self.update_progress_color(self.gpus[gpu_id]["temp"]["progress"], temp_percent)
        except Exception as e:
            print(f"GPU 정보 업데이트 오류: {e}")
    
    def update_progress_color(self, progress_bar, value):
        """값에 따라 프로그레스바 색상 변경"""
        style = ""
        if value < 60:
            style = "QProgressBar::chunk { background-color: #4CAF50; }"  # 녹색
        elif value < 80:
            style = "QProgressBar::chunk { background-color: #FF9800; }"  # 주황색
        else:
            style = "QProgressBar::chunk { background-color: #F44336; }"  # 빨간색
        
        progress_bar.setStyleSheet(style)
    
    def update_refresh_rate(self):
        """갱신 주기 업데이트"""
        is_running = self.timer.isActive()
        self.timer.stop()
        refresh_seconds = self.refresh_spinbox.value()
        if is_running:
            self.timer.start(refresh_seconds * 1000)
    
    def toggle_cpu_cores(self, state):
        """CPU 코어 표시 여부 토글"""
        for i in self.cpu_cores:
            for widget in [self.cpu_cores[i]["layout"].itemAt(j).widget() for j in range(self.cpu_cores[i]["layout"].count())]:
                if widget:
                    widget.setVisible(state == Qt.Checked)
    
    def start_monitoring(self):
        """모니터링 시작"""
        refresh_seconds = self.refresh_spinbox.value()
        self.timer.start(refresh_seconds * 1000)
        self.run_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("상태: 실행 중")
        self.update_stats()  # 즉시 첫 업데이트 수행
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.timer.stop()
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("상태: 중지됨")