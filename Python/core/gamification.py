from typing import Dict, Tuple

class GamificationEngine:
    
    LEVELS: Dict[str, int] = {
        "Ученик": 0,
        "Мастер пергаментов": 50,
        "Архимаг документов": 100
    }
    
    XP_MAP: Dict[str, int] = {
        "CREATE_QUEST": 3,
        "EXPORT_PDF": 2,
        "EXPORT_DOCX": 2,
        "SAVE_MAP": 5,
        "BOSS_FIGHT": 20
    }

    def __init__(self):
        self.current_xp: int = 0
        self.achievements: set[str] = set()

    def get_level_info(self) -> Tuple[str, int, int]:
        
        sorted_levels = sorted(self.LEVELS.items(), key=lambda item: item[1], reverse=True)
        
        current_level_name = "Новичок"
        xp_of_current_level = 0
        
        for name, xp_required in sorted_levels:
            if self.current_xp >= xp_required:
                current_level_name = name
                xp_of_current_level = xp_required
                break
                
        is_max_level = True
        next_xp_required = 99999
        for name, xp_required in sorted_levels:
             if xp_required > self.current_xp:
                 is_max_level = False
                 if xp_required < next_xp_required:
                     next_xp_required = xp_required
        
        xp_to_go = next_xp_required - self.current_xp if not is_max_level else 0

        return current_level_name, self.current_xp, next_xp_required

    def grant_xp(self, action_key: str):
        xp_gained = self.XP_MAP.get(action_key, 0)
        
        if xp_gained > 0:
            old_level_name, _, _ = self.get_level_info()
            self.current_xp += xp_gained
            new_level_name, _, _ = self.get_level_info()
            
            print(f"🎉 Получено {xp_gained} XP за '{action_key}'. Всего XP: {self.current_xp}")
            
            if new_level_name != old_level_name:
                print(f"⬆️ ПОЗДРАВЛЯЕМ! Вы достигли уровня: {new_level_name}!")
            
    def check_achievements(self, total_quests: int, boss_fight_time: float = -1):
        
        if total_quests >= 10 and "Первая Книжная Сотня" not in self.achievements:
            self.achievements.add("Первая Книжная Сотня")
            print("🏆 ДОСТИЖЕНИЕ: Первая Книжная Сотня!")

        if boss_fight_time != -1 and boss_fight_time < 5.0 and "Босс-Файт Покорен" not in self.achievements:
            self.achievements.add("Босс-Файт Покорен")
            self.grant_xp("BOSS_FIGHT") 
            print(f"👑 ДОСТИЖЕНИЕ: Босс-Файт Покорен за {boss_fight_time:.2f} сек!")

gamification_engine = GamificationEngine()
