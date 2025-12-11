import time
import random
from typing import Dict, Any, List

from core.database import db_manager
from core.gamification import gamification_engine

class BatchExporter:
    
    DIFFICULTY_OPTIONS = ['Легкий', 'Средний', 'Сложный', 'Эпический']
    QUEST_TEMPLATES = [
        "Поиск Древнего Артефакта",
        "Спасение Принцессы из Башни",
        "Охота на Гигантского Тролля",
        "Доставка Секретного Письма",
        "Зачистка Заброшенной Шахты",
        "Сбор Редких Трав",
        "Расследование Странных Событий",
    ]
    
    @staticmethod
    def generate_random_quest_data(index: int) -> Dict[str, Any]:
        
        title = f"{random.choice(BatchExporter.QUEST_TEMPLATES)} - Генерация {index:03d}"
        
        difficulty = random.choice(BatchExporter.DIFFICULTY_OPTIONS)
        reward = random.randint(10, 500)
        description = f"Сгенерированное описание для квеста '{title}'. Вам предстоит отправиться в {random.choice(['Дремучий Лес', 'Высокие Горы', 'Забытый Храм'])} и выполнить сложное задание."
        deadline_days = random.randint(1, 30)
        
        from datetime import datetime, timedelta
        deadline = (datetime.now() + timedelta(days=deadline_days)).strftime("%Y-%m-%dT%H:%M:%S")

        return {
            'title': title,
            'difficulty': difficulty,
            'reward': reward,
            'description': description,
            'deadline': deadline,
        }

    @staticmethod
    def generate_100_quests() -> float:
        db = db_manager 
        start_time = time.time()
        
        created_count = 0
        total_quests_to_generate = 100
        
        print("\n🔥 Начинаем БОСС-ФАЙТ: Генерация 100 квестов...")

        for i in range(1, total_quests_to_generate + 1):
            data = BatchExporter.generate_random_quest_data(i)
            
            try:
                quest_id = db.create_quest(data)
                
                if quest_id != -1:
                    created_count += 1
                else:
                    pass
                    
            except Exception as e:
                print(f"❌ Критическая ошибка при генерации квеста {i}: {e}. Операция прервана.")
                break

        elapsed_time = time.time() - start_time
        
        gamification_engine.grant_xp("BOSS_FIGHT") 
        gamification_engine.check_achievements(created_count, elapsed_time)
        
        print("\n✅ БОСС-ФАЙТ ЗАВЕРШЕН!")
        print(f"Создано квестов: {created_count} из {total_quests_to_generate}")
        print(f"⏳ Время генерации: {elapsed_time:.2f} секунд.")
        
        return elapsed_time
        
batch_exporter = BatchExporter()
