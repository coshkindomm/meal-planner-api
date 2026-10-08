from __future__ import annotations

import os
import sys
import uuid
from typing import Dict, List

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Импортируем ORM-модели и перечисления из файла backend_models.py
from backend_models import (
    Base,
    ChainRoleEnum,
    CityCodeEnum,
    CourseTypeEnum,
    Ingredient,
    MealTypeEnum,
    ProductPack,
    Recipe,
    RecipeIngredient,
    RecipeStep,
    StoreNetworkEnum,
    StorePrice,
)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///meal_planner.db")

print(f"[*] Подключение к базе данных: {DATABASE_URL}")
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Каталог продуктов с русскими названиями и флагами аллергенов
INGREDIENTS_DATA = [
    {
        "id": "ing_curd_5",
        "name": "Творог 5% в пачке",
        "category": "Молочные продукты",
        "is_lactose": True,
        "has_gluten": False,
        "is_pork": False,
        "is_beef": False,
        "is_poultry": False,
        "is_fish": False,
        "is_onion": False,
        "is_garlic": False,
        "is_mushrooms": False,
        "shelf_life_opened_days": 4,
        "default_unit": "г",
    },
    {
        "id": "ing_milk",
        "name": "Молоко питьевое пастеризованное 2.5%",
        "category": "Молочные продукты",
        "is_lactose": True,
        "has_gluten": False,
        "is_pork": False,
        "is_beef": False,
        "is_poultry": False,
        "is_fish": False,
        "is_onion": False,
        "is_garlic": False,
        "is_mushrooms": False,
        "shelf_life_opened_days": 5,
        "default_unit": "мл",
    },
    {
        "id": "ing_sour_cream",
        "name": "Сметана 15%",
        "category": "Молочные продукты",
        "is_lactose": True,
        "has_gluten": False,
        "is_pork": False,
        "is_beef": False,
        "is_poultry": False,
        "is_fish": False,
        "is_onion": False,
        "is_garlic": False,
        "is_mushrooms": False,
        "shelf_life_opened_days": 10,
        "default_unit": "г",
    },
    {
        "id": "ing_butter",
        "name": "Сливочное масло 82.5%",
        "category": "Молочные продукты",
        "is_lactose": True,
        "has_gluten": False,
        "is_pork": False,
        "is_beef": False,
        "is_poultry": False,
        "is_fish": False,
        "is_onion": False,
        "is_garlic": False,
        "is_mushrooms": False,
        "shelf_life_opened_days": 30,
        "default_unit": "г",
    },
    {
        "id": "ing_eggs",
        "name": "Яйца куриные С1 отборные",
        "category": "Яйца",
        "is_lactose": False,
        "has_gluten": False,
        "is_pork": False,
        "is_beef": False,
        "is_poultry": False,
        "is_fish": False,
        "is_onion": False,
        "is_garlic": False,
        "is_mushrooms": False,
        "shelf_life_opened_days": 25,
        "default_unit": "шт",
    },
    {
        "id": "ing_chicken_breast",
        "name": "Филе грудки цыпленка охлажденное",
        "category": "Мясо и птица",
        "is_lactose": False,
        "has_gluten": False,
        "is_pork": False,
        "is_beef": False,
        "is_poultry": True,
        "is_fish": False,
        "is_onion": False,
        "is_garlic": False,
        "is_mushrooms": False,
        "shelf_life_opened_days": 3,
        "default_unit": "г",
    },
    {
        "id": "ing_turkey_breast",
        "name": "Филе грудки индейки охлажденное",
        "category": "Мясо и птица",
        "is_lactose": False,
        "has_gluten": False,
        "is_pork": False,
        "is_beef": False,
        "is_poultry": True,
        "is_fish": False,
        "is_onion": False,
        "is_garlic": False,
        "is_mushrooms": False,
        "shelf_life_opened_days": 3,
        "default_unit": "г",
    },
    {
        "id": "ing_beef_stew",
        "name": "Говядина духовая лоток",
        "category": "Мясо и птица",
        "is_lactose": False,
        "has_gluten": False,
        "is_pork": False,
        "is_beef": True,
        "is_poultry": False,
        "is_fish": False,
        "is_onion": False,
        "is_garlic": False,
        "is_mushrooms": False,
        "shelf_life_opened_days": 4,
        "default_unit": "г",
    },
    {
        "id": "ing_beef_mince",
        "name": "Фарш говяжий домашний охлажденный",
        "category": "Мясо и птица",
        "is_lactose": False,
        "has_gluten": False,
        "is_pork": False,
        "is_beef": True,
        "is_poultry": False,
        "is_fish": False,
        "is_onion": False,
        "is_garlic": False,
        "is_mushrooms": False,
        "shelf_life_opened_days": 3,
        "default_unit": "г",
    },
    {
        "id": "ing_cod_fillet",
        "name": "Филе мурманской трески",
        "category": "Рыба и морепродукты",
        "is_lactose": False,
        "has_gluten": False,
        "is_pork": False,
        "is_beef": False,
        "is_poultry": False,
        "is_fish": True,
        "is_onion": False,
        "is_garlic": False,
        "is_mushrooms": False,
        "shelf_life_opened_days": 3,
        "default_unit": "г",
    },
    {
        "id": "ing_buckwheat",
        "name": "Гречневая крупа ядрица",
        "category": "Бакалея",
        "is_lactose": False,
        "has_gluten": False,
        "is_pork": False,
        "is_beef": False,
        "is_poultry": False,
        "is_fish": False,
        "is_onion": False,
        "is_garlic": False,
        "is_mushrooms": False,
        "shelf_life_opened_days": 360,
        "default_unit": "г",
    },
    {
        "id": "ing_rice",
        "name": "Рис Жасмин / круглозерный",
        "category": "Бакалея",
        "is_lactose": False,
        "has_gluten": False,
        "is_pork": False,
        "is_beef": False,
        "is_poultry": False,
        "is_fish": False,
        "is_onion": False,
        "is_garlic": False,
        "is_mushrooms": False,
        "shelf_life_opened_days": 360,
        "default_unit": "г",
    },
    {
        "id": "ing_millet",
        "name": "Пшено шлифованное золотистое",
        "category": "Бакалея",
        "is_lactose": False,
        "has_gluten": False,
        "is_pork": False,
        "is_beef": False,
        "is_poultry": False,
        "is_fish": False,
        "is_onion": False,
        "is_garlic": False,
        "is_mushrooms": False,
        "shelf_life_opened_days": 360,
        "default_unit": "г",
    },
    {
        "id": "ing_oats",
        "name": "Овсяные хлопья традиционные",
        "category": "Бакалея",
        "is_lactose": False,
        "has_gluten": False,
        "is_pork": False,
        "is_beef": False,
        "is_poultry": False,
        "is_fish": False,
        "is_onion": False,
        "is_garlic": False,
        "is_mushrooms": False,
        "shelf_life_opened_days": 180,
        "default_unit": "г",
    },
    {
        "id": "ing_flour",
        "name": "Мука пшеничная высший сорт",
        "category": "Бакалея",
        "is_lactose": False,
        "has_gluten": True,
        "is_pork": False,
        "is_beef": False,
        "is_poultry": False,
        "is_fish": False,
        "is_onion": False,
        "is_garlic": False,
        "is_mushrooms": False,
        "shelf_life_opened_days": 360,
        "default_unit": "г",
    },
    {
        "id": "ing_potatoes",
        "name": "Картофель отборный мытый",
        "category": "Овощи и зелень",
        "is_lactose": False,
        "has_gluten": False,
        "is_pork": False,
        "is_beef": False,
        "is_poultry": False,
        "is_fish": False,
        "is_onion": False,
        "is_garlic": False,
        "is_mushrooms": False,
        "shelf_life_opened_days": 30,
        "default_unit": "г",
    },
    {
        "id": "ing_cabbage",
        "name": "Капуста белокочанная",
        "category": "Овощи и зелень",
        "is_lactose": False,
        "has_gluten": False,
        "is_pork": False,
        "is_beef": False,
        "is_poultry": False,
        "is_fish": False,
        "is_onion": False,
        "is_garlic": False,
        "is_mushrooms": False,
        "shelf_life_opened_days": 20,
        "default_unit": "г",
    },
    {
        "id": "ing_beets",
        "name": "Свекла свежая столовая",
        "category": "Овощи и зелень",
        "is_lactose": False,
        "has_gluten": False,
        "is_pork": False,
        "is_beef": False,
        "is_poultry": False,
        "is_fish": False,
        "is_onion": False,
        "is_garlic": False,
        "is_mushrooms": False,
        "shelf_life_opened_days": 25,
        "default_unit": "г",
    },
    {
        "id": "ing_carrots",
        "name": "Морковь фермерская мытая",
        "category": "Овощи и зелень",
        "is_lactose": False,
        "has_gluten": False,
        "is_pork": False,
        "is_beef": False,
        "is_poultry": False,
        "is_fish": False,
        "is_onion": False,
        "is_garlic": False,
        "is_mushrooms": False,
        "shelf_life_opened_days": 20,
        "default_unit": "г",
    },
    {
        "id": "ing_dill",
        "name": "Укроп свежий пучок",
        "category": "Овощи и зелень",
        "is_lactose": False,
        "has_gluten": False,
        "is_pork": False,
        "is_beef": False,
        "is_poultry": False,
        "is_fish": False,
        "is_onion": False,
        "is_garlic": False,
        "is_mushrooms": False,
        "shelf_life_opened_days": 6,
        "default_unit": "г",
    },
    {
        "id": "ing_apples",
        "name": "Яблоки сезонные садовые",
        "category": "Овощи и зелень",
        "is_lactose": False,
        "has_gluten": False,
        "is_pork": False,
        "is_beef": False,
        "is_poultry": False,
        "is_fish": False,
        "is_onion": False,
        "is_garlic": False,
        "is_mushrooms": False,
        "shelf_life_opened_days": 14,
        "default_unit": "г",
    },
    {
        "id": "ing_pumpkin",
        "name": "Тыква свежая сладкая",
        "category": "Овощи и зелень",
        "is_lactose": False,
        "has_gluten": False,
        "is_pork": False,
        "is_beef": False,
        "is_poultry": False,
        "is_fish": False,
        "is_onion": False,
        "is_garlic": False,
        "is_mushrooms": False,
        "shelf_life_opened_days": 25,
        "default_unit": "г",
    },
    {
        "id": "ing_berries",
        "name": "Ягоды лесные замороженные",
        "category": "Овощи и зелень",
        "is_lactose": False,
        "has_gluten": False,
        "is_pork": False,
        "is_beef": False,
        "is_poultry": False,
        "is_fish": False,
        "is_onion": False,
        "is_garlic": False,
        "is_mushrooms": False,
        "shelf_life_opened_days": 180,
        "default_unit": "г",
    },
]

