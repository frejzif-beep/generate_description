class GeneratorError(Exception):
    """
    Базовое исключение для всех ошибок генератора.
    Используется как родительский класс для специфичных ошибок
    """
    pass


class TemplateNotFoundError(GeneratorError):
    """
    Вызывается, когда шаблоны для указанной категории не найдены.
    HTTP статус: 404 not found
    """
    pass


class TemplateDataError(GeneratorError):
    """
    Вызывается, когда в шаблоне есть переменные, которых нет в переданных данных.
    HTTP статус: 400 Bad Request
    """
    pass


class TemplateFileError(GeneratorError):
    """
    Вызывается, когда файл с шаблонами не найден или повреждён.
    HTTP статус: 500 Internal Server Error
    """
    pass