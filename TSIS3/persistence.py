# МЕНЕДЖЕР ДАННЫХ - СОХРАНЕНИЕ НАСТРОЕК И ТАБЛИЦЫ РЕКОРДОВ
import json  # Модуль для работы с JSON (сериализация/десериализация)
import os    # Модуль для работы с файловой системой (пути, проверка существования файлов)

class DataManager:
    """Класс для управления сохранением данных: настройки игры и таблица рекордов"""
    
    def __init__(self):
        # ОПРЕДЕЛЯЕМ ПУТИ К ФАЙЛАМ
        # os.path.dirname(os.path.abspath(__file__)) - получаем папку, где находится текущий скрипт
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        # Формируем полный путь к файлу настроек
        self.settings_file = os.path.join(self.script_dir, "settings.json")
        # Формируем полный путь к файлу таблицы рекордов
        self.leaderboard_file = os.path.join(self.script_dir, "leaderboard.json")
        
        # ЗАГРУЖАЕМ ДАННЫЕ ПРИ СОЗДАНИИ ОБЪЕКТА
        self.load_settings()     # Загрузка настроек
        self.load_leaderboard()  # Загрузка рекордов
    
    def load_settings(self):
        """Загружает настройки из JSON файла, если файл отсутствует - создаёт настройки по умолчанию"""
        
        # НАСТРОЙКИ ПО УМОЛЧАНИЮ
        default_settings = {
            "sound": True,                    # Звук включён (True/False)
            "car_color": (255, 0, 0),        # Цвет машины в формате RGB (красный)
            "difficulty": "normal"           # Уровень сложности: easy/normal/hard
        }
        
        # ПРОВЕРЯЕМ, СУЩЕСТВУЕТ ЛИ ФАЙЛ НАСТРОЕК
        if os.path.exists(self.settings_file):
            try:
                # Открываем файл для чтения
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)  # Загружаем JSON в словарь Python
                    
                    # КОНВЕРТАЦИЯ ЦВЕТА: в JSON цвет сохраняется как список [255,0,0]
                    # Но в игре нужен кортеж (255,0,0) - кортеж неизменяемый, список изменяемый
                    if "car_color" in loaded:
                        # Преобразуем список в кортеж: [255,0,0] -> (255,0,0)
                        loaded["car_color"] = tuple(loaded["car_color"])
                    
                    self.settings = loaded  # Сохраняем загруженные настройки
            except:
                # Если произошла ошибка (битый файл, неверный JSON) - используем настройки по умолчанию
                self.settings = default_settings
        else:
            # ФАЙЛА НЕТ - создаём настройки по умолчанию
            self.settings = default_settings
            self.save_settings()  # Сохраняем их в файл
    
    def save_settings(self):
        """Сохраняет текущие настройки в JSON файл"""
        
        # СОЗДАЁМ КОПИЮ НАСТРОЕК, чтобы не изменять оригинал
        settings_to_save = self.settings.copy()
        
        # ПРЕОБРАЗУЕМ ЦВЕТ ДЛЯ JSON
        # В JSON нельзя сохранить кортеж, только список
        settings_to_save["car_color"] = list(settings_to_save["car_color"])  # (255,0,0) -> [255,0,0]
        
        # ОТКРЫВАЕМ ФАЙЛ ДЛЯ ЗАПИСИ
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            # Записываем настройки в JSON
            # indent=4 - красивое форматирование с отступами
            # ensure_ascii=False - сохранять русские символы как есть, не преобразовывать в \u...
            json.dump(settings_to_save, f, indent=4, ensure_ascii=False)
    
    def load_leaderboard(self):
        """Загружает таблицу рекордов из JSON файла"""
        
        # ПРОВЕРЯЕМ СУЩЕСТВОВАНИЕ ФАЙЛА
        if os.path.exists(self.leaderboard_file):
            try:
                with open(self.leaderboard_file, 'r', encoding='utf-8') as f:
                    self.leaderboard = json.load(f)  # Загружаем список рекордов
            except:
                # При ошибке создаём пустой список
                self.leaderboard = []
        else:
            # Файла нет - создаём пустой список
            self.leaderboard = []
    
    def save_leaderboard(self):
        """Сохраняет таблицу рекордов в JSON файл (только топ-10)"""
        
        with open(self.leaderboard_file, 'w', encoding='utf-8') as f:
            # self.leaderboard[:10] - сохраняем только первые 10 записей (срез списка)
            json.dump(self.leaderboard[:10], f, indent=4, ensure_ascii=False)
    
    def add_score(self, name, score, distance, coins):
        """Добавляет новый результат в таблицу рекордов
           Аргументы:
           name - имя игрока
           score - набранные очки (основной критерий сортировки)
           distance - пройденная дистанция
           coins - собранные монеты
        """
        
        # ДОБАВЛЯЕМ НОВУЮ ЗАПИСЬ В КОНЕЦ СПИСКА
        self.leaderboard.append({
            "name": name,        # Имя игрока
            "score": score,      # Очки
            "distance": distance,# Дистанция
            "coins": coins       # Монеты
        })
        
        # СОРТИРУЕМ СПИСОК ПО ОЧКАМ (по убыванию)
        # lambda x: x["score"] - функция, которая из каждого словаря извлекает значение по ключу "score"
        # reverse=True - сортировка от большего к меньшему
        self.leaderboard.sort(key=lambda x: x["score"], reverse=True)
        
        # ОСТАВЛЯЕМ ТОЛЬКО ТОП-10 (обрезаем список до 10 элементов)
        self.leaderboard = self.leaderboard[:10]
        
        # СОХРАНЯЕМ ОБНОВЛЁННУЮ ТАБЛИЦУ В ФАЙЛ
        self.save_leaderboard()
    
    def get_top_scores(self):
        """Возвращает текущую таблицу рекордов (топ-10)"""
        return self.leaderboard