PACKS_CONFIG = {
    "ing_chicken_breast": {"title": "Филе цыпленка лоток", "amount": 850.0, "unit": "г", "by_weight": False, "price": 380.0},
    "ing_turkey_breast": {"title": "Филе индейки лоток", "amount": 800.0, "unit": "г", "by_weight": False, "price": 440.0},
    "ing_beef_stew": {"title": "Говядина духовая лоток", "amount": 700.0, "unit": "г", "by_weight": False, "price": 590.0},
    "ing_beef_mince": {"title": "Фарш говяжий охлажденный", "amount": 400.0, "unit": "г", "by_weight": False, "price": 275.0},
    "ing_cod_fillet": {"title": "Филе трески упаковка", "amount": 600.0, "unit": "г", "by_weight": False, "price": 430.0},
    "ing_curd_5": {"title": "Творог 5% пачка", "amount": 360.0, "unit": "г", "by_weight": False, "price": 145.0},
    "ing_eggs": {"title": "Яйца куриные десяток", "amount": 10.0, "unit": "шт", "by_weight": False, "price": 125.0},
    "ing_milk": {"title": "Молоко бутылка 930мл", "amount": 930.0, "unit": "мл", "by_weight": False, "price": 88.0},
    "ing_sour_cream": {"title": "Сметана 15% стакан", "amount": 300.0, "unit": "г", "by_weight": False, "price": 95.0},
    "ing_butter": {"title": "Масло сливочное пачка", "amount": 180.0, "unit": "г", "by_weight": False, "price": 190.0},
    "ing_buckwheat": {"title": "Гречка ядрица пачка", "amount": 800.0, "unit": "г", "by_weight": False, "price": 98.0},
    "ing_rice": {"title": "Рис шлифованный пачка", "amount": 800.0, "unit": "г", "by_weight": False, "price": 135.0},
    "ing_millet": {"title": "Пшено шлифованное пачка", "amount": 800.0, "unit": "г", "by_weight": False, "price": 85.0},
    "ing_oats": {"title": "Овсяные хлопья коробка", "amount": 500.0, "unit": "г", "by_weight": False, "price": 92.0},
    "ing_flour": {"title": "Мука пшеничная пачка", "amount": 1000.0, "unit": "г", "by_weight": False, "price": 85.0},
    "ing_potatoes": {"title": "Картофель свежий (развес)", "amount": 1000.0, "unit": "г", "by_weight": True, "price": 58.0},
    "ing_cabbage": {"title": "Капуста белокочанная (развес)", "amount": 1000.0, "unit": "г", "by_weight": True, "price": 42.0},
    "ing_beets": {"title": "Свекла свежая (развес)", "amount": 1000.0, "unit": "г", "by_weight": True, "price": 45.0},
    "ing_carrots": {"title": "Морковь мытая (развес)", "amount": 1000.0, "unit": "г", "by_weight": True, "price": 49.0},
    "ing_dill": {"title": "Укроп свежий пучок", "amount": 70.0, "unit": "г", "by_weight": False, "price": 55.0},
    "ing_apples": {"title": "Яблоки сезонные (развес)", "amount": 1000.0, "unit": "г", "by_weight": True, "price": 125.0},
    "ing_pumpkin": {"title": "Тыква свежая (развес)", "amount": 1000.0, "unit": "г", "by_weight": True, "price": 89.0},
    "ing_berries": {"title": "Ягоды замороженные пачка", "amount": 300.0, "unit": "г", "by_weight": False, "price": 195.0},
}

