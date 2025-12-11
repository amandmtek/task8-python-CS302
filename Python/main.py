import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, 
    QVBoxLayout, QPushButton, QMessageBox
)

from gui.quest_wizard import QuestWizard
from gui.map_editor import MapEditor
from gui.gamification_panel import GamificationPanel
from core.database import db_manager 
from core.template_engine import template_engine
from core.gamification import gamification_engine
from core.batch_exporter import BatchExporter 

class QuestMasterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quest Master (Гильдия Приключенцев) ✨")
        self.setGeometry(100, 100, 1000, 800)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget) 
        
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget) 
        
        self.quest_wizard = QuestWizard()
        self.map_editor = MapEditor()
        self.gamification_panel = GamificationPanel() 
        
        self.tab_widget.addTab(self.quest_wizard, "🧙‍♂️ Генератор Квестов")
        self.tab_widget.addTab(self.map_editor, "🗺️ Редактор Карт")
        
        self.main_layout.addWidget(self.gamification_panel)

        self.boss_fight_button = QPushButton("⚔️ Запустить Босс-Файт (100 квестов)")
        self.boss_fight_button.clicked.connect(self._run_boss_fight)
        self.main_layout.addWidget(self.boss_fight_button)
        
        self.quest_wizard.quest_saved.connect(self._handle_quest_update)

    def _run_boss_fight(self):
        self.boss_fight_button.setEnabled(False)
        
        BatchExporter.generate_100_quests()
        
        if hasattr(self, 'gamification_panel'):
            self.gamification_panel.update_ui()

        self.boss_fight_button.setEnabled(True)
        QMessageBox.information(self, "Босс-Файт", "⚔️ Тест на 100 квестов завершен! Проверьте консоль и достижения.")

    def _handle_quest_update(self, quest_id: int):
        
        if quest_id != -1:
            gamification_engine.grant_xp("CREATE_QUEST")
            
        self.map_editor.current_quest_id = quest_id
        
        self.gamification_panel.update_ui()
        print(f"Главное окно: Квест ID {quest_id} сохранен/обновлен. XP обновлен.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    db_manager._init_db() 
    
    window = QuestMasterApp()
    window.show()
    sys.exit(app.exec())
