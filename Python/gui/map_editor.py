import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene, 
    QPushButton, QToolBar, QSizePolicy, QLineEdit, QFileDialog, 
    QMessageBox, QInputDialog
)
from PyQt6.QtGui import QColor, QBrush, QPen, QFont, QFontDatabase, QPixmap, QImage, QPainter
from PyQt6.QtCore import Qt, QPointF
from core.gamification import gamification_engine

class MapEditor(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_quest_id = -1
        self.current_tool = "path" 
        self.last_point = None
        self.background_item = None
        
        self.setup_font()
        self.setup_ui()
        
    def setup_font(self):
        font_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonts', 'Uncial_Antiqua.ttf')
        if os.path.exists(font_path):
            QFontDatabase.addApplicationFont(font_path)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        toolbar = QToolBar()
        self.path_btn = QPushButton("Путь 🖋️")
        self.city_btn = QPushButton("Город 🟢")
        self.lair_btn = QPushButton("Логово 🔴")
        self.tavern_btn = QPushButton("Таверна 🟡")
        self.text_btn = QPushButton("Текст 📝")
        self.erase_btn = QPushButton("Ластик 🗑️")
        self.save_btn = QPushButton("💾 Сохранить")
        self.load_bg_btn = QPushButton("🖼️ Фон")
        
        for btn in [self.path_btn, self.city_btn, self.lair_btn, self.tavern_btn, self.text_btn, self.erase_btn]:
            toolbar.addWidget(btn)
        toolbar.addSeparator()
        toolbar.addWidget(self.load_bg_btn)
        toolbar.addWidget(self.save_btn)
        
        main_layout.addWidget(toolbar)

        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 800, 600)
        self.scene.setBackgroundBrush(QBrush(QColor('#f4e4bc'))) 
        
        self.view = QGraphicsView(self.scene)
        self.view.setFixedSize(800, 600)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        main_layout.addWidget(self.view)
        
        self.path_btn.clicked.connect(lambda: self._set_tool("path"))
        self.city_btn.clicked.connect(lambda: self._set_tool("city"))
        self.lair_btn.clicked.connect(lambda: self._set_tool("lair"))
        self.tavern_btn.clicked.connect(lambda: self._set_tool("tavern"))
        self.text_btn.clicked.connect(lambda: self._set_tool("text"))
        self.erase_btn.clicked.connect(lambda: self._set_tool("erase"))
        self.save_btn.clicked.connect(self._save_map)
        self.load_bg_btn.clicked.connect(self._load_background)

        self.view.mousePressEvent = self._mouse_press_event
        self.view.mouseMoveEvent = self._mouse_move_event
        self.view.mouseReleaseEvent = self._mouse_release_event
        
        self._update_cursor()

    def _set_tool(self, tool_name: str):
        self.current_tool = tool_name
        self.last_point = None
        self._update_cursor()
        print(f"Выбран инструмент: {tool_name}")
        
    def _update_cursor(self):
        if self.current_tool == "erase":
            self.view.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.view.setCursor(Qt.CursorShape.ArrowCursor)

    def _mouse_press_event(self, event):
        scene_pos = self.view.mapToScene(event.pos())
        
        if not (0 <= scene_pos.x() <= 800 and 0 <= scene_pos.y() <= 600):
            return

        if event.button() == Qt.MouseButton.LeftButton:
            
            if self.current_tool == "path":
                self.last_point = scene_pos
                
            elif self.current_tool in ("city", "lair", "tavern"):
                color_map = {"city": Qt.GlobalColor.green, "lair": Qt.GlobalColor.red, "tavern": Qt.GlobalColor.yellow}
                brush_color = color_map.get(self.current_tool)
                
                item = self.scene.addEllipse(scene_pos.x()-5, scene_pos.y()-5, 10, 10, QPen(Qt.GlobalColor.black), QBrush(brush_color))
                item.setZValue(10)
                
                label = self.scene.addText(self.current_tool.capitalize())
                label.setPos(scene_pos.x() + 10, scene_pos.y() - 10)
                label.setFont(QFont("Uncial Antiqua", 10))
                label.setZValue(10)
                
            elif self.current_tool == "text":
                text, ok = QInputDialog.getText(self, "Текст", "Введите текст метки:")
                if ok and text:
                    item = self.scene.addText(text)
                    item.setPos(scene_pos)
                    item.setFont(QFont("Uncial Antiqua", 12))
                    item.setZValue(10)
                    
            elif self.current_tool == "erase":
                items = self.scene.items(scene_pos)
                for item in items:
                    if item != self.background_item and item.zValue() > -100:
                        self.scene.removeItem(item)
                        break
                        
        QGraphicsView.mousePressEvent(self.view, event)

    def _mouse_move_event(self, event):
        if self.current_tool == "path" and self.last_point and (event.buttons() & Qt.MouseButton.LeftButton):
            scene_pos = self.view.mapToScene(event.pos())
            
            pen = QPen(QColor('#795548'), 3)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            
            line = self.scene.addLine(self.last_point.x(), self.last_point.y(), scene_pos.x(), scene_pos.y(), pen)
            line.setZValue(0)
            
            self.last_point = scene_pos
        
        QGraphicsView.mouseMoveEvent(self.view, event)

    def _mouse_release_event(self, event):
        if self.current_tool == "path":
            self.last_point = None
            
        QGraphicsView.mouseReleaseEvent(self.view, event)


    def _save_map(self):
        
        image = QImage(800, 600, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(image)
        self.scene.render(painter)
        painter.end()
        
        default_name = f"map_{self.current_quest_id}_{datetime.now().strftime('%H%M%S')}.png"
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить карту", default_name, "PNG (*.png)")
        
        if path:
            image.save(path)
            gamification_engine.grant_xp("SAVE_MAP")
            QMessageBox.information(self, "Успех", f"Карта сохранена!")

    def _load_background(self):
        path, _ = QFileDialog.getOpenFileName(self, "Загрузить фон", "", "Изображения (*.png *.jpg)")
        if path:
            pixmap = QPixmap(path)
            if self.background_item:
                self.scene.removeItem(self.background_item)
                
            self.background_item = self.scene.addPixmap(pixmap.scaled(800, 600, Qt.AspectRatioMode.IgnoreAspectRatio))
            self.background_item.setPos(0, 0)
            self.background_item.setZValue(-100)
            self.scene.setBackgroundBrush(Qt.GlobalColor.transparent)
