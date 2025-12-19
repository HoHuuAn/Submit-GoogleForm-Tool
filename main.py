import sys
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QSpinBox, QProgressBar, QMessageBox,
    QFrame, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QIcon, QPainter, QColor
import requests
from faker import Faker
from form import parse_form_entries

fake = Faker('vi_VN')


class ToggleSwitch(QCheckBox):
    """Custom toggle switch widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 24)
        self.setCursor(Qt.PointingHandCursor)
        self._circle_position = 3
        self.animation = QPropertyAnimation(self, b"circle_position", self)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.animation.setDuration(200)

        # Connect state change to animation
        self.stateChanged.connect(self.setup_animation)

    def setup_animation(self, value):
        self.animation.stop()
        if value:
            self.animation.setEndValue(27)
        else:
            self.animation.setEndValue(3)
        self.animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw background
        if self.isChecked():
            painter.setBrush(QColor("#4CAF50"))
        else:
            painter.setBrush(QColor("#ccc"))

        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, 50, 24, 12, 12)

        # Draw circle
        painter.setBrush(QColor("#fff"))
        painter.drawEllipse(int(self._circle_position), 3, 18, 18)

    def hitButton(self, pos):
        """Override to make the entire widget clickable"""
        return self.contentsRect().contains(pos)

    def mouseReleaseEvent(self, event):
        """Handle mouse release to toggle state"""
        if event.button() == Qt.LeftButton:
            self.setChecked(not self.isChecked())
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def get_circle_position(self):
        return self._circle_position

    def set_circle_position(self, pos):
        self._circle_position = pos
        self.update()

    circle_position = pyqtProperty(
        int, get_circle_position, set_circle_position)


class ScanWorker(QThread):
    finished = pyqtSignal(list)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        entries = parse_form_entries(self.url)
        self.finished.emit(entries)


class SubmitWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, url, data_list):
        super().__init__()
        self.url = url
        self.data_list = data_list

    def run(self):
        for i, data in enumerate(self.data_list):
            try:
                res = requests.post(self.url, data=data, timeout=5)
                if res.status_code != 200:
                    raise Exception(f"Status {res.status_code}")
            except Exception as e:
                self.finished.emit(f"Error at submission {i+1}: {e}")
                return
            self.progress.emit(i + 1)
        self.finished.emit("All submissions successful!")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Google Form Auto Submit Tool")
        self.setWindowIcon(QIcon('icon.ico'))
        self.setGeometry(100, 100, 1000, 700)

        # Set style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            QSpinBox {
                padding: 6px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
                min-width: 80px;
            }
            QCheckBox {
                font-size: 14px;
                spacing: 8px;
            }
            ToggleSwitch {
                border: none;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 4px;
                text-align: center;
                height: 28px;
                font-size: 13px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)

        # Layout chính
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Input URL - với styling đẹp hơn
        url_frame = QFrame()
        url_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        url_layout = QHBoxLayout()
        url_layout.setSpacing(10)

        url_label = QLabel("Form URL:")
        url_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        url_layout.addWidget(url_label)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Nhập link Google Form tại đây...")
        url_layout.addWidget(self.url_input)

        self.scan_btn = QPushButton("Scan Form")
        self.scan_btn.setFixedWidth(120)
        self.scan_btn.clicked.connect(self.scan_form)
        url_layout.addWidget(self.scan_btn)

        url_frame.setLayout(url_layout)
        layout.addWidget(url_frame)

        # Loading label
        self.loading_label = QLabel("⏳ Scanning form... Please wait.")
        self.loading_label.setStyleSheet(
            "color: #2196F3; font-weight: bold; font-size: 14px; padding: 5px;")
        self.loading_label.hide()
        layout.addWidget(self.loading_label)

        # Label cho danh sách câu hỏi
        questions_label = QLabel("📋 Danh sách câu hỏi và tỷ lệ (%):")
        questions_label.setStyleSheet(
            "font-weight: bold; font-size: 15px; color: #2196F3; padding: 5px 0px;")
        layout.addWidget(questions_label)

        # Danh sách câu hỏi với scroll
        self.questions_list = QListWidget()
        self.questions_list.setSpacing(5)
        layout.addWidget(self.questions_list)

        # Control panel với styling
        control_frame = QFrame()
        control_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        control_layout = QHBoxLayout()
        control_layout.setSpacing(15)

        submit_label = QLabel("Số lần gửi:")
        submit_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        control_layout.addWidget(submit_label)

        self.num_submissions = QSpinBox()
        self.num_submissions.setRange(1, 10000)
        self.num_submissions.setValue(100)
        self.num_submissions.setFixedWidth(100)
        control_layout.addWidget(self.num_submissions)

        control_layout.addStretch()

        self.submit_btn = QPushButton("🚀 Gửi (Chạy)")
        self.submit_btn.setFixedWidth(160)
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                font-size: 14px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.submit_btn.clicked.connect(self.start_submit)
        self.submit_btn.setEnabled(False)
        control_layout.addWidget(self.submit_btn)

        control_frame.setLayout(control_layout)
        layout.addWidget(control_frame)

        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Set central widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.entries = []  # Lưu entries từ scan
        self.option_widgets = {}  # Lưu spinbox cho % của mỗi option
        self.checkbox_widgets = {}  # Lưu checkbox cho mỗi option

    def scan_form(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a URL")
            return

        # Start loading
        self.scan_btn.setEnabled(False)
        self.loading_label.show()

        # Start worker
        self.scan_worker = ScanWorker(url)
        self.scan_worker.finished.connect(self.on_scan_finished)
        self.scan_worker.start()

    def on_scan_finished(self, entries):
        # Stop loading
        self.loading_label.hide()
        self.scan_btn.setEnabled(True)

        if not entries:
            QMessageBox.warning(self, "Error", "Could not parse form")
            return

        self.entries = entries
        self.questions_list.clear()
        self.option_widgets.clear()
        self.checkbox_widgets.clear()

        for entry in self.entries:
            if entry['id'] == 'pageHistory' or entry['id'] == 'emailAddress':
                continue  # Skip pageHistory and emailAddress

            # Tạo widget container cho mỗi câu hỏi
            question_widget = QWidget()
            question_layout = QVBoxLayout()
            question_layout.setContentsMargins(12, 8, 12, 8)
            question_layout.setSpacing(5)

            # Set background màu xen kẽ cho đẹp
            question_widget.setStyleSheet("""
                QWidget {
                    background-color: #fafafa;
                    border-radius: 6px;
                    border: 1px solid #e0e0e0;
                }
            """)

            # Tiêu đề câu hỏi - bold và rõ ràng
            question_title = QLabel(f"❓ {entry['container_name']}")
            question_title.setStyleSheet("""
                font-weight: bold; 
                font-size: 14px; 
                color: #1976D2;
                background-color: transparent;
                border: none;
                padding: 3px 0px;
            """)
            question_title.setWordWrap(True)
            question_layout.addWidget(question_title)

            # Layout cho options
            if entry['options']:
                self.option_widgets[entry['id']] = {}
                self.checkbox_widgets[entry['id']] = {}
                options = [opt for opt in entry['options']
                           if opt != 'ANY TEXT!!']

                for opt in options:
                    opt_layout = QHBoxLayout()
                    opt_layout.setSpacing(10)

                    # Toggle switch cho option
                    toggle = ToggleSwitch()
                    toggle.setChecked(True)
                    toggle.stateChanged.connect(
                        lambda state, eid=entry['id']: self.recalculate_percentages(eid))
                    opt_layout.addWidget(toggle)

                    # Label cho option với word wrap
                    opt_label = QLabel(opt)
                    opt_label.setStyleSheet("""
                        font-size: 13px; 
                        color: #555;
                        background-color: transparent;
                        border: none;
                        padding: 2px 0px;
                    """)
                    opt_label.setWordWrap(True)
                    opt_layout.addWidget(opt_label, stretch=1)

                    # Spinbox cho %
                    spin = QSpinBox()
                    spin.setRange(0, 100)
                    spin.setSuffix(" %")
                    spin.setValue(100 // len(options))  # Chia đều %
                    spin.setFixedWidth(90)
                    spin.setStyleSheet("""
                        QSpinBox {
                            background-color: white;
                            border: 1px solid #bbb;
                            border-radius: 4px;
                            padding: 5px;
                            font-size: 13px;
                        }
                    """)
                    opt_layout.addWidget(spin)

                    question_layout.addLayout(opt_layout)
                    self.option_widgets[entry['id']][opt] = spin
                    self.checkbox_widgets[entry['id']][opt] = toggle
            else:
                # Text field info
                text_info = QLabel(
                    "📝 Trường nhập text (sẽ tự động tạo dữ liệu giả)")
                text_info.setStyleSheet("""
                    font-size: 13px; 
                    color: #777; 
                    font-style: italic;
                    background-color: transparent;
                    border: none;
                    padding: 3px 0px;
                """)
                question_layout.addWidget(text_info)

            question_widget.setLayout(question_layout)

            # Tạo QListWidgetItem và set widget
            item = QListWidgetItem(self.questions_list)
            item.setSizeHint(question_widget.sizeHint())
            self.questions_list.addItem(item)
            self.questions_list.setItemWidget(item, question_widget)

        self.submit_btn.setEnabled(True)

    def recalculate_percentages(self, entry_id):
        """Recalculate percentages for checked options when a checkbox is toggled"""
        if entry_id not in self.checkbox_widgets or entry_id not in self.option_widgets:
            return

        # Get all checked options
        checked_options = [opt for opt, checkbox in self.checkbox_widgets[entry_id].items()
                           if checkbox.isChecked()]

        if not checked_options:
            return

        # Calculate equal percentage for checked options
        equal_percentage = 100 // len(checked_options)
        remainder = 100 % len(checked_options)

        # Set percentages
        for i, opt in enumerate(checked_options):
            percentage = equal_percentage + (1 if i < remainder else 0)
            self.option_widgets[entry_id][opt].setValue(percentage)

        # Set 0% for unchecked options
        for opt, checkbox in self.checkbox_widgets[entry_id].items():
            if not checkbox.isChecked():
                self.option_widgets[entry_id][opt].setValue(0)

    def start_submit(self):
        if not self.entries:
            return

        num = self.num_submissions.value()
        data_list = []

        for _ in range(num):
            data = {}
            for entry in self.entries:
                key = f"entry.{entry['id']}" if entry['id'] != 'emailAddress' else 'emailAddress'
                if entry['id'] == 'pageHistory':
                    data[key] = entry.get('default_value', '0,1,2,3')
                elif entry['id'] == 'emailAddress':
                    data[key] = fake.email()
                elif entry['options']:
                    # Random dựa trên % - chỉ chọn từ các option được checked
                    options = [opt for opt in entry['options']
                               if opt != 'ANY TEXT!!']

                    # Lọc chỉ các option được check
                    if entry['id'] in self.checkbox_widgets:
                        checked_options = [opt for opt in options
                                           if self.checkbox_widgets[entry['id']].get(opt, QCheckBox()).isChecked()]
                        if checked_options:
                            options = checked_options

                    weights = [self.option_widgets[entry['id']].get(
                        opt, QSpinBox()).value() for opt in options]
                    if sum(weights) == 0:
                        choice = random.choice(options)
                    else:
                        choice = random.choices(options, weights=weights)[0]
                    data[key] = choice
                else:
                    # Text, generate fake
                    if 'name' in entry['container_name'].lower():
                        data[key] = fake.name()
                    else:
                        data[key] = fake.sentence()
            data_list.append(data)

        # Start worker thread
        self.worker = SubmitWorker(self.url_input.text().replace('/viewform', '/formResponse'), data_list)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_finished)
        self.progress_bar.setMaximum(num)
        self.worker.start()

    def on_finished(self, msg):
        QMessageBox.information(self, "Done", msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
