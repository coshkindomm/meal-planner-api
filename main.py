from __future__ import annotations

import math
import os
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, joinedload, sessionmaker

# Импортируем ORM-модели из файла backend_models.py
from backend_models import (
    Base,
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

# ==========================================
# Подключение к базе данных
# ==========================================
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///meal_planner.db")
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Генератор сессии базы данных для FastAPI Dependency Injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================================
# Pydantic-схемы (API DTO)
# ==========================================
class PantryItemDTO(BaseModel):
    id: str
    name: str
    checked: bool


class MealTypesConfig(BaseModel):
    breakfast: bool = True
    lunch: bool = True
    dinner: bool = True
    snack: bool = False


class MenuGenerateRequest(BaseModel):
    city: str = Field(default="SPB", description="Код города: SPB, MSK, NN")
    days_count: int = Field(default=5, ge=1, le=14, description="Количество дней (1-14)")
    people_count: int = Field(default=2, ge=1, le=10, description="Количество персон (1-10)")
    lunch_mode: str = Field(default="both", description="first_only, second_only, both")
    meal_types: MealTypesConfig = Field(default_factory=MealTypesConfig)
    exclusions: List[str] = Field(default_factory=list, description="Список исключений")
    batch_cooking_enabled: bool = True
    weighted_produce_enabled: bool = True
    pantry_list: List[PantryItemDTO] = Field(default_factory=list)


class RecipeStepDTO(BaseModel):
    step_number: int
    title: str
    instruction: str
    duration_sec: int
    heat_level: Optional[str] = None
    visual_marker: Optional[str] = None
    chef_tip: Optional[str] = None


class IngredientDTO(BaseModel):
    id: str
    name: str
    amount_per_person: float
    unit: str = "г"
    category: str
    is_pantry: bool = False
    is_shared_side: bool = False


class RecipeDTO(BaseModel):
    id: str
    title: str
    image_url: str
    difficulty: str
    meal_type: str
    course_type: str
    prep_time_min: int
    calories: int
    proteins: int
    fats: int
    carbs: int
    tags: List[str]
    equipment: List[str]
    is_batchable: bool
    batch_label: Optional[str] = None
    chain_role: str
    linked_ingredient_id: Optional[str] = None
    base_ingredients: List[IngredientDTO]
    steps: List[RecipeStepDTO]


class DayMenuDTO(BaseModel):
    day_number: int
    meals: Dict[str, Optional[RecipeDTO]]


class BasketItemDTO(BaseModel):
    id: str
    name: str
    category: str
    unit: str
    pack_weight: float
    required_amount: float
    pack_count: int
    total_bought: float
    leftover: float
    is_weighted: bool
    base_price_total: float


class StoreSummaryDTO(BaseModel):
    id: str
    name: str
    badge: str
    total_rub: int


class BasketResponse(BaseModel):
    packed_items: List[BasketItemDTO]
    store_totals: List[StoreSummaryDTO]
    city: str
    currency: str = "RUB"


class MenuGenerateResponse(BaseModel):
    days: List[DayMenuDTO]
    basket: BasketResponse


app = FastAPI(
    title="Zero-Waste Meal Planner API",
    description="Бэкенд-сервис для составления сбалансированного меню и расчета цен супермаркетов",
    version="1.1.0",
)

# Разрешаем вызовы из Telegram WebApp и локальных клиентов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def recipe_to_dto(r: Recipe) -> RecipeDTO:
    """Конвертирует ORM-модель Recipe в Pydantic RecipeDTO."""
    return RecipeDTO(
        id=r.id,
        title=r.title,
        image_url=r.image_url,
        difficulty=r.difficulty,
        meal_type=r.meal_type.value if hasattr(r.meal_type, "value") else str(r.meal_type),
        course_type=r.course_type.value if hasattr(r.course_type, "value") else str(r.course_type),
        prep_time_min=r.prep_time_min,
        calories=r.calories,
        proteins=r.proteins,
        fats=r.fats,
        carbs=r.carbs,
        tags=r.tags or [],
        equipment=r.equipment or [],
        is_batchable=r.is_batchable,
        batch_label=r.batch_label,
        chain_role=r.chain_role.value if hasattr(r.chain_role, "value") else str(r.chain_role),
        linked_ingredient_id=r.linked_ingredient_id,
        base_ingredients=[
            IngredientDTO(
                id=ri.ingredient.id,
                name=ri.ingredient.name,
                amount_per_person=ri.amount_per_person,
                unit=ri.unit,
                category=ri.ingredient.category,
                is_pantry=ri.is_pantry,
                is_shared_side=ri.is_shared_side,
            )
            for ri in r.ingredients
        ],
        steps=[
            RecipeStepDTO(
                step_number=s.step_number,
                title=s.title,
                instruction=s.instruction,
                duration_sec=s.duration_sec,
                heat_level=s.heat_level,
                visual_marker=s.visual_marker,
                chef_tip=s.chef_tip,
            )
            for s in r.steps
        ],
    )


def is_recipe_allowed(recipe: Recipe, exclusions: List[str]) -> bool:
    """Проверяет рецепт на соответствие ограничениям по флагам аллергенов и названию."""
    if not exclusions:
        return True

    for excl in exclusions:
        raw = excl.lower().replace("без ", "").strip()
        if not raw:
            continue

        if "лактоз" in raw:
            if any(ri.ingredient.is_lactose for ri in recipe.ingredients):
                return False
        elif "свинин" in raw:
            if any(ri.ingredient.is_pork for ri in recipe.ingredients):
                return False
        elif "говяд" in raw:
            if any(ri.ingredient.is_beef for ri in recipe.ingredients):
                return False
        elif "индейк" in raw or "куриц" in raw or "цыплен" in raw:
            if any(ri.ingredient.is_poultry for ri in recipe.ingredients):
                return False
        elif "рыб" in raw:
            if any(ri.ingredient.is_fish for ri in recipe.ingredients):
                return False
        elif "глютен" in raw:
            if any(ri.ingredient.has_gluten for ri in recipe.ingredients):
                return False
        elif "лук" in raw:
            if any(ri.ingredient.is_onion for ri in recipe.ingredients):
                return False
        elif "чеснок" in raw:
            if any(ri.ingredient.is_garlic for ri in recipe.ingredients):
                return False
        elif "гриб" in raw:
            if any(ri.ingredient.is_mushrooms for ri in recipe.ingredients):
                return False
        else:
            # Пользовательские произвольные исключения
            if raw in recipe.title.lower():
                return False
            if any(raw in ri.ingredient.name.lower() for ri in recipe.ingredients):
                return False

    return True


# ==========================================
# Эндпоинты API
# ==========================================
@app.get("/api/health", tags=["Системные"])
async def health_check(db: Session = Depends(get_db)):
    """Проверка доступности API и подключения к базе данных."""
    recipe_count = db.query(Recipe).count()
    return {
        "status": "ok",
        "service": "Zero-Waste Meal Planner API",
        "database": "connected",
        "recipes_in_db": recipe_count,
    }


@app.get("/api/recipes", response_model=List[RecipeDTO], tags=["Рецепты"])
async def get_all_recipes(db: Session = Depends(get_db)):
    """Получение всех рецептов из базы данных."""
    recipes = (
        db.query(Recipe)
        .options(
            joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient),
            joinedload(Recipe.steps),
        )
        .all()
    )
    return [recipe_to_dto(r) for r in recipes]


