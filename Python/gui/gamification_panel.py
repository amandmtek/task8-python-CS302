import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QProgressBar, QLabel, QListWidget, 
    QListWidgetItem
)
from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QSoundEffect 
from core.gamification import gamification_engine

class GamificationPanel(QWidget):
    """UI для отображения XP, уровня и достижений."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sound_effect = QSoundEffect()
        self._init_sound()
        self.setup_ui()
        self.update_ui()
        
    def _init_sound(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'sounds', 'level_up.wav')
        if os.path.exists(path):
            self.sound_effect.setSource(QUrl.fromLocalFile(path))
            self.sound_effect.setVolume(0.5)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        main_layout.addWidget(QLabel("🔥 **Статус Мага-Источника**"))
        
        self.level_label = QLabel("Уровень: ...")
        main_layout.addWidget(self.level_label)
        
        self.xp_progress_bar = QProgressBar()
        main_layout.addWidget(self.xp_progress_bar)
        
        main_layout.addWidget(QLabel("\n🏆 **Достижения**"))
        
        self.achievement_list = QListWidget()
        main_layout.addWidget(self.achievement_list)

    def update_ui(self):
        old_level = getattr(self, '_last_level', None)
        
        current_level_name, current_xp, next_xp = gamification_engine.get_level_info()
        self._last_level = current_level_name
        
        self.level_label.setText(f"Уровень: **{current_level_name}** (Всего XP: {current_xp})")
        
        if next_xp == 99999:
            self.xp_progress_bar.setRange(0, 1)
            self.xp_progress_bar.setValue(1)
            self.xp_progress_bar.setFormat("МАКСИМУМ")
        else:
            base_xp = gamification_engine.LEVELS.get(current_level_name, 0)
            self.xp_progress_bar.setRange(0, next_xp - base_xp)
            self.xp_progress_bar.setValue(current_xp - base_xp)
            self.xp_progress_bar.setFormat(f"%v / %m XP")

        self.achievement_list.clear()
        for ach in gamification_engine.achievements:
            self.achievement_list.addItem(f"✅ {ach}")
            
        if old_level and old_level != current_level_name:
            if not self.sound_effect.source().isEmpty():
                self.sound_effect.play()
