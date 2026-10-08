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
    # 1. Сырники (золотистые творожные оладьи со сметаной)
    {
        "id": "rec_curd_pancakes",
        "title": "Пышные сырники из фермерского творога со сметаной",
        "image_url": "https://images.unsplash.com/photo-1579954115545-a95591f28bfc?auto=format&fit=crop&w=800&q=80",
        "difficulty": "Легко",
        "meal_type": MealTypeEnum.BREAKFAST,
        "course_type": CourseTypeEnum.BREAKFAST,
        "prep_time_min": 20,
        "calories": 380,
        "proteins": 31,
        "fats": 14,
        "carbs": 32,
        "tags": ["Завтрак", "Творог", "Русская кухня"],
        "equipment": ["Сковорода 26 см", "Лопатка", "Стакан"],
        "is_batchable": True,
        "batch_label": "Хранение 48ч",
        "chain_role": ChainRoleEnum.INITIATOR,
        "linked_ingredient_id": "ing_curd_5",
        "ingredients": [
            {"ingredient_id": "ing_curd_5", "amount": 180.0, "unit": "г", "is_pantry": False, "is_shared": False},
            {"ingredient_id": "ing_eggs", "amount": 1.0, "unit": "шт", "is_pantry": False, "is_shared": False},
            {"ingredient_id": "ing_flour", "amount": 35.0, "unit": "г", "is_pantry": True, "is_shared": False},
            {"ingredient_id": "ing_sour_cream", "amount": 40.0, "unit": "г", "is_pantry": False, "is_shared": False},
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Формовка творожных шайбочек",
                "instruction": "Творог разомните вилкой, смешайте с яйцом, сахаром и мукой. Припылите доску мукой, сформируйте шарики и подкрутите перевернутым стаканом для идеальной формы.",
                "duration_sec": 300,
                "heat_level": None,
                "visual_marker": "Ровные плотные ресторанные шайбочки с высокими бортиками.",
                "chef_tip": "Вращение стаканом центрует форму без липнущих к рукам комочков.",
            },
            {
                "step_number": 2,
                "title": "Томление под крышкой",
                "instruction": "Обжаривайте на умеренном огне по 3.5 минуты с каждой стороны до золотистого румянца.",
                "duration_sec": 420,
                "heat_level": "Средне-слабый огонь (4 из 9)",
                "visual_marker": "Золотисто-медовая корочка, серединка упруго пружинит.",
                "chef_tip": "Не делайте сильный огонь, чтобы творог пропекся внутри.",
            },
        ],
    },
    # 2. Пшенная каша с тыквой
    {
        "id": "rec_millet_pumpkin",
        "title": "Традиционная пшенная каша с печеной тыквой на воде",
        "image_url": "https://images.unsplash.com/photo-1517673132405-a56a62b18caf?auto=format&fit=crop&w=800&q=80",
        "difficulty": "Легко",
        "meal_type": MealTypeEnum.BREAKFAST,
        "course_type": CourseTypeEnum.BREAKFAST,
        "prep_time_min": 22,
        "calories": 310,
        "proteins": 9,
        "fats": 5,
        "carbs": 58,
        "tags": ["Завтрак", "Без лактозы", "Постное"],
        "equipment": ["Кастрюля с толстым дном"],
        "is_batchable": True,
        "batch_label": "Каша на 2 дня",
        "chain_role": ChainRoleEnum.INITIATOR,
        "linked_ingredient_id": "ing_millet",
        "ingredients": [
            {"ingredient_id": "ing_millet", "amount": 70.0, "unit": "г", "is_pantry": False, "is_shared": False},
            {"ingredient_id": "ing_pumpkin", "amount": 100.0, "unit": "г", "is_pantry": False, "is_shared": False},
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Ошпаривание крупы и варка",
                "instruction": "Пшено ошпарьте кипятком в сите, переложите в кастрюлю, добавьте 240 мл воды и нарезанную кубиками тыкву. Варите 18 минут под крышкой.",
                "duration_sec": 1080,
                "heat_level": "Тихий огонь (3 из 9)",
                "visual_marker": "Крупа впитала воду и стала бархатистой, тыква размягчилась.",
                "chef_tip": "Ошпаривание кипятком полностью убирает природную горчинку пшена.",
            }
        ],
    },
    # 3. Овсяная каша
    {
        "id": "rec_monastery_oatmeal",
        "title": "Монастырская овсяная каша на воде с яблоком",
        "image_url": "https://images.unsplash.com/photo-1584776296944-ab6fb57b0bdd?auto=format&fit=crop&w=800&q=80",
        "difficulty": "Очень легко",
        "meal_type": MealTypeEnum.BREAKFAST,
        "course_type": CourseTypeEnum.BREAKFAST,
        "prep_time_min": 12,
        "calories": 270,
        "proteins": 8,
        "fats": 4,
        "carbs": 52,
        "tags": ["Завтрак", "Без лактозы", "Постное"],
        "equipment": ["Сотейник", "Лопатка"],
        "is_batchable": False,
        "batch_label": "Без лактозы",
        "chain_role": ChainRoleEnum.INDEPENDENT,
        "linked_ingredient_id": None,
        "ingredients": [
            {"ingredient_id": "ing_oats", "amount": 65.0, "unit": "г", "is_pantry": False, "is_shared": False},
            {"ingredient_id": "ing_apples", "amount": 100.0, "unit": "г", "is_pantry": False, "is_shared": False},
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Томление овса на воде",
                "instruction": "Залейте хлопья кипятком (220 мл), варите 8 минут на слабом огне со щепоткой соли.",
                "duration_sec": 480,
                "heat_level": "Тихий огонь (2 из 9)",
                "visual_marker": "Хлопья стали нежными и шелковистыми.",
                "chef_tip": "Варка на воде раскрывает природный ореховый аромат овсянки.",
            }
        ],
    },
    # 4. Домашние картофельные драники (настоящие хрустящие оладьи)
    {
        "id": "rec_potato_draniki",
        "title": "Хрустящие картофельные драники по-домашнему",
        "image_url": "https://images.unsplash.com/photo-1599488615731-7e5c2823ff28?auto=format&fit=crop&w=800&q=80",
        "difficulty": "Легко",
        "meal_type": MealTypeEnum.BREAKFAST,
        "course_type": CourseTypeEnum.BREAKFAST,
        "prep_time_min": 20,
        "calories": 340,
        "proteins": 10,
        "fats": 12,
        "carbs": 46,
        "tags": ["Завтрак", "Без лактозы", "Русская кухня"],
        "equipment": ["Терка", "Сковорода 26 см"],
        "is_batchable": False,
        "batch_label": "Без лактозы",
        "chain_role": ChainRoleEnum.INDEPENDENT,
        "linked_ingredient_id": None,
        "ingredients": [
            {"ingredient_id": "ing_potatoes", "amount": 220.0, "unit": "г", "is_pantry": False, "is_shared": False},
            {"ingredient_id": "ing_eggs", "amount": 1.0, "unit": "шт", "is_pantry": False, "is_shared": False},
            {"ingredient_id": "ing_flour", "amount": 20.0, "unit": "г", "is_pantry": True, "is_shared": False},
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Натирание и отжим",
                "instruction": "Натрите картофель на средней терке, слегка отожмите лишний сок. Смешайте с яйцом и мукой.",
                "duration_sec": 300,
                "heat_level": None,
                "visual_marker": "Вязкая масса без лужи сока на дне.",
                "chef_tip": "Отжим картофеля дает гарантированно хрустящую корочку.",
            },
            {
                "step_number": 2,
                "title": "Обжаривание оладий",
                "instruction": "Жарьте на сковороде по 3.5 минуты с каждой стороны до золотистой корочки.",
                "duration_sec": 420,
                "heat_level": "Средний огонь (6 из 9)",
                "visual_marker": "Аппетитная янтарная корочка по краям.",
                "chef_tip": "100% безлактозный сытный завтрак.",
            },
        ],
    },
    # 5. Классический борщ со свеклой и говядиной
    {
        "id": "rec_classic_borscht",
        "title": "Классический домашний борщ со свеклой и говядиной",
        "image_url": "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=800&q=80",
        "difficulty": "Средняя",
        "meal_type": MealTypeEnum.LUNCH,
        "course_type": CourseTypeEnum.SOUP,
        "prep_time_min": 45,
        "calories": 360,
        "proteins": 29,
        "fats": 11,
        "carbs": 34,
        "tags": ["Суп", "Говядина", "Русская кухня"],
        "equipment": ["Кастрюля 3 л", "Терка"],
        "is_batchable": True,
        "batch_label": "Борщ на 2 дня",
        "chain_role": ChainRoleEnum.INITIATOR,
        "linked_ingredient_id": "ing_beef_stew",
        "ingredients": [
            {"ingredient_id": "ing_beef_stew", "amount": 130.0, "unit": "г", "is_pantry": False, "is_shared": False},
            {"ingredient_id": "ing_beets", "amount": 90.0, "unit": "г", "is_pantry": False, "is_shared": False},
            {"ingredient_id": "ing_cabbage", "amount": 80.0, "unit": "г", "is_pantry": False, "is_shared": False},
            {"ingredient_id": "ing_potatoes", "amount": 80.0, "unit": "г", "is_pantry": False, "is_shared": False},
            {"ingredient_id": "ing_dill", "amount": 10.0, "unit": "г", "is_pantry": False, "is_shared": False},
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Варка прозрачного мясного бульона",
                "instruction": "Говядину нарежьте кусочками 2.5 см, залейте водой, доведите до кипения и снимите пену. Варите 25 минут на тихом огне.",
                "duration_sec": 1500,
                "heat_level": "Тихий огонь (3 из 9)",
                "visual_marker": "Чистый прозрачный бульон с янтарными капельками.",
                "chef_tip": "Снятие первой пены гарантирует кристальную прозрачность.",
            },
            {
                "step_number": 2,
                "title": "Закладка свеклы и капусты",
                "instruction": "Добавьте картофель кубиком, нашинкованную капусту и натертую свеклу. Варите 15 минут.",
                "duration_sec": 900,
                "heat_level": "Слабый огонь (4 из 9)",
                "visual_marker": "Борщ приобретает благородный рубиновый цвет.",
                "chef_tip": "На второй день борщ настаивается и становится еще вкуснее!",
            },
        ],
    },
    # 6. Русские щи из свежей капусты
    {
        "id": "rec_fresh_shchi",
        "title": "Традиционные русские щи из свежей капусты с цыпленком",
        "image_url": "https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=800&q=80",
        "difficulty": "Легко",
        "meal_type": MealTypeEnum.LUNCH,
        "course_type": CourseTypeEnum.SOUP,
        "prep_time_min": 30,
        "calories": 290,
        "proteins": 28,
        "fats": 7,
        "carbs": 26,
        "tags": ["Суп", "Птица", "Русская кухня", "Без лактозы"],
        "equipment": ["Кастрюля 2.5 л", "Нож шефа"],
        "is_batchable": True,
        "batch_label": "Щи на 2 дня",
        "chain_role": ChainRoleEnum.INITIATOR,
        "linked_ingredient_id": "ing_chicken_breast",
        "ingredients": [
            {"ingredient_id": "ing_chicken_breast", "amount": 120.0, "unit": "г", "is_pantry": False, "is_shared": False},
            {"ingredient_id": "ing_cabbage", "amount": 120.0, "unit": "г", "is_pantry": False, "is_shared": False},
            {"ingredient_id": "ing_potatoes", "amount": 90.0, "unit": "г", "is_pantry": False, "is_shared": False},
            {"ingredient_id": "ing_carrots", "amount": 50.0, "unit": "г", "is_pantry": False, "is_shared": False},
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Варка куриного бульона",
                "instruction": "Куриное филе нарежьте кубиком, опустите в воду, варите 10 минут, снимая пенку.",
                "duration_sec": 600,
                "heat_level": "Средний огонь (5 из 9)",
                "visual_marker": "Золотистый легкий бульон.",
                "chef_tip": "Куриное филе варится гораздо быстрее говядины.",
            },
            {
                "step_number": 2,
                "title": "Закладка овощей",
                "instruction": "Всыпьте тонко нашинкованную капусту, картофель и тертую морковь. Варите 14 минут.",
                "duration_sec": 840,
                "heat_level": "Тихий огонь (3 из 9)",
                "visual_marker": "Капуста стала прозрачной и мягкой.",
                "chef_tip": "Легкое сытное обеденное блюдо без капли лишнего жира.",
            },
        ],
    },
    # 7. Поморская уха из мурманской трески
    {
        "id": "rec_pomor_ukha",
        "title": "Поморская уха из мурманской трески с картофелем",
        "image_url": "https://images.unsplash.com/photo-1594041680534-e8c8cdebd659?auto=format&fit=crop&w=800&q=80",
        "difficulty": "Легко",
        "meal_type": MealTypeEnum.LUNCH,
        "course_type": CourseTypeEnum.SOUP,
        "prep_time_min": 25,
        "calories": 280,
        "proteins": 31,
        "fats": 5,
        "carbs": 25,
        "tags": ["Суп", "Рыба", "Русская кухня", "Без лактозы"],
        "equipment": ["Кастрюля 2.5 л", "Шумовка"],
        "is_batchable": True,
        "batch_label": "Рыбный суп",
        "chain_role": ChainRoleEnum.INITIATOR,
        "linked_ingredient_id": "ing_cod_fillet",
        "ingredients": [
            {"ingredient_id": "ing_cod_fillet", "amount": 160.0, "unit": "г", "is_pantry": False, "is_shared": False},
            {"ingredient_id": "ing_potatoes", "amount": 110.0, "unit": "г", "is_pantry": False, "is_shared": False},
            {"ingredient_id": "ing_carrots", "amount": 50.0, "unit": "г", "is_pantry": False, "is_shared": False},
            {"ingredient_id": "ing_dill", "amount": 15.0, "unit": "г", "is_pantry": False, "is_shared": False},
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Варка овощного отвара",
                "instruction": "Картофель и морковь нарежьте ломтиками, сварите до полуготовности (10 минут).",
                "duration_sec": 600,
                "heat_level": "Средний огонь (6 из 9)",
                "visual_marker": "Картофель легко прокалывается ножом.",
                "chef_tip": "Рыба варится всего 6-7 минут, поэтому овощи закладываются первыми.",
            },
            {
                "step_number": 2,
                "title": "Закладка трески",
                "instruction": "Опустите крупные кусочки трески (3х3 см), убавьте огонь до минимума и томите 7 минут. Всыпьте свежий укроп.",
                "duration_sec": 420,
                "heat_level": "Слабый огонь (2 из 9)",
                "visual_marker": "Рыба распадается на перламутровые сочные лепестки.",
                "chef_tip": "Не допускайте бурного кипения, чтобы треска не разварилась в пюре.",
            },
        ],
    },
    # 8. Мясные котлеты с отварным картофелем
    {
        "id": "rec_beef_cutlets_potatoes",
        "title": "Домашние мясные котлеты с отварным картофелем",
        "image_url": "https://images.unsplash.com/photo-1529042410759-befb1204b468?auto=format&fit=crop&w=800&q=80",
        "difficulty": "Легко",
        "meal_type": MealTypeEnum.LUNCH,
        "course_type": CourseTypeEnum.MAIN,
        "prep_time_min": 30,
        "calories": 460,
        "proteins": 36,
        "fats": 16,
        "carbs": 42,
        "tags": ["Обед", "Говядина", "Русская кухня"],
        "equipment": ["Сковорода с крышкой", "Кастрюля"],
        "is_batchable": True,
        "batch_label": "Котлеты на 2 дня",
        "chain_role": ChainRoleEnum.INITIATOR,
        "linked_ingredient_id": "ing_beef_mince",
        "ingredients": [
            {"ingredient_id": "ing_beef_mince", "amount": 160.0, "unit": "г", "is_pantry": False, "is_shared": False},
            {"ingredient_id": "ing_potatoes", "amount": 180.0, "unit": "г", "is_pantry": False, "is_shared": False},
            {"ingredient_id": "ing_dill", "amount": 10.0, "unit": "г", "is_pantry": False, "is_shared": False},
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Формовка и обжарка котлет",
                "instruction": "Фарш посолите, отбейте об ладони и сформируйте котлеты. Обжаривайте по 4 минуты с каждой стороны.",
                "duration_sec": 480,
                "heat_level": "Средний огонь (6 из 9)",
                "visual_marker": "Румяная плотная корочка с обеих сторон.",
                "chef_tip": "Отбивание фарша делает котлеты сочными без добавления хлебного мякиша.",
            },
            {
                "step_number": 2,
                "title": "Варка картофеля",
                "instruction": "Сварите картофель 18 минут до рассыпчатости, посыпьте укропом.",
                "duration_sec": 1080,
                "heat_level": "Средний огонь (5 из 9)",
                "visual_marker": "Картофель мягкий и рассыпчатый.",
                "chef_tip": "Классическое сытное домашнее второе блюдо.",
            },
        ],
    },
    # 9. Гречка по-купечески с цыпленком
    {
        "id": "rec_merchant_buckwheat",
        "title": "Гречка по-купечески с кусочками филе цыпленка",
        "image_url": "https://images.unsplash.com/photo-1543339308-43e59d6b73a6?auto=format&fit=crop&w=800&q=80",
        "difficulty": "Очень легко",
        "meal_type": MealTypeEnum.LUNCH,
        "course_type": CourseTypeEnum.MAIN,
        "prep_time_min": 25,
        "calories": 410,
        "proteins": 38,
        "fats": 9,
        "carbs": 45,
        "tags": ["Обед", "Птица", "Русская кухня", "Без лактозы"],
        "equipment": ["Глубокая сковорода или сотейник"],
        "is_batchable": True,
        "batch_label": "Блюдо на 2 дня",
        "chain_role": ChainRoleEnum.INITIATOR,
        "linked_ingredient_id": "ing_chicken_breast",
        "ingredients": [
            {"ingredient_id": "ing_chicken_breast", "amount": 160.0, "unit": "г", "is_pantry": False, "is_shared": False},
            {"ingredient_id": "ing_buckwheat", "amount": 75.0, "unit": "г", "is_pantry": False, "is_shared": False},
            {"ingredient_id": "ing_carrots", "amount": 50.0, "unit": "г", "is_pantry": False, "is_shared": False},
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Обжарка цыпленка с морковью",
                "instruction": "Кусочки филе быстро обжарьте с морковью 4 минуты на сильном огне до побеления мяса.",
                "duration_sec": 240,
                "heat_level": "Сильный огонь (7 из 9)",
                "visual_marker": "Мясо подрумянилось и запечатало сок.",
                "chef_tip": "Быстрая обжарка сохраняет сочность грудки.",
            },
            {
                "step_number": 2,
                "title": "Томление гречки в мясном соке",
                "instruction": "Всыпьте промытую крупу, залейте 160 мл горячей воды, закройте крышкой и томите 16 минут на тихом огне.",
                "duration_sec": 960,
                "heat_level": "Тихий огонь (2 из 9)",
                "visual_marker": "Вода полностью впиталась, гречка стала рассыпчатой.",
                "chef_tip": "Гречка пропитывается ароматом птицы без капли лишнего масла.",
            },
        ],
    },
    # 10. Тушеная капуста с говядиной
    {
        "id": "rec_stewed_cabbage_beef",
        "title": "Тушеная капуста с говядиной по-русски",
        "image_url": "https://images.unsplash.com/photo-1574484284002-952d92456975?auto=format&fit=crop&w=800&q=80",
        "difficulty": "Легко",
        "meal_type": MealTypeEnum.DINNER,
        "course_type": CourseTypeEnum.MAIN,
        "prep_time_min": 35,
        "calories": 370,
        "proteins": 35,
        "fats": 14,
        "carbs": 22,
        "tags": ["Ужин", "Говядина", "Русская кухня", "Без лактозы"],
        "equipment": ["Сотейник с крышкой"],
        "is_batchable": True,
        "batch_label": "Рагу на 2 дня",
        "chain_role": ChainRoleEnum.INITIATOR,
        "linked_ingredient_id": "ing_beef_stew",
        "ingredients": [
            {"ingredient_id": "ing_beef_stew", "amount": 160.0, "unit": "г", "is_pantry": False, "is_shared": False},
            {"ingredient_id": "ing_cabbage", "amount": 180.0, "unit": "г", "is_pantry": False, "is_shared": False},
            {"ingredient_id": "ing_carrots", "amount": 50.0, "unit": "г", "is_pantry": False, "is_shared": False},
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Томление мяса и капусты",
                "instruction": "Мясо нарежьте брусочками, обжарьте 5 минут. Добавьте нашинкованную капусту, морковь, 60 мл воды и тушите 25 минут под крышкой.",
                "duration_sec": 1500,
                "heat_level": "Тихий огонь (3 из 9)",
                "visual_marker": "Капуста стала карамельно-мягкой, мясо тает во рту.",
                "chef_tip": "Сытный традиционный низкоуглеводный домашний ужин.",
            }
        ],
    },
    # 11. Филе трески с картофелем
    {
        "id": "rec_baked_cod_potatoes",
        "title": "Филе мурманской трески с картофелем и укропом",
        "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=800&q=80",
        "difficulty": "Легко",
        "meal_type": MealTypeEnum.DINNER,
        "course_type": CourseTypeEnum.MAIN,
        "prep_time_min": 28,
        "calories": 340,
        "proteins": 36,
        "fats": 6,
        "carbs": 32,
        "tags": ["Ужин", "Рыба", "Без мяса", "Без лактозы"],
        "equipment": ["Форма для запекания"],
        "is_batchable": True,
        "batch_label": "Рыбный день",
        "chain_role": ChainRoleEnum.INITIATOR,
        "linked_ingredient_id": "ing_cod_fillet",
        "ingredients": [
            {"ingredient_id": "ing_cod_fillet", "amount": 180.0, "unit": "г", "is_pantry": False, "is_shared": False},
            {"ingredient_id": "ing_potatoes", "amount": 160.0, "unit": "г", "is_pantry": False, "is_shared": False},
            {"ingredient_id": "ing_dill", "amount": 15.0, "unit": "г", "is_pantry": False, "is_shared": False},
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Запекание рыбы с картофелем",
                "instruction": "Выложите тонкие слайсы картофеля и треску в форму, посыпьте укропом. Запекайте 20 минут при 180°C.",
                "duration_sec": 1200,
                "heat_level": "Духовка 180°C",
                "visual_marker": "Мякоть рыбы распадается вилкой на сочные лепестки.",
                "chef_tip": "Диетическая белая рыба богата белком и фосфором.",
            }
        ],
    },
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