@app.post("/api/menu/generate", response_model=MenuGenerateResponse, tags=["Планировщик"])
async def generate_menu_endpoint(
    payload: MenuGenerateRequest, db: Session = Depends(get_db)
):
    """
    Генерирует сбалансированное меню из базы данных с учетом исключений
    и рассчитывает стоимость корзин супермаркетов.
    """
    all_recipes = (
        db.query(Recipe)
        .options(
            joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient),
            joinedload(Recipe.steps),
        )
        .all()
    )

    # Фильтрация по исключениям
    safe_recipes = [r for r in all_recipes if is_recipe_allowed(r, payload.exclusions)]
    if not safe_recipes:
        safe_recipes = all_recipes

    generated_days: List[DayMenuDTO] = []

    # Распределение блюд по дням
    for day_idx in range(1, payload.days_count + 1):
        is_first_day = day_idx == 1
        day_meals: Dict[str, Optional[RecipeDTO]] = {}

        def get_pool(m_type: MealTypeEnum, c_type: Optional[CourseTypeEnum] = None):
            res = [
                r for r in safe_recipes
                if r.meal_type == m_type
                and (c_type is None or r.course_type == c_type)
                and not (is_first_day and r.chain_role == "consumer")
            ]
            if not res and c_type:
                res = [r for r in safe_recipes if r.meal_type == m_type]
            return res or safe_recipes

        if payload.meal_types.breakfast:
            b_pool = get_pool(MealTypeEnum.BREAKFAST)
            day_meals["breakfast"] = recipe_to_dto(b_pool[(day_idx - 1) % len(b_pool)])

        if payload.meal_types.lunch:
            if payload.lunch_mode in ["first_only", "both"]:
                soups = get_pool(MealTypeEnum.LUNCH, CourseTypeEnum.SOUP)
                day_meals["lunch_soup"] = recipe_to_dto(soups[(day_idx - 1) % len(soups)])
            if payload.lunch_mode in ["second_only", "both"]:
                mains = get_pool(MealTypeEnum.LUNCH, CourseTypeEnum.MAIN)
                day_meals["lunch_main"] = recipe_to_dto(mains[(day_idx - 1) % len(mains)])

        if payload.meal_types.dinner:
            d_pool = get_pool(MealTypeEnum.DINNER, CourseTypeEnum.MAIN)
            day_meals["dinner"] = recipe_to_dto(d_pool[(day_idx - 1) % len(d_pool)])

        if payload.meal_types.snack:
            s_pool = get_pool(MealTypeEnum.SNACK)
            day_meals["snack"] = recipe_to_dto(s_pool[(day_idx - 1) % len(s_pool)])

        generated_days.append(DayMenuDTO(day_number=day_idx, meals=day_meals))

    # Расчет потребности в ингредиентах
    raw_demand: Dict[str, float] = {}
    pantry_checked = {p.id for p in payload.pantry_list if p.checked}

    for day in generated_days:
        for meal in day.meals.values():
            if not meal:
                continue
            for ing in meal.base_ingredients:
                if ing.is_pantry and ing.id in pantry_checked:
                    continue
                qty = ing.amount_per_person * payload.people_count
                raw_demand[ing.id] = raw_demand.get(ing.id, 0.0) + qty

    # Расчет упаковок и цен из базы данных
    packed_items: List[BasketItemDTO] = []
    city_enum = getattr(CityCodeEnum, payload.city, CityCodeEnum.SPB)

    # Кэшируем упаковки и цены из БД
    all_packs = (
        db.query(ProductPack)
        .options(joinedload(ProductPack.prices), joinedload(ProductPack.ingredient))
        .all()
    )
    packs_map = {p.ingredient_id: p for p in all_packs}

    for ing_id, required_qty in raw_demand.items():
        pack = packs_map.get(ing_id)
        if not pack:
            continue

        is_weighted = payload.weighted_produce_enabled and pack.is_by_weight
        pack_weight = pack.pack_amount

        # Базовая цена для стандартной сети в выбранном городе
        price_rec = next(
            (pr for pr in pack.prices if pr.city_code == city_enum and pr.store_tier == StoreNetworkEnum.STANDARD),
            None,
        )
        base_price = float(price_rec.price_rub) if price_rec else 100.0

        if is_weighted:
            total_bought = math.ceil(required_qty / 50.0) * 50.0
            leftover = max(0.0, total_bought - round(required_qty))
            pack_count = 1
            base_price_total = (base_price * total_bought) / 1000.0
        else:
            pack_count = math.ceil(required_qty / pack_weight)
            total_bought = pack_count * pack_weight
            leftover = total_bought - required_qty
            base_price_total = base_price * pack_count

        packed_items.append(
            BasketItemDTO(
                id=ing_id,
                name=pack.pack_title,
                category=pack.ingredient.category,
                unit=pack.unit,
                pack_weight=pack_weight,
                required_amount=round(required_qty, 1),
                pack_count=pack_count,
                total_bought=round(total_bought, 1),
                leftover=round(leftover, 1),
                is_weighted=is_weighted,
                base_price_total=round(base_price_total, 2),
            )
        )

    # Итоговый расчет для 3 сетей супермаркетов
    store_summaries: List[StoreSummaryDTO] = []
    store_multipliers = {
        StoreNetworkEnum.BUDGET: ("Магнит / Пятёрочка", "Эконом", 0.88),
        StoreNetworkEnum.STANDARD: ("Перекрёсток / Лента", "Баланс", 1.00),
        StoreNetworkEnum.PREMIUM: ("ВкусВилл", "Премиум", 1.28),
    }

    for store_tier, (name, badge, mult) in store_multipliers.items():
        total_sum = sum(item.base_price_total * mult for item in packed_items)
        store_summaries.append(
            StoreSummaryDTO(
                id=store_tier.value,
                name=name,
                badge=badge,
                total_rub=round(total_sum),
            )
        )

    basket = BasketResponse(
        packed_items=packed_items,
        store_totals=store_summaries,
        city=payload.city,
    )

    return MenuGenerateResponse(days=generated_days, basket=basket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)