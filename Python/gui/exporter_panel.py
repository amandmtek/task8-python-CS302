import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
    QPushButton, QFileDialog, QMessageBox, QLabel
)
from PyQt6.QtCore import pyqtSignal
from core.template_engine import template_engine
from core.gamification import gamification_engine
from typing import Dict, Any

class ExporterPanel(QWidget):
    
    request_quest_data = pyqtSignal()
    
    current_quest_data: Dict[str, Any] = {}
    
    TEMPLATES = {
        "Royal (Королевский)": "royal.html",
        "Guild (Гильдия)": "guild.html",
        "Ancient (Древний)": "ancient.html",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        main_layout.addWidget(QLabel("📜 **Настройки Экспорта Пергамента**"))

        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("Шаблон:"))
        
        self.template_combo = QComboBox()
        self.template_combo.addItems(self.TEMPLATES.keys())
        template_layout.addWidget(self.template_combo)
        
        main_layout.addLayout(template_layout)

        button_layout = QHBoxLayout()
        
        self.pdf_button = QPushButton("Экспорт в PDF (Weasyprint)")
        self.pdf_button.clicked.connect(lambda: self.export_quest('pdf'))
        
        self.docx_button = QPushButton("Экспорт в DOCX")
        self.docx_button.clicked.connect(lambda: self.export_quest('docx'))
        
        button_layout.addWidget(self.pdf_button)
        button_layout.addWidget(self.docx_button)
        
        main_layout.addLayout(button_layout)
        
        self.setMaximumHeight(main_layout.sizeHint().height())

    def set_quest_data(self, data: Dict[str, Any]):
        self.current_quest_data = data
        self.pdf_button.setEnabled(data.get('id') is not None)
        self.docx_button.setEnabled(data.get('id') is not None)

    def export_quest(self, format: str):
        
        self.request_quest_data.emit() 
        
        if not self.current_quest_data.get('title'):
            QMessageBox.warning(self, "Ошибка Экспорта", "Невозможно экспортировать: квест должен иметь название и быть сохранен.")
            return
            
        quest_id = self.current_quest_data.get('id', 'temp')
        template_key = self.template_combo.currentText()
        template_name = self.TEMPLATES[template_key]
        
        file_extension = "pdf" if format == 'pdf' else "docx"
        default_name = f"{self.current_quest_data['title'].replace(' ', '_')}_{quest_id}.{file_extension}"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            f"Сохранить {file_extension.upper()} Пергамент", 
            default_name, 
            f"{file_extension.upper()} (*.{file_extension})"
        )
        
        if not file_path:
            return

        try:
            from core.gamification import gamification_engine
            
            if format == 'pdf':
                template_engine.export_pdf(template_name, self.current_quest_data, file_path)
                gamification_engine.grant_xp("EXPORT_PDF")
            elif format == 'docx':
                template_engine.export_docx(self.current_quest_data, file_path)
                gamification_engine.grant_xp("EXPORT_DOCX")

            QMessageBox.information(
                self, 
                "Успешный Экспорт", 
                f"✅ Пергамент в формате {file_extension.upper()} создан и сохранен в:\n{file_path}", 
                QMessageBox.StandardButton.Ok
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Критическая Ошибка Экспорта", f"Произошла ошибка при экспорте: {e}")