# Каталог блюд с ТОЧНЫМИ проверенными фотографиями русской кухни
RECIPES_DATABASE = [
    {
        "id": 1,
        "name": "Борщ классический с говядиной",
        "category": "Первые блюда",
        "portion_weight_g": 350,
        "nutrition_per_portion": {
            "calories": 285,
            "proteins": 16.5,
            "fats": 14.0,
            "carbs": 23.0
        },
        "ingredients_per_person": [
            {"name": "Говяжья грудинка на кости", "weight_g": 120, "comment": "для наваристого бульона"},
            {"name": "Свёкла", "weight_g": 80, "comment": "соломкой 3-4 мм"},
            {"name": "Капуста белокочанная", "weight_g": 70, "comment": "тонкая соломка"},
            {"name": "Картофель", "weight_g": 60, "comment": "брусочки"},
            {"name": "Морковь", "weight_g": 35, "comment": "мелкая соломка"},
            {"name": "Лук репчатый", "weight_g": 30, "comment": "мелкий кубик"},
            {"name": "Томатная паста", "weight_g": 15, "comment": "для фиксации рубинового цвета"},
            {"name": "Уксус 9% (или лимонный сок)", "weight_g": 5, "comment": "для кислотности"},
            {"name": "Сахар", "weight_g": 4, "comment": "баланс вкуса"},
            {"name": "Чеснок", "weight_g": 5, "comment": "1 зубчик, измельчить"},
            {"name": "Масло растительное", "weight_g": 10, "comment": "для пассеровки"},
            {"name": "Вода питьевая", "weight_g": 350, "comment": "для варки бульона"},
            {"name": "Лавровый лист", "weight_g": 1, "comment": "1 штука"},
            {"name": "Соль и черный перец", "weight_g": 3, "comment": "по вкусу"},
            {"name": "Сметана 15% и укроп", "weight_g": 25, "comment": "для подачи"}
        ],
        "cooking_steps": [
            {
                "step": 1,
                "action": "Варка бульона",
                "heat": "Сильный до кипения, затем минимальный",
                "color_and_visual": "Снятие серой пены; бульон становится прозрачным, янтарным",
                "time_min": 85,
                "description": "Залить мясо холодной водой, довести до кипения, тщательно снять шум. Варить при едва заметном колыхании жидкости до мягкости говядины."
            },
            {
                "step": 2,
                "action": "Тушение свёклы",
                "heat": "Умеренный, затем слабый под крышкой",
                "color_and_visual": "Цвет меняется с сырого багрового на блестящий рубиновый",
                "time_min": 18,
                "description": "Спассеровать свёклу на масле 3 минуты, ввести томатную пасту, уксус, сахар и 50 мл бульона. Тушить до размягчения."
            },
            {
                "step": 3,
                "action": "Пассеровка кореньев",
                "heat": "Средний огонь",
                "color_and_visual": "Лук полупрозрачный, морковь отдает цвет маслу (оранжевый оттенок)",
                "time_min": 7,
                "description": "Обжарить лук и морковь до мягкости, не допуская подгорания."
            },
            {
                "step": 4,
                "action": "Сборка супа",
                "heat": "Средний огонь, затем тихий",
                "color_and_visual": "Насыщенный темно-красный цвет, овощи распределены равномерно",
                "time_min": 15,
                "description": "В кипящий бульон опустить картофель, через 5 минут капусту, варить 7 минут. Добавить свёклу и пассеровку, варить еще 5 минут."
            },
            {
                "step": 5,
                "action": "Доводка и настаивание",
                "heat": "Огонь выключен",
                "color_and_visual": "Плотная бархатистая текстура с зеленью на поверхности",
                "time_min": 20,
                "description": "Ввести чеснок, соль, перец и лавровый лист. Снять с огня, накрыть крышкой и дать настояться перед подачей со сметаной."
            }
        ],
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Borscht_served.jpg/800px-Borscht_served.jpg"
    },
    {
        "id": 2,
        "name": "Щи суточные из квашеной капусты",
        "category": "Первые блюда",
        "portion_weight_g": 350,
        "nutrition_per_portion": {
            "calories": 230,
            "proteins": 14.0,
            "fats": 12.5,
            "carbs": 15.0
        },
        "ingredients_per_person": [
            {"name": "Говяжья голяшка или грудинка", "weight_g": 120, "comment": "на кости"},
            {"name": "Капуста квашеная бочковая", "weight_g": 130, "comment": "нашинкованная, отжатая"},
            {"name": "Картофель", "weight_g": 50, "comment": "небольшие клубни целыми"},
            {"name": "Морковь", "weight_g": 35, "comment": "соломка"},
            {"name": "Лук репчатый", "weight_g": 35, "comment": "кубик"},
            {"name": "Томатное пюре", "weight_g": 15, "comment": "для томления"},
            {"name": "Масло топленое", "weight_g": 10, "comment": "для томления капусты"},
            {"name": "Бульон мясной", "weight_g": 350, "comment": "основа"},
            {"name": "Чеснок", "weight_g": 4, "comment": "растертый с солью"},
            {"name": "Специи и соль", "weight_g": 3, "comment": "лавр, перец горошком"},
            {"name": "Сметана 20%", "weight_g": 20, "comment": "для подачи"}
        ],
        "cooking_steps": [
            {
                "step": 1,
                "action": "Томление капусты",
                "heat": "Минимальный огонь в толстостенном сотейнике",
                "color_and_visual": "Капуста темнеет до золотисто-коричневого, мягкая, без резкой кислоты",
                "time_min": 75,
                "description": "Квашеную капусту соединить с топленым маслом, томатным пюре и 70 мл бульона. Томить под крышкой до полной мягкости."
            },
            {
                "step": 2,
                "action": "Варка основы",
                "heat": "Тихий огонь",
                "color_and_visual": "Бульон прозрачный, янтарно-желтый",
                "time_min": 80,
                "description": "Сварить крепкий говяжий навар. За 20 минут до готовности опустить картофель целиком."
            },
            {
                "step": 3,
                "action": "Пассеровка кореньев",
                "heat": "Средний огонь",
                "color_and_visual": "Морковь и лук приобретают теплый золотистый колер",
                "time_min": 8,
                "description": "Обжарить лук и морковь на топленом масле до появления сладковатого аромата."
            },
            {
                "step": 4,
                "action": "Объединение щей",
                "heat": "Слабый огонь",
                "color_and_visual": "Суп становится густым, цвета старого янтаря",
                "time_min": 25,
                "description": "Размять готовый картофель вилкой, вернуть в бульон вместе с томленой капустой и пассеровкой. Варить на малом огне."
            },
            {
                "step": 5,
                "action": "Суточная выдержка",
                "heat": "Теплое укутывание или остывающая духовка",
                "color_and_visual": "Глубокий матовый оттенок, однородная бархатистость",
                "time_min": 360,
                "description": "Заправить чесноком и специями. Настоять не менее 6 часов (в идеале — сутки в прохладном месте с последующим разогревом)."
            }
        ],
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Russian_cabbage_soup.jpg/800px-Russian_cabbage_soup.jpg"
    },
    {
        "id": 3,
        "name": "Щи из свежей капусты",
        "category": "Первые блюда",
        "portion_weight_g": 350,
        "nutrition_per_portion": {
            "calories": 195,
            "proteins": 12.0,
            "fats": 10.0,
            "carbs": 14.5
        },
        "ingredients_per_person": [
            {"name": "Говядина (лопаточная часть)", "weight_g": 110, "comment": "нарезка кусочками"},
            {"name": "Капуста белокочанная свежая", "weight_g": 120, "comment": "соломка 5 мм"},
            {"name": "Картофель", "weight_g": 60, "comment": "брусочки"},
            {"name": "Морковь", "weight_g": 40, "comment": "тонкие кружочки или соломка"},
            {"name": "Лук репчатый", "weight_g": 30, "comment": "четверть-кольца"},
            {"name": "Помидор свежий", "weight_g": 40, "comment": "без кожицы, кубик"},
            {"name": "Масло растительное", "weight_g": 10, "comment": "для пассеровки"},
            {"name": "Бульон мясной", "weight_g": 350, "comment": "чистый навар"},
            {"name": "Укроп и петрушка", "weight_g": 7, "comment": "мелко порубленные"},
            {"name": "Соль, лавр, перец", "weight_g": 3, "comment": "по вкусу"},
            {"name": "Сметана 15%", "weight_g": 20, "comment": "при подаче"}
        ],
        "cooking_steps": [
            {
                "step": 1,
                "action": "Приготовление бульона",
                "heat": "Средний огонь до закипания, затем минимальный",
                "color_and_visual": "Светло-золотой прозрачный бульон без взвеси",
                "time_min": 70,
                "description": "Сварить мясо с добавлением стеблей зелени, процедить навар."
            },
            {
                "step": 2,
                "action": "Пассеровка овощей",
                "heat": "Умеренный огонь",
                "color_and_visual": "Томаты отдают сок, масло окрашивается в нежно-оранжевый тон",
                "time_min": 8,
                "description": "Обжарить лук с морковью 5 минут, добавить томаты и тушить до мягкости."
            },
            {
                "step": 3,
                "action": "Варка капусты и картофеля",
                "heat": "Средний огонь",
                "color_and_visual": "Капуста сохраняет легкую текстуру, цвет полупрозрачно-зеленый",
                "time_min": 15,
                "description": "В кипящий бульон опустить картофель, через 4 минуты — нашинкованную капусту. Варить до состояния al dente."
            },
            {
                "step": 4,
                "action": "Соединение и варка",
                "heat": "Слабый огонь",
                "color_and_visual": "Овощи объединяются, легкие блестки жира на поверхности",
                "time_min": 6,
                "description": "Переложить пассеровку в суп, добавить соль, перец и лавровый лист. Варить на тихом огне."
            },
            {
                "step": 5,
                "action": "Отдых супа",
                "heat": "Огонь выключен",
                "color_and_visual": "Прозрачный легкий суп с яркими вкраплениями зелени",
                "time_min": 10,
                "description": "Всыпать свежую зелень, закрыть крышкой и дать отдохнуть 10 минут перед подачей."
            }
        ],
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Shchi_with_sour_cream.jpg/800px-Shchi_with_sour_cream.jpg"
    },
    {
        "id": 4,
        "name": "Щи зелёные со щавелем",
        "category": "Первые блюда",
        "portion_weight_g": 350,
        "nutrition_per_portion": {
            "calories": 210,
            "proteins": 13.5,
            "fats": 11.0,
            "carbs": 14.0
        },
        "ingredients_per_person": [
            {"name": "Куриное бедро (или говядина)", "weight_g": 100, "comment": "для легкого бульона"},
            {"name": "Щавель свежий", "weight_g": 80, "comment": "промытый, нашинкованный соломкой"},
            {"name": "Шпинат свежий", "weight_g": 30, "comment": "для баланса кислоты"},
            {"name": "Картофель", "weight_g": 60, "comment": "небольшой кубик"},
            {"name": "Морковь", "weight_g": 30, "comment": "соломка"},
            {"name": "Лук репчатый", "weight_g": 30, "comment": "мелкий кубик"},
            {"name": "Масло сливочное", "weight_g": 10, "comment": "для мягкой пассеровки"},
            {"name": "Бульон куриный", "weight_g": 350, "comment": "прозрачная основа"},
            {"name": "Яйцо куриное вареное", "weight_g": 50, "comment": "1 шт., для подачи"},
            {"name": "Зеленый лук и укроп", "weight_g": 10, "comment": "свежая зелень"},
            {"name": "Сметана 20%", "weight_g": 20, "comment": "при подаче"}
        ],
        "cooking_steps": [
            {
                "step": 1,
                "action": "Варка куриного бульона",
                "heat": "Умеренный огонь, затем тихий",
                "color_and_visual": "Светлый, полностью прозрачный отвар",
                "time_min": 40,
                "description": "Сварить куриное бедро до готовности, мясо разобрать на волокна, бульон отфильтровать."
            },
            {
                "step": 2,
                "action": "Сливочная пассеровка",
                "heat": "Слабый огонь",
                "color_and_visual": "Лук стеклянистый, морковь мягкая, без пригорания",
                "time_min": 6,
                "description": "Припустить лук и морковь на сливочном масле до мягкой текстуры."
            },
            {
                "step": 3,
                "action": "Варка картофеля",
                "heat": "Средний огонь",
                "color_and_visual": "Картофель становится крахмалистым и мягким при прокалывании",
                "time_min": 12,
                "description": "В кипящий бульон опустить картофель и пассеровку, варить до готовности картофеля."
            },
            {
                "step": 4,
                "action": "Введение зелени",
                "heat": "Минимальный огонь",
                "color_and_visual": "Щавель за секунды меняет изумрудный цвет на благородный оливковый",
                "time_min": 3,
                "description": "Всыпать нарезанный щавель и шпинат. Проварить ровно 2-3 минуты, чтобы сохранить витамины и приятную кислинку."
            },
            {
                "step": 5,
                "action": "Сервировка",
                "heat": "Огонь выключен",
                "color_and_visual": "Оливковый суп с контрастными белыми половинками яйца и сметаной",
                "time_min": 5,
                "description": "Разлить в тарелки, выложить половинки яйца, щедрую ложку сметаны и зеленый лук."
            }
        ],
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Sorrel_soup.jpg/800px-Sorrel_soup.jpg"
    },
    {
        "id": 5,
        "name": "Солянка сборная мясная",
        "category": "Первые блюда",
        "portion_weight_g": 350,
        "nutrition_per_portion": {
            "calories": 340,
            "proteins": 22.0,
            "fats": 22.0,
            "carbs": 12.0
        },
        "ingredients_per_person": [
            {"name": "Говядина отварная", "weight_g": 60, "comment": "соломка"},
            {"name": "Окорок копченый / ветчина", "weight_g": 40, "comment": "соломка"},
            {"name": "Охотничьи колбаски", "weight_g": 30, "comment": "кружочки"},
            {"name": "Огурцы соленые бочковые", "weight_g": 50, "comment": "очищенные от грубой кожи, соломка"},
            {"name": "Лук репчатый", "weight_g": 50, "comment": "тонкие перья"},
            {"name": "Томатная паста", "weight_g": 20, "comment": "для бреза"},
            {"name": "Каперсы", "weight_g": 10, "comment": "с рассолом"},
            {"name": "Маслины без косточек", "weight_g": 20, "comment": "целые или половинки"},
            {"name": "Масло сливочное", "weight_g": 10, "comment": "для пассеровки бреза"},
            {"name": "Бульон мясной крепкий", "weight_g": 300, "comment": "основа"},
            {"name": "Огуречный рассол процеженный", "weight_g": 30, "comment": "кипяченый"},
            {"name": "Лимон", "weight_g": 15, "comment": "1 кружок, очищенный от цедры при подаче"},
            {"name": "Зелень и сметана", "weight_g": 20, "comment": "для подачи"}
        ],
        "cooking_steps": [
            {
                "step": 1,
                "action": "Приготовление соляночного бреза",
                "heat": "Умеренный огонь",
                "color_and_visual": "Лук уварен с томатом до темно-кирпичного цвета и глянцевого блеска",
                "time_min": 14,
                "description": "Обжарить лук на сливочном масле, добавить томатную пасту и тушить до полного исчезновения запаха сырого томата."
            },
            {
                "step": 2,
                "action": "Припускание огурцов",
                "heat": "Слабый огонь",
                "color_and_visual": "Огурцы становятся полупрозрачными, оливковыми, сохраняя хруст",
                "time_min": 10,
                "description": "Залить огурцы небольшим количеством бульона и рассола, припустить до мягкости."
            },
            {
                "step": 3,
                "action": "Обжарка мясного набора",
                "heat": "Средне-сильный огонь",
                "color_and_visual": "Колбаски и ветчина слегка подрумяниваются, отдавая копченый жир",
                "time_min": 4,
                "description": "Слегка прогреть нарезку мясопродуктов на сухой сковороде."
            },
            {
                "step": 4,
                "action": "Сборка солянки",
                "heat": "Слабый огонь",
                "color_and_visual": "Густой темно-оранжевый суп с капельками золотистого жира",
                "time_min": 10,
                "description": "В кипящий бульон ввести брез, мясной набор, припущенные огурцы и каперсы. Варить 8-10 минут при тихом кипении."
            },
            {
                "step": 5,
                "action": "Финализация",
                "heat": "Огонь выключен",
                "color_and_visual": "Ароматный густой бульон с черными маслинами и зеленью",
                "time_min": 10,
                "description": "Ввести маслины, снять с огня, настоять 10 минут. Подавать с ломтиком лимона и сметаной."
            }
        ],
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Solyanka_01.jpg/800px-Solyanka_01.jpg"
    },
    {
        "id": 6,
        "name": "Рассольник классический с перловкой",
        "category": "Первые блюда",
        "portion_weight_g": 350,
        "nutrition_per_portion": {
            "calories": 240,
            "proteins": 13.0,
            "fats": 9.5,
            "carbs": 26.0
        },
        "ingredients_per_person": [
            {"name": "Говядина на косточке", "weight_g": 100, "comment": "отварная"},
            {"name": "Перловая крупа сухая", "weight_g": 25, "comment": "промытая"},
            {"name": "Картофель", "weight_g": 60, "comment": "брусочки"},
            {"name": "Огурцы соленые бочковые", "weight_g": 50, "comment": "соломка"},
            {"name": "Морковь", "weight_g": 35, "comment": "мелкая соломка"},
            {"name": "Лук репчатый", "weight_g": 30, "comment": "кубик"},
            {"name": "Огуречный рассол процеженный", "weight_g": 40, "comment": "прокипяченный"},
            {"name": "Масло растительное", "weight_g": 10, "comment": "для пассеровки"},
            {"name": "Бульон мясной", "weight_g": 350, "comment": "прозрачная основа"},
            {"name": "Лавровый лист и перец", "weight_g": 2, "comment": "специи"},
            {"name": "Сметана 15% и укроп", "weight_g": 20, "comment": "при подаче"}
        ],
        "cooking_steps": [
            {
                "step": 1,
                "action": "Отдельная варка перловки",
                "heat": "Умеренный огонь",
                "color_and_visual": "Крупа набухает, полупрозрачная, отвар сливается (чтобы суп не посинел)",
                "time_min": 45,
                "description": "Сварить перловую крупу в отдельной воде до мягкости, откинуть на сито и промыть горячей водой."
            },
            {
                "step": 2,
                "action": "Припускание огурцов",
                "heat": "Слабый огонь",
                "color_and_visual": "Огурцы размягчаются, цвет меняется на оливково-прозрачный",
                "time_min": 10,
                "description": "Нарезанные огурцы прогреть в сотейнике с небольшим количеством бульона."
            },
            {
                "step": 3,
                "action": "Пассеровка кореньев",
                "heat": "Средний огонь",
                "color_and_visual": "Лук и морковь золотистые, источают сладковатый аромат",
                "time_min": 7,
                "description": "Обжарить лук и морковь на масле до мягкости."
            },
            {
                "step": 4,
                "action": "Варка основы рассольника",
                "heat": "Средний огонь",
                "color_and_visual": "Бульон чистый, картофель проварился до мягкости",
                "time_min": 15,
                "description": "В кипящий бульон заложить готовую перловку и картофель, варить 12-15 минут."
            },
            {
                "step": 5,
                "action": "Заправка рассолом и сборка",
                "heat": "Тихий огонь",
                "color_and_visual": "Слегка опаловый бульон с золотистым оттенком",
                "time_min": 8,
                "description": "Добавить припущенные огурцы, пассеровку и кипяченый рассол. Проварить 5-7 минут, дать настояться под крышкой."
            }
        ],
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Rassolnik.jpg/800px-Rassolnik.jpg"
    },
    {
        "id": 7,
        "name": "Уха рыбацкая классическая",
        "category": "Первые блюда",
        "portion_weight_g": 350,
        "nutrition_per_portion": {
            "calories": 165,
            "proteins": 21.0,
            "fats": 5.5,
            "carbs": 8.0
        },
        "ingredients_per_person": [
            {"name": "Судак (филе или стейк)", "weight_g": 120, "comment": "крупные куски"},
            {"name": "Рыбная мелочь / окунь / ерш", "weight_g": 80, "comment": "в марле для первого навара"},
            {"name": "Картофель", "weight_g": 50, "comment": "крупные дольки"},
            {"name": "Морковь", "weight_g": 30, "comment": "крупные кружки"},
            {"name": "Лук репчатый", "weight_g": 30, "comment": "1 небольшая головка целиком"},
            {"name": "Корень петрушки", "weight_g": 15, "comment": "соломка"},
            {"name": "Водка", "weight_g": 10, "comment": "традиционный элемент для осветления и крепости"},
            {"name": "Вода родниковая", "weight_g": 380, "comment": "основа"},
            {"name": "Лавр, черный перец горошком", "weight_g": 2, "comment": "пряности"},
            {"name": "Укроп свежий", "weight_g": 8, "comment": "для финала"}
        ],
        "cooking_steps": [
            {
                "step": 1,
                "action": "Двойной навар",
                "heat": "Едва заметное кипение",
                "color_and_visual": "Кристально чистый, слегка золотистый бульон",
                "time_min": 35,
                "description": "Выварить мелкую рыбу в марлевом мешочке с целой луковицей и корнем петрушки. Извлечь и отжать рыбу."
            },
            {
                "step": 2,
                "action": "Варка овощей",
                "heat": "Умеренный огонь",
                "color_and_visual": "Овощи становятся полумягкими, не разваливаясь",
                "time_min": 10,
                "description": "В процеженный бульон заложить картофель и морковь, варить 10 минут."
            },
            {
                "step": 3,
                "action": "Закладка благородной рыбы",
                "heat": "Минимальный огонь без бурного кипения",
                "color_and_visual": "Мякоть судака становится молочно-белой и расслаивается на лепестки",
                "time_min": 8,
                "description": "Опустить крупные куски судака, лавровый лист и перец горошком. Томить 7-8 минут."
            },
            {
                "step": 4,
                "action": "Введение водки и трав",
                "heat": "Огонь выключен",
                "color_and_visual": "Абсолютная прозрачность бульона с яркими каплями рыбьего жира",
                "time_min": 2,
                "description": "Влить рюмку водки (устраняет запах тины и осветляет бульон), засыпать рубленый укроп."
            },
            {
                "step": 5,
                "action": "Настаивание",
                "heat": "Без нагрева",
                "color_and_visual": "Рыба оседает на дно, чистый аромат речной рыбы и укропа",
                "time_min": 7,
                "description": "Накрыть крышкой на 7 минут перед подачей."
            }
        ],
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Ukha_soup.jpg/800px-Ukha_soup.jpg"
    },
    {
        "id": 8,
        "name": "Гороховый суп с копчёностями",
        "category": "Первые блюда",
        "portion_weight_g": 350,
        "nutrition_per_portion": {
            "calories": 320,
            "proteins": 18.5,
            "fats": 15.0,
            "carbs": 28.0
        },
        "ingredients_per_person": [
            {"name": "Ребрышки свиные копченые", "weight_g": 90, "comment": "разрубленные на порции"},
            {"name": "Горох сушеный колотый", "weight_g": 60, "comment": "промытый, замоченный на 2 часа"},
            {"name": "Картофель", "weight_g": 60, "comment": "средний кубик"},
            {"name": "Морковь", "weight_g": 35, "comment": "кубик"},
            {"name": "Лук репчатый", "weight_g": 35, "comment": "мелкий кубик"},
            {"name": "Масло растительное", "weight_g": 10, "comment": "для зажарки"},
            {"name": "Вода питьевая", "weight_g": 350, "comment": "жидкая основа"},
            {"name": "Чеснок", "weight_g": 3, "comment": "измельченный"},
            {"name": "Сухарики ржаные / пшеничные", "weight_g": 20, "comment": "для подачи"},
            {"name": "Зелень и специи", "weight_g": 4, "comment": "петрушка, лавр, черный перец"}
        ],
        "cooking_steps": [
            {
                "step": 1,
                "action": "Разваривание гороха",
                "heat": "Средний до кипения, затем слабый под крышкой",
                "color_and_visual": "Горох превращается в мягкую, бархатистую желтую суспензию",
                "time_min": 50,
                "description": "Варить замоченный горох вместе с копчеными ребрышками до частичного пюрирования горошин."
            },
            {
                "step": 2,
                "action": "Золотистая пассеровка",
                "heat": "Средний огонь",
                "color_and_visual": "Лук и морковь ярко-оранжевые, карамелизованные",
                "time_min": 7,
                "description": "Обжарить лук и морковь до выраженного румяного цвета."
            },
            {
                "step": 3,
                "action": "Варка картофеля",
                "heat": "Умеренный огонь",
                "color_and_visual": "Картофель становится мягким, суп заметно густеет",
                "time_min": 15,
                "description": "Опустить в кастрюлю картофель, варить 12-15 минут, периодически помешивая со дна."
            },
            {
                "step": 4,
                "action": "Сборка и томление",
                "heat": "Минимальный огонь",
                "color_and_visual": "Кремовая текстура солнечного цвета с кусочками копченого мяса",
                "time_min": 8,
                "description": "Добавить пассеровку, специи и чеснок. Томить 5-8 минут, контролируя, чтобы горох не пригорал ко дну."
            },
            {
                "step": 5,
                "action": "Подача",
                "heat": "Огонь выключен",
                "color_and_visual": "Густой суп-пюре с хрустящими золотистыми гренками сверху",
                "time_min": 5,
                "description": "Дать постоять 10 минут. Подавать с мелко рубленной петрушкой и сухариками."
            }
        ],
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Pea_soup_with_smoked_meat.jpg/800px-Pea_soup_with_smoked_meat.jpg"
    },
    {
        "id": 9,
        "name": "Окрошка мясная на квасе",
        "category": "Первые блюда",
        "portion_weight_g": 350,
        "nutrition_per_portion": {
            "calories": 225,
            "proteins": 15.0,
            "fats": 9.5,
            "carbs": 20.0
        },
        "ingredients_per_person": [
            {"name": "Говядина отварная постная", "weight_g": 80, "comment": "кубик 5 мм"},
            {"name": "Квас белый окрошечный (несладкий)", "weight_g": 230, "comment": "ледяной"},
            {"name": "Огурцы свежие грунтовые", "weight_g": 60, "comment": "мелкий кубик"},
            {"name": "Редис свежий", "weight_g": 40, "comment": "тонкие четвертинки кружка"},
            {"name": "Картофель отварной", "weight_g": 50, "comment": "кубик"},
            {"name": "Яйцо куриное вареное", "weight_g": 50, "comment": "1 шт."},
            {"name": "Зеленый лук", "weight_g": 15, "comment": "мелко порубленный"},
            {"name": "Укроп свежий", "weight_g": 10, "comment": "мелкая рубка"},
            {"name": "Горчица русская острая", "weight_g": 5, "comment": "для заправки"},
            {"name": "Хрен столовый", "weight_g": 4, "comment": "для остроты"},
            {"name": "Сметана 20%", "weight_g": 25, "comment": "в заправку и при подаче"},
            {"name": "Соль поваренная", "weight_g": 3, "comment": "для перетирания зелени"}
        ],
        "cooking_steps": [
            {
                "step": 1,
                "action": "Растирание зелени с солью",
                "heat": "Холодный процесс (без нагрева)",
                "color_and_visual": "Зеленый лук выделяет темный изумрудный сок и источает сильный аромат",
                "time_min": 4,
                "description": "Порубленный зеленый лук поместить в ступку или миску с солью и тщательно размять пестиком."
            },
            {
                "step": 2,
                "action": "Приготовление заправки",
                "heat": "Без нагрева",
                "color_and_visual": "Желто-кремовая однородная пряная эмульсия",
                "time_min": 3,
                "description": "Яичный желток растереть с острой горчицей, хреном и столовой ложкой сметаны."
            },
            {
                "step": 3,
                "action": "Нарезка ингредиентов",
                "heat": "Без нагрева",
                "color_and_visual": "Ровный калиброванный кубик мяса, яичного белка и свежих овощей",
                "time_min": 10,
                "description": "Нарезать говядину, картофель, редис, огурцы и яичный белок аккуратным кубиком."
            },
            {
                "step": 4,
                "action": "Смешивание основы",
                "heat": "Без нагрева",
                "color_and_visual": "Пестрый салат с равномерным распределением заправки",
                "time_min": 3,
                "description": "Соединить овощи, мясо, перетертый лук и горчично-желтковую заправку. Тщательно перемешать."
            },
            {
                "step": 5,
                "action": "Заливка квасом",
                "heat": "Подача при температуре 6-8°C",
                "color_and_visual": "Пенистый светлый квас с плавающими свежими овощами и шапкой сметаны",
                "time_min": 2,
                "description": "Разложить основу по тарелкам, залить ледяным белым квасом, украсить сметаной и укропом."
            }
        ],
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Okroshka_with_kvass.jpg/800px-Okroshka_with_kvass.jpg"
    },
    {
        "id": 10,
        "name": "Окрошка на кефире",
        "category": "Первые блюда",
        "portion_weight_g": 350,
        "nutrition_per_portion": {
            "calories": 215,
            "proteins": 16.0,
            "fats": 9.0,
            "carbs": 17.5
        },
        "ingredients_per_person": [
            {"name": "Куриное филе отварное", "weight_g": 80, "comment": "охлажденное, кубик"},
            {"name": "Кефир 2.5%", "weight_g": 200, "comment": "охлажденный"},
            {"name": "Вода минеральная газированная", "weight_g": 60, "comment": "ледяная, для легкой газации"},
            {"name": "Огурцы свежие", "weight_g": 60, "comment": "соломка или кубик"},
            {"name": "Редис свежий", "weight_g": 40, "comment": "тонкая соломка"},
            {"name": "Картофель отварной", "weight_g": 50, "comment": "кубик"},
            {"name": "Яйцо куриное вареное", "weight_g": 50, "comment": "1 шт."},
            {"name": "Зеленый лук и укроп", "weight_g": 20, "comment": "обильная зелень"},
            {"name": "Сок лимона", "weight_g": 5, "comment": "для баланса кислотности"},
            {"name": "Соль и черный перец", "weight_g": 3, "comment": "по вкусу"}
        ],
        "cooking_steps": [
            {
                "step": 1,
                "action": "Охлаждение компонентов",
                "heat": "Холодильник (+4°C)",
                "color_and_visual": "Все компоненты холодные, предотвращают нагрев супа",
                "time_min": 30,
                "description": "Предварительно отварить и полностью остудить куриное филе, картофель и яйца."
            },
            {
                "step": 2,
                "action": "Нарезка",
                "heat": "Без нагрева",
                "color_and_visual": "Четкие контрастные цвета: белый, розовый, ярко-зеленый",
                "time_min": 10,
                "description": "Нарезать курицу, огурцы, редис, картофель и яйца мелкими кусочками одинакового размера."
            },
            {
                "step": 3,
                "action": "Подготовка кефирной заливки",
                "heat": "Без нагрева",
                "color_and_visual": "Однородная, слегка игристая белая жидкость с пузырьками газа",
                "time_min": 3,
                "description": "Взбить кефир с минеральной газированной водой, солью и свежевыжатым соком лимона."
            },
            {
                "step": 4,
                "action": "Объединение",
                "heat": "Без нагрева",
                "color_and_visual": "Густой белоснежный холодный суп с вкраплениями зелени и овощей",
                "time_min": 2,
                "description": "Залить подготовленную нарезку кефирной смесью, добавить измельченный зеленый лук и укроп."
            },
            {
                "step": 5,
                "action": "Выдержка перед подачей",
                "heat": "Охлаждение",
                "color_and_visual": "Равномерно просоленная, освежающая текстура",
                "time_min": 15,
                "description": "Поставить в холодильник на 15 минут для раскрытия травяных и овощных ароматов."
            }
        ],
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Okroshka_kefir.jpg/800px-Okroshka_kefir.jpg"
    },
    {
        "id": 11,
        "name": "Суп грибной из сушеных белых грибов",
        "category": "Первые блюда",
        "portion_weight_g": 350,
        "nutrition_per_portion": {
            "calories": 180,
            "proteins": 7.5,
            "fats": 8.0,
            "carbs": 20.0
        },
        "ingredients_per_person": [
            {"name": "Белые грибы сушеные", "weight_g": 25, "comment": "отборные шляпки и ножки"},
            {"name": "Картофель", "weight_g": 70, "comment": "средний кубик"},
            {"name": "Морковь", "weight_g": 35, "comment": "тонкая соломка"},
            {"name": "Лук репчатый", "weight_g": 35, "comment": "мелкий кубик"},
            {"name": "Перловая крупа (или вермишель)", "weight_g": 20, "comment": "отваренная отдельно"},
            {"name": "Масло сливочное", "weight_g": 15, "comment": "для обжарки грибов и лука"},
            {"name": "Вода (грибной настой)", "weight_g": 350, "comment": "отфильтрованная основа"},
            {"name": "Лавр, черный перец, соль", "weight_g": 3, "comment": "специи"},
            {"name": "Сметана и зелень укропа", "weight_g": 20, "comment": "для подачи"}
        ],
        "cooking_steps": [
            {
                "step": 1,
                "action": "Замачивание и настой",
                "heat": "Комнатная температура",
                "color_and_visual": "Вода приобретает цвет темного коньяка и насыщенный лесной запах",
                "time_min": 120,
                "description": "Залить сушеные белые грибы теплой водой на 2 часа. Настой аккуратно слить через марлю."
            },
            {
                "step": 2,
                "action": "Варка грибного бульона",
                "heat": "Слабый огонь",
                "color_and_visual": "Грибы становятся мягкими, упругими",
                "time_min": 30,
                "description": "Отварить грибы в настое до мягкости, вынуть шумовкой и нарезать соломкой."
            },
            {
                "step": 3,
                "action": "Сливочная обжарка грибов",
                "heat": "Средний огонь",
                "color_and_visual": "Грибы и лук приобретают аппетитный глянец и легкую золотистую корочку",
                "time_min": 8,
                "description": "Обжарить нарезанные грибы с луком и морковью на сливочном масле."
            },
            {
                "step": 4,
                "action": "Сборка супа",
                "heat": "Умеренный огонь",
                "color_and_visual": "Глубокий коричнево-янтарный цвет, чистый прозрачный навар",
                "time_min": 15,
                "description": "В кипящий грибной отвар опустить картофель, через 10 минут добавить обжаренные грибы и готовую перловку."
            },
            {
                "step": 5,
                "action": "Томление",
                "heat": "Огонь выключен",
                "color_and_visual": "Ароматный густой бульон с плавающей зеленью",
                "time_min": 10,
                "description": "Добавить соль, перец и лавровый лист. Накрыть крышкой на 10 минут. Подавать со сметаной."
            }
        ],
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Mushroom_soup.jpg/800px-Mushroom_soup.jpg"
    },
    {
        "id": 12,
        "name": "Куриный суп с домашней лапшой",
        "category": "Первые блюда",
        "portion_weight_g": 350,
        "nutrition_per_portion": {
            "calories": 220,
            "proteins": 16.5,
            "fats": 8.5,
            "carbs": 19.5
        },
        "ingredients_per_person": [
            {"name": "Суповая курица (бедро/остов)", "weight_g": 120, "comment": "на кости для чистого жира"},
            {"name": "Мука пшеничная в/с", "weight_g": 35, "comment": "для лапши"},
            {"name": "Яйцо куриное", "weight_g": 25, "comment": "1/2 шт., без добавления воды"},
            {"name": "Морковь", "weight_g": 35, "comment": "фигурная нарезка или тонкая соломка"},
            {"name": "Лук репчатый", "weight_g": 30, "comment": "целиком для бульона"},
            {"name": "Масло сливочное", "weight_g": 8, "comment": "для бережной пассеровки моркови"},
            {"name": "Вода питьевая", "weight_g": 380, "comment": "для бульона"},
            {"name": "Укроп и петрушка", "weight_g": 7, "comment": "листики без стеблей"},
            {"name": "Соль, перец горошком", "weight_g": 3, "comment": "по вкусу"}
        ],
        "cooking_steps": [
            {
                "step": 1,
                "action": "Варка прозрачного бульона",
                "heat": "Минимальное кипение (еле заметное колыхание)",
                "color_and_visual": "Прозрачный, золотистый навар с круглыми каплями куриного жира",
                "time_min": 65,
                "description": "Варить курицу с луковицей и солью, регулярно снимая пену и излишки жира. Процедить."
            },
            {
                "step": 2,
                "action": "Приготовление домашней лапши",
                "heat": "Без нагрева",
                "color_and_visual": "Плотное желтое тесто, раскатанное до толщины 1 мм, тонкая соломка",
                "time_min": 25,
                "description": "Замесить крутое тесто из муки и яйца, тонко раскатать, подсушить пласт 10 минут и нарезать тонкой лапшой."
            },
            {
                "step": 3,
                "action": "Пассеровка моркови",
                "heat": "Слабый огонь",
                "color_and_visual": "Морковь мягкая, масло приобретает яркий золотистый оттенок",
                "time_min": 6,
                "description": "Припустить морковь на сливочном масле без появления поджаристой корочки."
            },
            {
                "step": 4,
                "action": "Отваривание лапши",
                "heat": "Умеренно-сильный огонь",
                "color_and_visual": "Лапша всплывает на поверхность, бульон остается идеально прозрачным",
                "time_min": 4,
                "description": "В кипящий бульон опустить пассерованную морковь и лапшу (стряхнув с нее лишнюю муку). Варить 3-4 минуты."
            },
            {
                "step": 5,
                "action": "Подача",
                "heat": "Огонь выключен",
                "color_and_visual": "Светлый золотистый суп с нежной лапшой и свежей зеленью",
                "time_min": 5,
                "description": "Разлить по тарелкам, добавить кусочки куриного мяса и посыпать свежим укропом."
            }
        ],
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Chicken_noodle_soup.jpg/800px-Chicken_noodle_soup.jpg"
    },
    {
        "id": 13,
        "name": "Свекольник холодный",
        "category": "Первые блюда",
        "portion_weight_g": 350,
        "nutrition_per_portion": {
            "calories": 195,
            "proteins": 9.0,
            "fats": 7.5,
            "carbs": 23.0
        },
        "ingredients_per_person": [
            {"name": "Свёкла столовая (запеченная или отварная)", "weight_g": 110, "comment": "натертая на крупной терке"},
            {"name": "Свекольный отвар охлажденный", "weight_g": 220, "comment": "насыщенный настой"},
            {"name": "Огурцы свежие", "weight_g": 60, "comment": "соломка"},
            {"name": "Редис", "weight_g": 30, "comment": "кружочки или соломка"},
            {"name": "Яйцо куриное вареное", "weight_g": 50, "comment": "1 шт."},
            {"name": "Зеленый лук", "weight_g": 15, "comment": "рубленый"},
            {"name": "Укроп", "weight_g": 10, "comment": "рубленый"},
            {"name": "Уксус яблочный или сок лимона", "weight_g": 10, "comment": "фиксатор цвета и кислинки"},
            {"name": "Сахар", "weight_g": 5, "comment": "баланс вкуса"},
            {"name": "Сметана 20%", "weight_g": 25, "comment": "для подачи"},
            {"name": "Соль", "weight_g": 3, "comment": "по вкусу"}
        ],
        "cooking_steps": [
            {
                "step": 1,
                "action": "Приготовление рубинового отвара",
                "heat": "Слабый огонь, затем охлаждение",
                "color_and_visual": "Глубокий рубиново-бордовый цвет жидкости, без бурого оттенка",
                "time_min": 25,
                "description": "Проварить часть натертой свёклы в воде с лимонным соком и сахаром, процедить и охладить до ледяного состояния."
            },
            {
                "step": 2,
                "action": "Подготовка свежих овощей",
                "heat": "Без нагрева",
                "color_and_visual": "Хрустящая тонкая соломка огурцов и редиса",
                "time_min": 8,
                "description": "Нарезать огурцы и редис соломкой."
            },
            {
                "step": 3,
                "action": "Растирание лука с солью",
                "heat": "Без нагрева",
                "color_and_visual": "Выделение сока, лук становится мягким",
                "time_min": 3,
                "description": "Размять зеленый лук с солью пестиком для максимального аромата."
            },
            {
                "step": 4,
                "action": "Соединение основы",
                "heat": "Без нагрева",
                "color_and_visual": "Яркая темно-малиновая смесь с контрастными зелеными вкраплениями",
                "time_min": 3,
                "description": "Соединить печеную свёклу, овощи, зелень и залить холодным свекольным отваром."
            },
            {
                "step": 5,
                "action": "Подача со сметаной и яйцом",
                "heat": "Подача при +6°C",
                "color_and_visual": "Нежно-розовый шлейф при размешивании сметаны в рубиновом бульоне",
                "time_min": 2,
                "description": "Положить в тарелку половинку яйца и щедрую ложку сметаны, посыпать укропом."
            }
        ],
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Cold_borscht.jpg/800px-Cold_borscht.jpg"
    },
    {
        "id": 14,
        "name": "Суп с мясными фрикадельками",
        "category": "Первые блюда",
        "portion_weight_g": 350,
        "nutrition_per_portion": {
            "calories": 235,
            "proteins": 15.5,
            "fats": 11.5,
            "carbs": 17.5
        },
        "ingredients_per_person": [
            {"name": "Фарш смешанный (говядина + свинина)", "weight_g": 90, "comment": "мелкий помол"},
            {"name": "Картофель", "weight_g": 60, "comment": "кубик 1.5 см"},
            {"name": "Морковь", "weight_g": 35, "comment": "мелкая соломка"},
            {"name": "Лук репчатый", "weight_g": 35, "comment": "половина в фарш, половина в суп"},
            {"name": "Вермишель тонкая («паутинка»)", "weight_g": 15, "comment": "быстроразвариваемая"},
            {"name": "Масло растительное", "weight_g": 10, "comment": "для пассеровки"},
            {"name": "Вода или легкий бульон", "weight_g": 350, "comment": "основа"},
            {"name": "Чеснок", "weight_g": 3, "comment": "измельчить"},
            {"name": "Соль, лавр, перец, укроп", "weight_g": 3, "comment": "по вкусу"}
        ],
        "cooking_steps": [
            {
                "step": 1,
                "action": "Формовка фрикаделек",
                "heat": "Без нагрева",
                "color_and_visual": "Плотные круглые шарики диаметром 2.5 см с ровной поверхностью",
                "time_min": 10,
                "description": "Фарш вымешать с измельченным луком, солью и перцем, отбить о миску, скатать шарики по 18-20 г."
            },
            {
                "step": 2,
                "action": "Варка картофеля и пассеровка",
                "heat": "Средний огонь",
                "color_and_visual": "Морковь золотистая; картофель в кипящей воде полумягкий",
                "time_min": 12,
                "description": "В кипящую воду опустить картофель. Отдельно спассеровать лук с морковью на масле."
            },
            {
                "step": 3,
                "action": "Закладка фрикаделек",
                "heat": "Умеренный огонь",
                "color_and_visual": "Фрикадельки всплывают на поверхность, светлеют, бульон остается чистым",
                "time_min": 7,
                "description": "По одной опустить фрикадельки в тихо кипящий суп, снять появившуюся пену."
            },
            {
                "step": 4,
                "action": "Добавление вермишели",
                "heat": "Средний огонь",
                "color_and_visual": "Тонкая вермишель увеличивается в объеме, сохраняя упругость",
                "time_min": 2,
                "description": "Ввести пассеровку и вермишель. Варить ровно 2 минуты, не допуская разваривания."
            },
            {
                "step": 5,
                "action": "Финальная доводка",
                "heat": "Огонь выключен",
                "color_and_visual": "Светлый аппетитный суп с шариками мяса и зеленью укропа",
                "time_min": 5,
                "description": "Добавить лавровый лист, чеснок и рубленый укроп. Накрыть крышкой на 5 минут."
            }
        ],
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Meatball_soup.jpg/800px-Meatball_soup.jpg"
    },
    {
        "id": 15,
        "name": "Калья рыбная соленая",
        "category": "Первые блюда",
        "portion_weight_g": 350,
        "nutrition_per_portion": {
            "calories": 205,
            "proteins": 18.0,
            "fats": 7.5,
            "carbs": 16.5
        },
        "ingredients_per_person": [
            {"name": "Рыба белая жирная (палтус / судак)", "weight_g": 110, "comment": "филе без костей"},
            {"name": "Икра рыбная (или молоки)", "weight_g": 20, "comment": "традиционный элемент кальи"},
            {"name": "Огурцы соленые бочковые", "weight_g": 45, "comment": "очищенные, ломтики"},
            {"name": "Лук репчатый", "weight_g": 40, "comment": "полукольца"},
            {"name": "Огуречный рассол процеженный", "weight_g": 50, "comment": "прокипяченный"},
            {"name": "Масло сливочное", "weight_g": 10, "comment": "для пассеровки"},
            {"name": "Рыбный бульон", "weight_g": 300, "comment": "прозрачный"},
            {"name": "Шафран (или куркума)", "weight_g": 0.5, "comment": "на кончике ножа для цвета"},
            {"name": "Лимонный сок", "weight_g": 5, "comment": "для баланса"},
            {"name": "Петрушка, белый перец, соль", "weight_g": 3, "comment": "по вкусу"}
        ],
        "cooking_steps": [
            {
                "step": 1,
                "action": "Припускание огурцов",
                "heat": "Слабый огонь",
                "color_and_visual": "Огурцы полупрозрачные, оливковые, мягкие",
                "time_min": 8,
                "description": "Огурцы припустить в 50 мл рыбного бульона под крышкой."
            },
            {
                "step": 2,
                "action": "Томление лука со сливочным маслом",
                "heat": "Минимальный огонь",
                "color_and_visual": "Лук стеклянистый, без зажаривания и корочки",
                "time_min": 6,
                "description": "Потомить лук на сливочном масле до полной мягкости."
            },
            {
                "step": 3,
                "action": "Варка рассольной пряной основы",
                "heat": "Умеренный огонь",
                "color_and_visual": "Бульон приобретает теплый шафраново-желтый оттенок",
                "time_min": 10,
                "description": "Соединить рыбный бульон, рассол, шафран, припущенные огурцы и лук. Проварить 8-10 минут."
            },
            {
                "step": 4,
                "action": "Закладка рыбы и икры",
                "heat": "Тихий огонь (без бурления)",
                "color_and_visual": "Рыба становится плотной, матовой, белоснежной",
                "time_min": 7,
                "description": "Опустить порционные куски рыбы и икру в бульон. Варить 6-7 минут при очень слабом кипении."
            },
            {
                "step": 5,
                "action": "Отдых кальи",
                "heat": "Огонь выключен",
                "color_and_visual": "Плотный наваристый суп с приятным солоновато-пряным ароматом",
                "time_min": 7,
                "description": "Снять с плиты, всыпать свежую петрушку, выдержать 7 минут под крышкой."
            }
        ],
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Kalya_soup.jpg/800px-Kalya_soup.jpg"
    },
    {
        "id": 16,
        "name": "Кулеш пшённый со шкварками",
        "category": "Первые блюда",
        "portion_weight_g": 350,
        "nutrition_per_portion": {
            "calories": 310,
            "proteins": 11.5,
            "fats": 16.0,
            "carbs": 30.0
        },
        "ingredients_per_person": [
            {"name": "Пшено шлифованное", "weight_g": 45, "comment": "промытое кипятком до чистой воды"},
            {"name": "Сало свиное с мясной прослойкой", "weight_g": 40, "comment": "кубик 8 мм для шкварок"},
            {"name": "Картофель", "weight_g": 70, "comment": "кубик"},
            {"name": "Лук репчатый", "weight_g": 40, "comment": "мелкий кубик"},
            {"name": "Морковь", "weight_g": 30, "comment": "мелкий кубик"},
            {"name": "Вода или легкий мясной бульон", "weight_g": 350, "comment": "жидкая основа"},
            {"name": "Чеснок", "weight_g": 4, "comment": "измельчить"},
            {"name": "Укроп свежий", "weight_g": 7, "comment": "мелко нарубленный"},
            {"name": "Соль, перец черный горошком", "weight_g": 3, "comment": "по вкусу"}
        ],
        "cooking_steps": [
            {
                "step": 1,
                "action": "Промывка пшена от горечи",
                "heat": "Кипяток",
                "color_and_visual": "Вода становится абсолютно прозрачной, смывается окислившийся жир",
                "time_min": 5,
                "description": "Промыть пшено в трех водах, ошпарить кипятком, слить воду."
            },
            {
                "step": 2,
                "action": "Вытапливание шкварок",
                "heat": "Средний огонь",
                "color_and_visual": "Сало уменьшается в размерах, приобретая золотисто-коричневую хрустящую корочку",
                "time_min": 8,
                "description": "Вытопить нарезанное сало на сухой сковороде до образования золотистых шкварок."
            },
            {
                "step": 3,
                "action": "Обжарка лука в смальце",
                "heat": "Умеренный огонь",
                "color_and_visual": "Лук и морковь карамелизуются в вытопленном жире до румянца",
                "time_min": 6,
                "description": "В вытопившийся жир добавить лук и морковь, обжарить до приятного золотистого цвета."
            },
            {
                "step": 4,
                "action": "Варка кулеша",
                "heat": "Слабый огонь",
                "color_and_visual": "Пшено разваривается, картофель становится мягким, суп приобретает кремовую густоту",
                "time_min": 22,
                "description": "В кипящую воду опустить пшено и картофель. Варить при тихом кипении около 20 минут до мягкости."
            },
            {
                "step": 5,
                "action": "Заправка шкварками",
                "heat": "Огонь выключен",
                "color_and_visual": "Густая бархатистая текстура с ароматными кусочками шкварок и зеленью",
                "time_min": 10,
                "description": "Ввести в кастрюлю шкварки с луком, чеснок и зелень. Накрыть крышкой и дать настояться 10 минут."
            }
        ],
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Kulesh.jpg/800px-Kulesh.jpg"
    },
    {
        "id": 17,
        "name": "Похлёбка мясная старорусская с репой",
        "category": "Первые блюда",
        "portion_weight_g": 350,
        "nutrition_per_portion": {
            "calories": 220,
            "proteins": 16.0,
            "fats": 9.5,
            "carbs": 17.5
        },
        "ingredients_per_person": [
            {"name": "Говяжья мякоть (грудинка)", "weight_g": 110, "comment": "кусочки по 20 г"},
            {"name": "Репа свежая", "weight_g": 60, "comment": "брусочки"},
            {"name": "Картофель", "weight_g": 45, "comment": "кубики"},
            {"name": "Лук репчатый", "weight_g": 35, "comment": "крупные перья"},
            {"name": "Морковь", "weight_g": 30, "comment": "кружочки"},
            {"name": "Чеснок", "weight_g": 4, "comment": "раздавить ножом"},
            {"name": "Масло топленое", "weight_g": 8, "comment": "для томления"},
            {"name": "Бульон говяжий", "weight_g": 350, "comment": "прозрачная основа"},
            {"name": "Петрушка, душистый перец, соль", "weight_g": 3, "comment": "пряности"}
        ],
        "cooking_steps": [
            {
                "step": 1,
                "action": "Бланширование репы от горечи",
                "heat": "Кипящая вода",
                "color_and_visual": "Репа становится полупрозрачной, уходит лишняя резкость",
                "time_min": 3,
                "description": "Опустить нарезанную репу в кипяток на 2-3 минуты, откинуть на дуршлаг."
            },
            {
                "step": 2,
                "action": "Приготовление бульона",
                "heat": "Слабый огонь",
                "color_and_visual": "Чистый янтарный навар, мясо мягкое",
                "time_min": 75,
                "description": "Сварить кусочки говядины до мягкости на медленном огне."
            },
            {
                "step": 3,
                "action": "Томление корнеплодов",
                "heat": "Минимальный огонь (или в духовке)",
                "color_and_visual": "Овощи сохраняют форму, впитывая мясной сок",
                "time_min": 20,
                "description": "В кипящий бульон с мясом опустить репу, картофель, морковь и лук, припущенный на топленом масле."
            },
            {
                "step": 4,
                "action": "Чесночная заправка",
                "heat": "Минимальный огонь",
                "color_and_visual": "Бульон насыщенный, с выраженным ароматом печеного чеснока",
                "time_min": 5,
                "description": "Ввести раздавленный чеснок, перец душистый и соль, проварить 5 минут."
            },
            {
                "step": 5,
                "action": "Настаивание в тепле",
                "heat": "Огонь выключен",
                "color_and_visual": "Прозрачная сытная похлебка со сладковатым вкусом репы",
                "time_min": 15,
                "description": "Укутать кастрюлю или оставить в теплой духовке на 15 минут перед подачей."
            }
        ],
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Russian_meat_stew_in_clay_pot.jpg/800px-Russian_meat_stew_in_clay_pot.jpg"
    },
    {
        "id": 18,
        "name": "Ботвинья рыбная с судаком",
        "category": "Первые блюда",
        "portion_weight_g": 350,
        "nutrition_per_portion": {
            "calories": 210,
            "proteins": 19.0,
            "fats": 8.0,
            "carbs": 15.5
        },
        "ingredients_per_person": [
            {"name": "Судак или осетрина (отварная)", "weight_g": 100, "comment": "подается отдельно или на краю тарелки"},
            {"name": "Ботва свекольная молодая", "weight_g": 60, "comment": "промытая, без грубых черешков"},
            {"name": "Щавель свежий", "weight_g": 40, "comment": "соломка"},
            {"name": "Шпинат", "weight_g": 30, "comment": "соломка"},
            {"name": "Огурцы свежие", "weight_g": 50, "comment": "мелкий кубик"},
            {"name": "Квас белый хлебный (кислый)", "weight_g": 220, "comment": "ледяной"},
            {"name": "Хрен столовый тертый", "weight_g": 5, "comment": "для остроты"},
            {"name": "Горчица", "weight_g": 3, "comment": "для заправки"},
            {"name": "Зеленый лук и укроп", "weight_g": 15, "comment": "рубленая зелень"},
            {"name": "Соль", "weight_g": 3, "comment": "по вкусу"}
        ],
        "cooking_steps": [
            {
                "step": 1,
                "action": "Отваривание рыбы",
                "heat": "Слабый огонь",
                "color_and_visual": "Белоснежная плотная мякоть рыбы, охлажденная",
                "time_min": 10,
                "description": "Отварить порционный кусок рыбы с солью и лавром, вынуть и полностью остудить."
            },
            {
                "step": 2,
                "action": "Бланширование зелени",
                "heat": "Кипяток, затем ледяная вода",
                "color_and_visual": "Листья обмякают, сохраняя яркий изумрудный цвет",
                "time_min": 3,
                "description": "Припустить ботву, щавель и шпинат в кипятке 2 минуты, откинуть в холодную воду, отжать и мелко порубить."
            },
            {
                "step": 3,
                "action": "Приготовление острой заправки",
                "heat": "Без нагрева",
                "color_and_visual": "Однородный пряный соус",
                "time_min": 3,
                "description": "Смешать тертый хрен, горчицу, соль и 2 ложки кваса."
            },
            {
                "step": 4,
                "action": "Соединение зеленой массы",
                "heat": "Без нагрева",
                "color_and_visual": "Густая зеленая основа из рубленой зелени и свежих огурцов",
                "time_min": 3,
                "description": "Перемешать пюре из ботвы со свежими огурцами, зеленым луком и заправкой."
            },
            {
                "step": 5,
                "action": "Подача ботвиньи",
                "heat": "Подача с пищевым льдом (+4°C)",
                "color_and_visual": "Изумрудный суп со льдом; отварная рыба на отдельном блюдце",
                "time_min": 2,
                "description": "Залить массу квасом. Традиционно подавать с колотым льдом и рыбой на отдельной тарелке."
            }
        ],
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Botvinya.jpg/800px-Botvinya.jpg"
    },
    {
        "id": 19,
        "name": "Гречневый суп с говядиной",
        "category": "Первые блюда",
        "portion_weight_g": 350,
        "nutrition_per_portion": {
            "calories": 235,
            "proteins": 15.5,
            "fats": 9.0,
            "carbs": 23.0
        },
        "ingredients_per_person": [
            {"name": "Говядина (лопаточная часть)", "weight_g": 100, "comment": "кубик 2 см"},
            {"name": "Крупа гречневая ядрица", "weight_g": 35, "comment": "прокаленная на сковороде"},
            {"name": "Картофель", "weight_g": 60, "comment": "средний кубик"},
            {"name": "Морковь", "weight_g": 35, "comment": "соломка"},
            {"name": "Лук репчатый", "weight_g": 30, "comment": "мелкий кубик"},
            {"name": "Масло растительное", "weight_g": 10, "comment": "для пассеровки"},
            {"name": "Бульон говяжий", "weight_g": 350, "comment": "основа"},
            {"name": "Лавровый лист, черный перец, соль", "weight_g": 3, "comment": "специи"},
            {"name": "Зелень петрушки", "weight_g": 5, "comment": "для подачи"}
        ],
        "cooking_steps": [
            {
                "step": 1,
                "action": "Прокаливание гречки",
                "heat": "Средний огонь на сухой сковороде",
                "color_and_visual": "Крупинки темнеют до шоколадного цвета, появляется выраженный ореховый запах",
                "time_min": 4,
                "description": "Прогреть сухую гречку на сковороде, непрерывно помешивая, до появления стойкого аромата."
            },
            {
                "step": 2,
                "action": "Варка мясного бульона",
                "heat": "Медленный огонь",
                "color_and_visual": "Прозрачный золотисто-коричневый навар",
                "time_min": 70,
                "description": "Сварить говядину до мягкости, снимая пену. Бульон процедить."
            },
            {
                "step": 3,
                "action": "Золотистая пассеровка",
                "heat": "Умеренный огонь",
                "color_and_visual": "Лук и морковь мягкие, маслянистые, янтарного цвета",
                "time_min": 7,
                "description": "Обжарить лук и морковь на растительном масле."
            },
            {
                "step": 4,
                "action": "Закладка картофеля и гречки",
                "heat": "Средний огонь",
                "color_and_visual": "Зерна гречки раскрываются «розочками», не развариваясь в кашу",
                "time_min": 15,
                "description": "В кипящий бульон с мясом опустить картофель и прокаленную гречку. Варить 12-15 минут."
            },
            {
                "step": 5,
                "action": "Финализация вкуса",
                "heat": "Огонь выключен",
                "color_and_visual": "Прозрачный легкий суп с четкими зернами гречки и зеленью",
                "time_min": 10,
                "description": "Добавить пассеровку, специи и соль. Настоять 10 минут под крышкой. Посыпать свежей петрушкой."
            }
        ],
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Buckwheat_soup.jpg/800px-Buckwheat_soup.jpg"
    },
    {
        "id": 20,
        "name": "Солянка рыбная",
        "category": "Первые блюда",
        "portion_weight_g": 350,
        "nutrition_per_portion": {
            "calories": 220,
            "proteins": 19.5,
            "fats": 10.0,
            "carbs": 13.0
        },
        "ingredients_per_person": [
            {"name": "Лосось / сёмга (филе)", "weight_g": 60, "comment": "кубики 2.5 см"},
            {"name": "Судак или треска (филе)", "weight_g": 60, "comment": "кубики 2.5 см"},
            {"name": "Огурцы соленые бочковые", "weight_g": 45, "comment": "тонкая соломка"},
            {"name": "Лук репчатый", "weight_g": 45, "comment": "тонкие перья"},
            {"name": "Томатная паста", "weight_g": 15, "comment": "для бреза"},
            {"name": "Каперсы", "weight_g": 8, "comment": "с рассолом"},
            {"name": "Маслины черные без косточек", "weight_g": 15, "comment": "целые"},
            {"name": "Масло сливочное", "weight_g": 10, "comment": "для соуса"},
            {"name": "Бульон рыбный концентрированный", "weight_g": 300, "comment": "основа"},
            {"name": "Огуречный рассол процеженный", "weight_g": 30, "comment": "прокипяченный"},
            {"name": "Лимон", "weight_g": 15, "comment": "1 кружок при подаче"},
            {"name": "Укроп свежий, перец черный", "weight_g": 3, "comment": "по вкусу"}
        ],
        "cooking_steps": [
            {
                "step": 1,
                "action": "Приготовление томатного бреза",
                "heat": "Умеренный огонь",
                "color_and_visual": "Лук с томатом уварен до темно-кораллового блестящего оттенка",
                "time_min": 10,
                "description": "Спассеровать лук на сливочном масле, добавить томатную пасту и томить до сладковатого запаха."
            },
            {
                "step": 2,
                "action": "Припускание огурцов",
                "heat": "Слабый огонь",
                "color_and_visual": "Огурцы мягкие, полупрозрачные, оливкового цвета",
                "time_min": 8,
                "description": "Соленые огурцы припустить в сотейнике с рассолом до мягкости."
            },
            {
                "step": 3,
                "action": "Варка основы солянки",
                "heat": "Слабый огонь",
                "color_and_visual": "Ярко-оранжевый ароматный бульон с легкими искрами сливочного масла",
                "time_min": 8,
                "description": "В кипящий рыбный навар переложить брез, припущенные огурцы и каперсы, варить 8 минут."
            },
            {
                "step": 4,
                "action": "Закладка рыбы",
                "heat": "Минимальный огонь (без бурного кипения)",
                "color_and_visual": "Кусочки лосося становятся нежно-розовыми, судака — молочно-белыми",
                "time_min": 6,
                "description": "Аккуратно опустить куски лосося и судака в суп. Варить 5-6 минут, сохраняя целостность рыбы."
            },
            {
                "step": 5,
                "action": "Финишная подача",
                "heat": "Огонь выключен",
                "color_and_visual": "Богатый пряный суп с контрастными черными маслинами, зеленью и лимоном",
                "time_min": 5,
                "description": "Добавить маслины, снять с огня, настоять 5 минут. Подавать с долькой свежего лимона и укропом."
            }
        ],
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Fish_solyanka.jpg/800px-Fish_solyanka.jpg"
    }
]

