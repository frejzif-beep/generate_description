import json
import random
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Environment, DictLoader, TemplateNotFound as JinjaTemplateNotFound

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
        self.jinja2_env: Optional[Environment] = None
        self.templates: Dict[str, Any] = {}
        self._load_templates()
        logger.info(f"Генератор инициализирован, загружено {len(self.templates)} категорий")
        
    def _load_templates(self) -> None:
        """Загружаем шаблоны из JSON файла"""
        logger.debug(f"Загрузка шаблонов из: {self.templates_path}")
        
        try:
            with open(self.templates_path, "r", encoding="utf-8") as f:
                self.templates = json.load(f)
                
            self.jinja2_env = Environment(
                loader=DictLoader(self._flatten_templates()),
                autoescape=False,
                trim_blocks=True,
                lstrip_blocks=True
            )
            
            self.jinja2_env.filters['plural'] = self._russian_plural
                
            logger.info(f"Загружено {len(self.templates)} категорий шаблонов")                

        except FileNotFoundError:
            logger.error(f"Файл шаблонов не найден: {self.templates_path}")
            raise TemplateFileError(f"Файл шаблонов не найден: {self.templates_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка JSON в файле шаблонов: {e}")
            raise TemplateFileError(f"Ошибка в формате JSON файла шаблонов: {self.templates_path}")
        
    def _flatten_templates(self) -> Dict[str, str]:
        """
        Преобразует структуру шаблонов в формат для DictLoader.
        Ключ: "category_template_index", Значение: шаблон
        """
        flattened = {}
        for category, templates_list in self.templates.items():
            for idx, template in enumerate(templates_list):
                key = f"{category}_{idx}"
                flattened[key] = template
        return flattened        
        
    def generate(self, category: str, attributes: Dict[str, Any]) -> str:
        """Генерирует описание товара с использованием jinja"""
        logger.debug(f"Генерация для категории '{category}' с {len(attributes)} атрибутами")
        
        # Проверяем есть ли шаблоны для данной кетегории
        if category not in self.templates:
            logger.warning(f"Шаблон не найдет для категории: {category}")
            raise TemplateNotFoundError(f"Шаблоны для категории '{category}' не найдены")
        
        # Шаблоны
        category_templates = self.templates[category]
        
        if not category_templates:
            logger.warning(f"Пустой список шаблонов для категори: {category}")
            raise TemplateNotFoundError(f"Нет доступных шаблонов для категории '{category}'.")
        
        # Выбираем случайный шаблон
        template_index = random.randint(0, len(category_templates) - 1)
        template_key = f"{category}_{template_index}"
        
        # Подставляем данные в шаблон
        try:
            template = self.jinja2_env.get_template(template_key)
            logger.debug(f"Выбран шаблон: {template_key}")
            
            #Рендерим с атрибутами
            context = {
                **attributes,
                'attributes': attributes,
                "attrs_count": len(attributes),
                "category": category
            }
            description = template.render(**context)
            logger.info(f"Генерация прошла успешно: {len(description)} символов")
            return description

        except JinjaTemplateNotFound:
            logger.error(f"Шаблон {template_key} не найден в Environment")
            raise TemplateNotFoundError(f"Внутренняя ошибка: шаблон не загружен")
        except KeyError as e:
            logger.warning(f"Отсутствует поле в атрибутах: {str(e)}")
            raise TemplateDataError(f"В шаблоне есть переменная {e}, но нет данных для неё")
        except Exception as e:
            logger.error(f"Ошибка рендеринга шаблона: {e}", exc_info=True)
            raise TemplateDataError(f"Ошибка при генерации текста: {str(e)}")         
            
    def _russian_plural(self, value: int, forms: list[str]) -> str:
        """
        Фильтр для склонения числительных в русском языке.
        Пример: {{ 5 | plural(['товар', 'товара', 'товаров']) }} → "товаров"
        """
        if not forms or not isinstance(forms, (list, tuple)) or len(forms) < 3:
            logger.warning(f"Некоректный список форм для plural: {forms}")
            return str(value)
        
        if value is None:
            return forms[0]
        
        try:
            value = int(value)
        except (ValueError, TypeError):
            logger.warning(f"Некорректное значение для plural: {value}")
            return forms[0]
            
        if value % 100 in range(11, 15):
            return forms[2]
        
        last_digit = value % 10
        
        if last_digit == 1:
            return forms[0]
        elif last_digit in [2, 3, 4]:
            return forms[1]
        else:
            return forms[2]
            
    def get_categories(self) -> list[str]:
        """Возвращает список доступных категорий"""
        return list(self.templates.keys())
        
    
# Глобальный экземпляр генератора
global_generator_service = TextGenerator()