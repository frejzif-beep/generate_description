import json
import random
from pathlib import Path
from typing import Dict, Any

from src.services.exceptions import (
    TemplateNotFoundError,
    TemplateDataError,
    TemplateFileError
)


class TextGenerator:
    """
    Класс для генерации текстов описаний на основе шаблонов
    """
    def __init__(self):
        self.templates_path = Path(__file__).parent.parent.parent / "data" / "templates.json"
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict:
        """
        Загружаем шаблоны из JSON файла
        """
        try:
            with open(self.templates_path, "r", encoding="utf-8") as myfile:
                return json.load(myfile)
        except FileNotFoundError:
            raise TemplateFileError(f"Файл шаблонов не найден: {self.templates_path}")
        except json.JSONDecodeError:
            raise TemplateFileError(f"Ошибка в формате JSON файла шаблонов: {self.templates_path}")
        
    def generate(self, category: str, attributes: Dict[str, Any]) -> str:
        """
        Генерирует описание товара на основе товара
        """
        
        # Проверяем есть ли шаблоны для данныой кетегории
        if category not in self.templates:
            raise TemplateNotFoundError(f"Шаблоны для категории '{category}' не найдены.")
        
        # Шаблоны
        category_templates = self.templates[category]
        
        if not category_templates:
            raise TemplateNotFoundError(f"Нет доступных шаблонов для категории '{category}'.")
        
        # Выбираем случайный шаблон
        template = random.choice(category_templates)
        
        # Подставляем данные в шаблон
        try:
            description = template.format_map(attributes)
            return description
        except KeyError as Ekey:
            raise TemplateDataError(f"В шаблоне есть переменная {Ekey}, но нет данных для неё.")
        
        
# Глобальный экземпляр генератора
global_generator_service = TextGenerator()