import sqlite3
from typing import Dict, Any, List

class DatabaseManager:
    
    DB_NAME = "quest_master.db"

    def __init__(self):
        self._conn = sqlite3.connect(self.DB_NAME)
        self._cursor = self._conn.cursor()
        self._init_db()

    def _init_db(self):
        self._cursor.execute("""
            CREATE TABLE IF NOT EXISTS quests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,  
                difficulty TEXT CHECK(difficulty IN ('Легкий','Средний','Сложный','Эпический')),
                reward INTEGER,
                description TEXT,
                deadline TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        self._cursor.execute("""
            CREATE TABLE IF NOT EXISTS quest_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quest_id INTEGER,
                title TEXT,
                difficulty TEXT,
                reward INTEGER,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (quest_id) REFERENCES quests(id)
            );
        """)
        self._conn.commit()

    def create_quest(self, data: Dict[str, Any]) -> int:
        
        data.pop('id', None) 
        
        keys = ', '.join(data.keys())
        placeholders = ', '.join('?' * len(data))
        values = list(data.values())
        
        try:
            self._cursor.execute(f"INSERT INTO quests ({keys}) VALUES ({placeholders})", values)
            quest_id = self._cursor.lastrowid
            self._conn.commit()
            self._insert_version(quest_id, data)
            return quest_id
        except sqlite3.IntegrityError as e:
            print(f"❌ Ошибка при создании квеста: {e}")
            return -1

    def update_quest(self, quest_id: int, data: Dict[str, Any]):
        data.pop('id', None) 
        
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        values = list(data.values())
        values.append(quest_id)
        
        self._cursor.execute(f"UPDATE quests SET {set_clause} WHERE id = ?", values)
        self._conn.commit()
        self._insert_version(quest_id, data)

    def _insert_version(self, quest_id: int, data: Dict[str, Any]):
        version_data = {k: v for k, v in data.items() if k in ['title', 'difficulty', 'reward', 'description']}
        
        keys = 'quest_id, ' + ', '.join(version_data.keys())
        placeholders = '?, ' + ', '.join('?' * len(version_data))
        values = [quest_id] + list(version_data.values())
        
        self._cursor.execute(f"INSERT INTO quest_versions ({keys}) VALUES ({placeholders})", values)
        self._conn.commit()

    def get_quest(self, quest_id: int) -> Dict[str, Any] | None:
        self._cursor.execute("SELECT * FROM quests WHERE id = ?", (quest_id,))
        row = self._cursor.fetchone()
        if row:
            cols = [col[0] for col in self._cursor.description]
            return dict(zip(cols, row))
        return None
    
    def get_all_quests(self) -> List[Dict[str, Any]]:
        self._cursor.execute("SELECT * FROM quests ORDER BY created_at DESC")
        rows = self._cursor.fetchall()
        cols = [col[0] for col in self._cursor.description]
        return [dict(zip(cols, row)) for row in rows]

db_manager = DatabaseManager()