def seed_database():
    """Создает таблицы и наполняет базу проверенными блюдами с фото."""
    print("[*] Инициализация структуры базы данных...")
    Base.metadata.create_all(bind=engine)

    session: Session = SessionLocal()
    try:
        # 1. Загрузка ингредиентов
        print(f"[*] Загрузка ингредиентов ({len(INGREDIENTS_DATA)} позиций)...")
        for item in INGREDIENTS_DATA:
            existing_ing = session.query(Ingredient).filter_by(id=item["id"]).first()
            if not existing_ing:
                ing = Ingredient(**item)
                session.add(ing)
            else:
                for key, value in item.items():
                    setattr(existing_ing, key, value)
        session.flush()

        # 2. Загрузка упаковок и цен
        print("[*] Генерация фабричных упаковок и расчет цен 3 сетей...")
        city_multipliers = {
            CityCodeEnum.SPB: 1.0,
            CityCodeEnum.MSK: 1.08,
            CityCodeEnum.NN: 0.94,
        }
        store_multipliers = {
            StoreNetworkEnum.BUDGET: 0.88,
            StoreNetworkEnum.STANDARD: 1.00,
            StoreNetworkEnum.PREMIUM: 1.28,
        }

        for ing_id, cfg in PACKS_CONFIG.items():
            pack = session.query(ProductPack).filter_by(ingredient_id=ing_id).first()
            if not pack:
                pack = ProductPack(
                    id=uuid.uuid4(),
                    ingredient_id=ing_id,
                    pack_title=cfg["title"],
                    pack_amount=cfg["amount"],
                    unit=cfg["unit"],
                    is_by_weight=cfg["by_weight"],
                )
                session.add(pack)
                session.flush()

            for city_enum, c_mult in city_multipliers.items():
                for store_enum, s_mult in store_multipliers.items():
                    calculated_price = round(cfg["price"] * c_mult * s_mult, 2)
                    price_record = (
                        session.query(StorePrice)
                        .filter_by(pack_id=pack.id, store_tier=store_enum, city_code=city_enum)
                        .first()
                    )
                    if not price_record:
                        price_record = StorePrice(
                            id=uuid.uuid4(),
                            pack_id=pack.id,
                            store_tier=store_enum,
                            city_code=city_enum,
                            price_rub=calculated_price,
                            in_stock=True,
                        )
                        session.add(price_record)
                    else:
                        price_record.price_rub = calculated_price

        session.flush()

        # 3. Загрузка рецептов с точными фотографиями
        print(f"[*] Загрузка каталога рецептов с фото ({len(RECIPES_DATABASE)} блюд)...")
        for r_data in RECIPES_DATABASE:
            recipe = session.query(Recipe).filter_by(id=r_data["id"]).first()
            if not recipe:
                recipe = Recipe(
                    id=r_data["id"],
                    title=r_data["title"],
                    image_url=r_data["image_url"],
                    difficulty=r_data["difficulty"],
                    meal_type=r_data["meal_type"],
                    course_type=r_data["course_type"],
                    prep_time_min=r_data["prep_time_min"],
                    calories=r_data["calories"],
                    proteins=r_data["proteins"],
                    fats=r_data["fats"],
                    carbs=r_data["carbs"],
                    tags=r_data["tags"],
                    equipment=r_data["equipment"],
                    is_batchable=r_data["is_batchable"],
                    batch_label=r_data["batch_label"],
                    chain_role=r_data["chain_role"],
                    linked_ingredient_id=r_data["linked_ingredient_id"],
                )
                session.add(recipe)
                session.flush()

                for ing_item in r_data["ingredients"]:
                    rec_ing = RecipeIngredient(
                        id=uuid.uuid4(),
                        recipe_id=recipe.id,
                        ingredient_id=ing_item["ingredient_id"],
                        amount_per_person=ing_item["amount"],
                        unit=ing_item["unit"],
                        is_pantry=ing_item["is_pantry"],
                        is_shared_side=ing_item["is_shared"],
                    )
                    session.add(rec_ing)

                for st in r_data["steps"]:
                    rec_step = RecipeStep(
                        id=uuid.uuid4(),
                        recipe_id=recipe.id,
                        step_number=st["step_number"],
                        title=st["title"],
                        instruction=st["instruction"],
                        duration_sec=st["duration_sec"],
                        heat_level=st["heat_level"],
                        visual_marker=st["visual_marker"],
                        chef_tip=st["chef_tip"],
                    )
                    session.add(rec_step)
            else:
                # Обновляем фото существующего рецепта
                recipe.image_url = r_data["image_url"]

        session.commit()
        print("[✓] База данных успешно обновлена и заполнена точными фото!")

    except Exception as e:
        session.rollback()
        print(f"[!] Ошибка: {e}", file=sys.stderr)
        raise
    finally:
        session.close()

if __name__ == "__main__":
    seed_database()
