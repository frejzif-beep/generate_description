import json
import random
import logging
from pathlib import Path
from typing import Dict, Any

from src.services.exceptions import (
    TemplateNotFoundError,
    TemplateDataError,
    TemplateFileError
)

logger = logging.getLogger(__name__)


class TextGenerator:
    """
    Класс для генерации текстов описаний на основе шаблонов
    """
    def __init__(self):
        self.templates_path = Path(__file__).parent.parent.parent / "data" / "templates.json"
        self.templates: Dict[str, Any] = {}
        self._load_templates()
        logger.info(f"Генератор инициализирован, загружено {len(self.templates)} категорий")
        
    def _load_templates(self) -> None:
        """
        Загружаем шаблоны из JSON файла
        """
        logger.debug(f"Загрузка шаблонов из: {self.templates_path}")
        
        try:
            with open(self.templates_path, "r", encoding="utf-8") as f:
                self.templates = json.load(f)
                
            logger.info(f"Загружено {len(self.templates)} категорий шаблонов")                

        except FileNotFoundError:
            logger.error(f"Файл шаблонов не найден: {self.templates_path}")
            raise TemplateFileError(f"Файл шаблонов не найден: {self.templates_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка JSON в файле шаблонов: {e}")
            raise TemplateFileError(f"Ошибка в формате JSON файла шаблонов: {self.templates_path}")
        
    def generate(self, category: str, attributes: Dict[str, Any]) -> str:
        """
        Генерирует описание товара на основе товара
        """
        logger.debug(f"Генерация для категории '{category}' с {len(attributes)} атрибутами")
        
        # Проверяем есть ли шаблоны для данной кетегории
        if category not in self.templates:
            logger.warning(f"Шаблон не найдет для категории: {category}")
            raise TemplateNotFoundError(category=category)
        
        # Шаблоны
        category_templates = self.templates[category]
        
        if not category_templates:
            logger.warning(f"Пустой список шаблонов для категори: {category}")
            raise TemplateNotFoundError(f"Нет доступных шаблонов для категории '{category}'.")
        
        # Выбираем случайный шаблон
        template = random.choice(category_templates)
        logger.debug(f"Выбран шаблон: {template[:50]}...")
        
        # Подставляем данные в шаблон
        try:
            description = template.format_map(attributes)
            logger.info(f"Генерация прошла успешно: {len(description)} символов")
            return description
        
        except KeyError as e:
            logger.warning(f"Отсутствует поле в атрибутах: {str(e)}")
            raise TemplateDataError(f"В шаблоне есть переменная {e}, но нет данных для неё.")
        
    def get_categories(self) -> list[str]:
        """
        Возвращает список доступных категорий
        """
        return list(self.templates.keys())
        
    
# Глобальный экземпляр генератора
global_generator_service = TextGenerator()