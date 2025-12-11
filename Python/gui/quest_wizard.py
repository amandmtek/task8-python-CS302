import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLineEdit, QComboBox, QSpinBox, QTextEdit, QDateTimeEdit, 
    QPushButton, QMessageBox, QLabel, QDialog, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QDateTime, pyqtSignal, QTimer
from PyQt6.QtGui import QKeySequence
from core.database import db_manager

from typing import Any, Dict
from gui.exporter_panel import ExporterPanel 

class QuestWizard(QWidget):
    """Модуль Quest Wizard (Генератор квестов) с автосохранением и валидацией."""

    quest_saved = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_quest_id = -1 
        self._unsaved_changes = {}
        
        self.setup_ui()
        self.setup_connections()
        
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.setInterval(3000)
        self.auto_save_timer.timeout.connect(self._auto_save)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.title_input = QLineEdit()
        self.title_input.setMaxLength(50)
        self.title_input.setPlaceholderText("Например: Спасти рядового Райана")
        form_layout.addRow("📜 Название квеста:", self.title_input)

        self.difficulty_input = QComboBox()
        self.difficulty_input.addItems(["Легкий", "Средний", "Сложный", "Эпический"])
        form_layout.addRow("✨ Сложность:", self.difficulty_input)

        self.reward_input = QSpinBox()
        self.reward_input.setRange(10, 10000)
        form_layout.addRow("💰 Награда (золото):", self.reward_input)

        self.description_input = QTextEdit()
        self.description_input.setFixedHeight(100)
        self.description_input.setPlaceholderText("Опишите задание подробно...")
        self.char_count_label = QLabel("Символов: 0 (Нужно минимум 50)")
        form_layout.addRow("📝 Описание (мин 50 симв.):", self.description_input)
        form_layout.addRow("", self.char_count_label)
        
        self.deadline_input = QDateTimeEdit()
        self.deadline_input.setCalendarPopup(True)
        self.deadline_input.setDateTime(QDateTime.currentDateTime().addDays(7)) 
        form_layout.addRow("⏳ Дедлайн:", self.deadline_input)

        main_layout.addLayout(form_layout)

        buttons_layout = QHBoxLayout()
        
        self.create_button = QPushButton("✨ Создать (Ctrl+Enter)")
        self.create_button.setShortcut(QKeySequence("Ctrl+Return"))
        
        self.load_button = QPushButton("📂 Список квестов")
        self.load_button.clicked.connect(self.open_quest_list)
        
        buttons_layout.addWidget(self.create_button)
        buttons_layout.addWidget(self.load_button)
        main_layout.addLayout(buttons_layout)

        self.exporter_panel = ExporterPanel() 
        main_layout.addWidget(self.exporter_panel)
        
    def setup_connections(self):
        self.title_input.textChanged.connect(lambda t: self._handle_change('title', t))
        self.difficulty_input.currentTextChanged.connect(lambda t: self._handle_change('difficulty', t))
        self.reward_input.valueChanged.connect(lambda v: self._handle_change('reward', v))
        self.description_input.textChanged.connect(self._update_description)
        self.deadline_input.dateTimeChanged.connect(lambda dt: self._handle_change('deadline', dt.toString(Qt.DateFormat.ISODate)))
        
        self.exporter_panel.request_quest_data.connect(self._handle_export_request)
        self.create_button.clicked.connect(self.try_create_quest)
        self.title_input.textChanged.connect(self._start_auto_save)
            
    def _start_auto_save(self):
        if not self.auto_save_timer.isActive():
            self.auto_save_timer.start()
            
    def _update_description(self):
        text = self.description_input.toPlainText().strip()
        chars = len(text)
        self.char_count_label.setText(f"Символов: {chars}/50")
        
        if chars < 50:
            self.char_count_label.setStyleSheet("color: red;")
        else:
            self.char_count_label.setStyleSheet("color: green;")
        
        self._handle_change('description', text)

    def _handle_export_request(self):
        quest_data = self._collect_quest_data()
        self.exporter_panel.set_quest_data(quest_data)

    def _collect_quest_data(self) -> Dict[str, Any]:
        data = {
            'id': self.current_quest_id, 
            'title': self.title_input.text(),
            'difficulty': self.difficulty_input.currentText(),
            'reward': self.reward_input.value(),
            'description': self.description_input.toPlainText(),
            'deadline': self.deadline_input.dateTime().toString(Qt.DateFormat.ISODate),
        }
        return data

    def _handle_change(self, field_name: str, value: Any):
        if getattr(self, '_loading_data', False):
            return

        if self.current_quest_id == -1 and field_name == 'title' and len(str(value)) > 0:
            data = self._collect_quest_data()
            if 'id' in data: del data['id'] 
            
            self.current_quest_id = db_manager.create_quest(data)
            
            if self.current_quest_id != -1:
                print(f"✅ Черновик создан ID: {self.current_quest_id}")
                self.quest_saved.emit(self.current_quest_id)
                self.exporter_panel.set_quest_data(self._collect_quest_data())
            return
            
        if self.current_quest_id != -1:
            self._unsaved_changes[field_name] = value

    def _auto_save(self):
        if self._unsaved_changes and self.current_quest_id != -1:
            db_manager.update_quest(self.current_quest_id, self._unsaved_changes)
            print(f"💾 Автосохранение: {list(self._unsaved_changes.keys())}")
            self._unsaved_changes.clear()
            self.quest_saved.emit(self.current_quest_id)

    def open_quest_list(self):
        """Открывает диалог со списком квестов."""
        quests = db_manager.get_all_quests()
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Архив Гильдии")
        dialog.setMinimumSize(400, 500)
        layout = QVBoxLayout(dialog)
        
        list_widget = QListWidget()
        for q in quests:
            item_text = f"#{q['id']} - {q['title']} ({q['difficulty']})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, q['id']) 
            list_widget.addItem(item)
            
        layout.addWidget(list_widget)
        
        load_btn = QPushButton("Загрузить")
        load_btn.clicked.connect(dialog.accept)
        layout.addWidget(load_btn)
        
        if dialog.exec() and list_widget.currentItem():
            quest_id = list_widget.currentItem().data(Qt.ItemDataRole.UserRole)
            self.load_quest(quest_id)

    def load_quest(self, quest_id: int):
        """Загружает данные квеста в форму."""
        data = db_manager.get_quest(quest_id)
        if not data: return
        
        self._loading_data = True         
        self.current_quest_id = data['id']
        self.title_input.setText(data['title'])
        self.difficulty_input.setCurrentText(data['difficulty'])
        self.reward_input.setValue(data['reward'])
        self.description_input.setText(data['description'])
        
       
        if data['deadline']:
             dt = QDateTime.fromString(data['deadline'], Qt.DateFormat.ISODate)
             self.deadline_input.setDateTime(dt)
             
        self._loading_data = False
        self._unsaved_changes.clear()
        
        self.quest_saved.emit(self.current_quest_id)
        self.exporter_panel.set_quest_data(self._collect_quest_data())
        
        QMessageBox.information(self, "Загружено", f"Квест #{quest_id} загружен!")

    def _validate_fields(self) -> bool:
        is_valid = True
        title_ok = len(self.title_input.text().strip()) > 0
        self._set_field_style(self.title_input, title_ok)
        if not title_ok: is_valid = False
        
        desc_ok = len(self.description_input.toPlainText().strip()) >= 50
        self._set_field_style(self.description_input, desc_ok)
        if not desc_ok: is_valid = False
        return is_valid

    def _set_field_style(self, widget: QWidget, is_valid: bool):
        if is_valid: widget.setStyleSheet("")
        else: widget.setStyleSheet("border: 2px solid red;")

    def try_create_quest(self):
        if not self._validate_fields():
            QMessageBox.warning(self, "Ошибка", "Заполните название и описание (мин. 50 символов)!", QMessageBox.StandardButton.Ok)
            return

        self._auto_save() 
        if self.current_quest_id == -1:
             data = self._collect_quest_data()
             if 'id' in data: del data['id']
             self.current_quest_id = db_manager.create_quest(data)
             self.quest_saved.emit(self.current_quest_id)

        QMessageBox.information(self, "Успех", f"✅ Квест '{self.title_input.text()}' создан!", QMessageBox.StandardButton.Ok)
        self.clear_form()

    def clear_form(self):
        self.current_quest_id = -1
        self._unsaved_changes.clear()
        self.auto_save_timer.stop()
        
        self.title_input.clear()
        self.difficulty_input.setCurrentIndex(0)
        self.reward_input.setValue(10)
        self.description_input.clear()
        self.deadline_input.setDateTime(QDateTime.currentDateTime().addDays(7))
        self.title_input.setStyleSheet("")
        self.description_input.setStyleSheet("")
