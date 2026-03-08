import streamlit as st
import requests
from datetime import datetime


# НАСТРОЙКА СТРАНИЦЫ

st.set_page_config(
    page_title="Генератор описаний товаров",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# КОНФИГУРАЦИЯ API

API_URL = "http://localhost:8000/api"

# CSS СТИЛИ

st.markdown("""
    <style>
    .main-header {font-size: 2.5rem; font-weight: bold; color: #1f77b4;}
    .sub-header {font-size: 1.2rem; color: #666;}
    .success-box {padding: 1rem; background-color: #d4edda; border-radius: 5px;}
    .error-box {padding: 1rem; background-color: #f8d7da; border-radius: 5px;}
    </style>
""", unsafe_allow_html=True)

# КЭШИРОВАНИЕ ДАННЫХ

@st.cache_data
def get_categories():
    """
    Получает список доступных категорий из API.
    Кэшируется, чтобы не делать запрос при каждом обновлении страницы.
    """
    
    try:
        response = requests.get(f"{API_URL}/categories", timeout=5)
        if response.ok:
            return response.json()["categories"]
    except:
        pass
    return ["smartphones", "sneakers", "coffee_machines", "laptops", "headphones"]


@st.cache_data
def get_category_schema(category: str):
    """
    Получает схему атрибутов для конкретной категории.
    Нужно, чтобы знать, какие поля обязательны, а какие нет.
    """
    try:
        response = requests.get(f"{API_URL}/attributes/{category}", timeout=5)
        if response.ok:
            return response.json()
        
    except:
        pass
    return None

# ЗАГОЛОВОК СТРАНИЦЫ !!!

st.markdown('<p class="main-header">🛒 Генератор описаний товаров для интернет-магазина</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Автоматизация рутинных задач контент-менеджмента в E-commerce</p>', unsafe_allow_html=True)
st.markdown("---")

# БОКОВАЯ ПАНЕЛЬ !!!

with st.sidebar:
    st.header("Настройки")
    
    api_url_custom = st.text_input("URL API", value=API_URL)
    if api_url_custom:
        API_URL = api_url_custom
        
    st.markdown("---")
    
    st.markdown("### Навигация")
    st.markdown(f"[API Документация]({API_URL.replace('/api', '')}/docs)")
    st.markdown(f"[ReDoc]({API_URL.replace('/api', '')}/redoc)")
    
    st.markdown("---")
    
    st.markdown("### О проекте")
    st.info("""
    **Технологии:**
    - FastAPI (Backend)
    - Jinja2 (Шаблоны)
    - PostgreSQL (База Данных)
    - Streamlit (UI)
    """)


# ВЫБОР КАТЕГОРИИ ТОВАРА

st.header("Шаг 1: Выберите категорию товара")

categories = get_categories()

category = st.selectbox(
    "Категории товара",
    categories,
    help="Выберите категорию, для которой нужно создать описание"
)

# ФОРМА С ХАРАКТЕРИСТИКАМИ

st.header("Шаг 2: Заполните характеристики товара")

schema_info = get_category_schema(category)

attributes = {}

col1, col2 = st.columns(2)


# КОЛОНКА 1: Общие поля для всех категорий


# КОЛОНКА 1: Общие поля для всех категорий

with col1:
    # Динамические placeholder'ы в зависимости от категории
    if category == "smartphones":
        brand_placeholder = "Apple, Samsung, Xiaomi..."
        model_placeholder = "iPhone 15, Galaxy S24, Redmi Note 13..."
    elif category == "sneakers":
        brand_placeholder = "Nike, Adidas, Puma..."
        model_placeholder = "Air Force 1, Ultraboost, Suede..."
    elif category == "coffee_machines":
        brand_placeholder = "DeLonghi, Philips, Bosch, Saeco..."
        model_placeholder = "Magnifica, LatteGo, Barista..."
    elif category == "laptops":
        brand_placeholder = "Apple, ASUS, Lenovo, HP, Acer..."
        model_placeholder = "MacBook Pro, ThinkPad, Predator..."
    elif category == "headphones":
        brand_placeholder = "Sony, Bose, Sennheiser, JBL..."
        model_placeholder = "WH-1000XM5, QuietComfort, Momentum..."
    else:
        brand_placeholder = "Бренд товара"
        model_placeholder = "Модель товара"
    
    brand = st.text_input(
        "Бренд *",
        placeholder=brand_placeholder,  # ✅ Динамический
        help="Название бренда (обязательно)"
    )
    
    attributes["brand"] = brand if brand else ""
    
    model = st.text_input(
        "Модель *",
        placeholder=model_placeholder,  # ✅ Динамический
        help="Модель товара (обязательно)"
    )
    attributes["model"] = model if model else ""
    
    
# КОЛОНКА 2: Динамические поля

with col2:
    if category == "smartphones":
        memory = st.number_input(
            "Оперативная память (ГБ)*",
            min_value=4,
            max_value=1024,
            value=128,
            step=4,
            help="Объем оперативной памяти"
        )
        attributes["memory"] = memory
        
        camera = st.text_input(
            "Камера",
            placeholder="48 МП, 50МП, 108МП...",
            help="Разрешение основной камеры"
        )
        if camera:
            attributes["camera"] = camera
            
        color = st.text_input(
            "Цвет",
            placeholder="Black, White, Blue...",
            help="Цвет корпуса"
        )
        if color:
            attributes["color"] = color
            
    elif category == "sneakers":
        size = st.number_input(
            "Размер *",
            min_value=30,
            max_value=50,
            value=42,
            help="Размер обуви (EU)"
        )
        attributes["size"] = size
        
        color = st.text_input(
            "Цвет *",
            placeholder="White, Black, Red...",
            help="Основной цвет"
        )
        if color:
            attributes["color"] = color
            
        material = st.text_input(
            "Материал",
            placeholder="Leather, Mesh, Canvas...",
            help="Материал верха"
        )
        if material:
            attributes["material"] = material
            
    elif category == "coffee_machines":
        machine_type = st.selectbox(
            "Тип",
            ["автоматическая", "капсульная", "рожковая", "гейзерная"],
            help="Тип кофемашины"
        )
        attributes["type"] = machine_type
        
        power = st.text_input(
            "Мощность",
            placeholder="1500 Вт",
            help="Потребляемая мощность"
        )
        if power:
            attributes["power"] = power
            
        pressure = st.number_input(
            "Давление (бар)",
            min_value=1,
            max_value=20,
            value=15,
            help="Давление помпы"
        )
        attributes["pressure"] = pressure
        
        milk_frother = st.checkbox(
            "Капучинатор",
            value=False,
            help="Наличие капучинатора"
        )
        attributes["milk_frother"] = milk_frother
        
    elif category == "laptops":
        memory = st.number_input(
            "Оперативная помять (ГБ) *",
            min_value=4,
            max_value=128,
            value=16,
            step=4,
            help="Объем ОЗУ"
        )
        attributes["memory"] = memory
        
        processor = st.text_input(
            "Процессор",
            placeholder="Intel Core i7...",
            help="Модель процессора"
        )
        if processor:
            attributes["processor"] = processor
            
        weight = st.number_input(
            "Вес (кг)",
            min_value=0.5,
            max_value=5.0,
            value=1.5,
            step=0.1,
            help="Вес ноутбука"
        )
        if weight:
            attributes["weight"] = weight
            
    elif category == "headphones":
        hp_type = st.selectbox(
            "Тип",
            ["полноразмерные", "внутриканальные", "накладные", "вкладыши"],
            help="Тип конструкции"
        )
        attributes["type"] = hp_type
        
        battery = st.number_input(
            "Время работы (часы)",
            min_value=1,
            max_value=100,
            value=20,
            help="Время автономной работы"
        )
        if battery:
            attributes["battery"] = battery
            
        noise_cancelling = st.checkbox(
            "Активное шумоподавление",
            value=False,
            help="Наличие ANC"
        )
        attributes["noise_cancelling"] = noise_cancelling
        
        connectivity = st.selectbox(
            "Подключение",
            ["Bluetooth", "Wired", "Bluetooth + Wired"],
            help="Тип подключения"
        )
        attributes["connectivity"] = connectivity
        
        
# ГЕНЕРАЦИЯ ОПИСАНИЯ

st.markdown("---")
st.header("Шаг 3: Сгенерируйте описание")

if st.button("Сгенерировать описание", type="primary", use_container_width=True):
    errors = []
    
    if not attributes.get("brand"):
        errors.append("Бренд")
    if not attributes.get("model"):
        errors.append("Модель")
    if category == "smartphones" and not attributes.get("memory"):
        errors.append("Память")
    if category == "sneakers" and not attributes.get("size"):
        errors.append("Размер")
    if category == "laptops" and not attributes.get("memory"):
        errors.append("Память")
    
    model_lower = model.lower() if model else ""
    brand_lower = brand.lower() if brand else ""
    
    if "iphone" in model_lower and brand_lower != "apple":
        st.error("❌ iPhone производит только Apple! Исправьте бренд или модель.")
        errors.append("brand_model_mismatch")
    elif "galaxy" in model_lower and brand_lower != "samsung":
        st.error("❌ Galaxy производит только Samsung! Исправьте бренд или модель.")
        errors.append("brand_model_mismatch")
    elif "air force" in model_lower and brand_lower != "nike":
        st.error("❌ Air Force производит только Nike! Исправьте бренд или модель.")
        errors.append("brand_model_mismatch")
    
    
    if errors:
        st.error(f"Заполните обязательные поля: {', '.join(errors)}") 
    else:
        with st.spinner("Генерируем описание..."):
            try:
                response = requests.post(
                    f"{API_URL}/generate",
                    json={"category": category, "attributes": attributes},
                    timeout=30
                )
                
                if response.ok:
                    result = response.json()
                    
                    st.success("Описание успешно сгенерировано!")
                    st.subheader("Результат:")
                    st.info(result["generated_text"])
                    st.code(result["generated_text"], language="text")
                    
                    with st.expander("Информация о записи"):
                        st.json({
                            "ID": result["id"],
                            "Категория": result["category"],
                            "Статус": result["status"],
                            "Сохранено в историю": "Да"
                        })
                        
                    if "last_generated" not in st.session_state:
                        st.session_state["last_generated"] = []
                    st.session_state["last_generated"].append({
                        "id": result["id"],
                        "category": result["category"],
                        "text": result["generated_text"],
                        "time": datetime.now().strftime("%H:%M:%S")
                    })
                    
                else:
                    error_detail = response.json().get("detail", "Неизвестная ошибка")
                    st.error(f"Ошибка генерации: {error_detail}")
                    
            except requests.exceptions.ConnectionError:
                st.error("Не удалось подключиться к API. Убедитесь, что сервер запущен:")
                st.code("uvicorn src.main:app --reload", language="bash")
            except Exception as e:
                st.error(f"Произошла оишбка: {str(e)}")
                
                
# ИСТОРИЯ ГЕНЕРАЦИЙ

st.markdown("---")
st.header("История генераций")

with st.expander("Показать историю", expanded=False):
    if st.button("Обновить историю"):
        with st.spinner("Загружаем..."):
            try:
                response = requests.get(
                    f"{API_URL}/history?page=0&size=10",
                    timeout=10
                )
                
                if response.ok:
                    history = response.json()
                    
                    if history.get("items"):
                        st.success(f"Загружено {len(history['items'])} записей")
                        
                        for item in history["items"]:
                            with st.container():
                                col_date, col_cat = st.columns([1, 2])
                                with col_date:
                                    st.caption(f"{item['created_at']}")
                                with col_cat:
                                    st.markdown(f"**#{item['id']}** - {item['category']}")
                                st.text(item["generated_text"][:200] + "..." if len(item["generated_text"]) > 200 else item["generated_text"])
                                st.markdown("---")
                    else:
                        st.info(f"История пуста. Сгенерируйте первое описание!")
                else:
                    st.error("Не удалось загрузить историю")
                    
            except Exception as e:
                st.error(f"Ошибка: {str(e)}")
                
# ПОДВАЛ

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p><b>Проект выполнен в рамках курса...»</b></p>
    <p>FastAPI • Jinja2 • PostgreSQL • Streamlit</p>
</div>
""", unsafe_allow_html=True)