from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    """Базовый декларативный класс для всех моделей базы данных."""
    pass


class MealTypeEnum(str, enum.Enum):
    """Основные приемы пищи."""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class CourseTypeEnum(str, enum.Enum):
    """Тип блюда (для разделения супов и вторых блюд на обед)."""
    SOUP = "soup"
    MAIN = "main"
    BREAKFAST = "breakfast"
    SNACK = "snack"


class ChainRoleEnum(str, enum.Enum):
    """Роль блюда в Zero-Waste цепочке утилизации фабричных упаковок."""
    INITIATOR = "initiator"      # Вскрывает новую упаковку (готовится первым)
    CONSUMER = "consumer"        # Утилизирует остаток вскрытой упаковки (строго со 2-го дня)
    INDEPENDENT = "independent"  # Автономное блюдо (не привязано к жестким остаткам)


class StoreNetworkEnum(str, enum.Enum):
    """Торговые сети для расчета 3 корзин."""
    BUDGET = "budget"            # Магнит / Пятёрочка
    STANDARD = "standard"        # Перекрёсток / Лента
    PREMIUM = "premium"          # ВкусВилл


class CityCodeEnum(str, enum.Enum):
    """Города пилотного запуска."""
    SPB = "SPB"                  # Санкт-Петербург
    MSK = "MSK"                  # Москва
    NN = "NN"                    # Нижний Новгород


class User(Base):
    """
    Пользователь Telegram Mini App.
    Хранит базовые настройки семьи, город и профиль ограничений.
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False, index=True
    )
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    city: Mapped[CityCodeEnum] = mapped_column(
        Enum(CityCodeEnum), default=CityCodeEnum.SPB, nullable=False
    )
    default_people_count: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    batch_cooking_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    weighted_produce_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Список исключений пользователя в формате JSON (например: ["без лактозы", "без лука"])
    custom_exclusions: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Связи
    pantry_items: Mapped[List["UserPantryItem"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    saved_menus: Mapped[List["SavedMenuPlan"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Ingredient(Base):
    """
    Справочник продуктов и ингредиентов.
    Содержит флаги аллергенов, категорию хранения и сроки годности открытой пачки.
    """
    __tablename__ = "ingredients"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # e.g. "ing_chicken_breast"
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    
    # Флаги ограничений для мгновенной фильтрации блюд
    is_lactose: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    has_gluten: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    is_pork: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    is_beef: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    is_poultry: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    is_fish: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    is_onion: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    is_garlic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    is_mushrooms: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    # Параметры хранения
    is_perishable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    shelf_life_opened_days: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    default_unit: Mapped[str] = mapped_column(String(16), default="г", nullable=False)

    # Связи
    product_packs: Mapped[List["ProductPack"]] = relationship(
        back_populates="ingredient", cascade="all, delete-orphan"
    )
    recipes_link: Mapped[List["RecipeIngredient"]] = relationship(
        back_populates="ingredient"
    )


class ProductPack(Base):
    """
    Фабричная упаковка конкретного товара в торговых сетях (лоток, бутылка, пачка, развес).
    """
    __tablename__ = "product_packs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    ingredient_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    pack_title: Mapped[str] = mapped_column(String(255), nullable=False)
    pack_amount: Mapped[float] = mapped_column(Float, nullable=False)  # 800 (г), 10 (шт)
    unit: Mapped[str] = mapped_column(String(16), nullable=False)      # "г", "шт", "мл"
    is_by_weight: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Связи
    ingredient: Mapped["Ingredient"] = relationship(back_populates="product_packs")
    prices: Mapped[List["StorePrice"]] = relationship(
        back_populates="pack", cascade="all, delete-orphan"
    )


class StorePrice(Base):
    """
    Цены торговых сетей на упаковку с привязкой к городу.
    Обновляются фоновым парсером 1 раз в сутки.
    """
    __tablename__ = "store_prices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    pack_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("product_packs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    store_tier: Mapped[StoreNetworkEnum] = mapped_column(
        Enum(StoreNetworkEnum), nullable=False, index=True
    )
    city_code: Mapped[CityCodeEnum] = mapped_column(
        Enum(CityCodeEnum), nullable=False, index=True
    )
    price_rub: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    in_stock: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    pack: Mapped["ProductPack"] = relationship(back_populates="prices")

    __table_args__ = (
        Index("ix_store_prices_pack_store_city", "pack_id", "store_tier", "city_code", unique=True),
    )


class Recipe(Base):
    """
    Каталог обучающих рецептов домашней кухни.
    Включает макронутриенты, сложность, пошаговые ориентиры и цепочки утилизации.
    """
    __tablename__ = "recipes"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # e.g. "rec_shchi_fresh_cabbage"
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    image_url: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(32), default="Легко", nullable=False)
    
    meal_type: Mapped[MealTypeEnum] = mapped_column(Enum(MealTypeEnum), nullable=False, index=True)
    course_type: Mapped[CourseTypeEnum] = mapped_column(Enum(CourseTypeEnum), nullable=False, index=True)
    
    prep_time_min: Mapped[int] = mapped_column(Integer, nullable=False)
    calories: Mapped[int] = mapped_column(Integer, nullable=False)
    proteins: Mapped[int] = mapped_column(Integer, nullable=False)
    fats: Mapped[int] = mapped_column(Integer, nullable=False)
    carbs: Mapped[int] = mapped_column(Integer, nullable=False)
    
    tags: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    equipment: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    
    # Zero-Waste параметры
    is_batchable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    batch_label: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    chain_role: Mapped[ChainRoleEnum] = mapped_column(
        Enum(ChainRoleEnum), default=ChainRoleEnum.INDEPENDENT, nullable=False, index=True
    )
    linked_ingredient_id: Mapped[Optional[str]] = mapped_column(
        String(64), ForeignKey("ingredients.id", ondelete="SET NULL"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Связи
    ingredients: Mapped[List["RecipeIngredient"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan"
    )
    steps: Mapped[List["RecipeStep"]] = relationship(
        back_populates="recipe", order_by="RecipeStep.step_number", cascade="all, delete-orphan"
    )


class RecipeIngredient(Base):
    """
    Таблица связи рецепта и необходимого количества ингредиента на 1 персону.
    """
    __tablename__ = "recipe_ingredients"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    recipe_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ingredient_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Количество на 1 взрослую персону
    amount_per_person: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(16), default="г", nullable=False)
    is_pantry: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_shared_side: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    recipe: Mapped["Recipe"] = relationship(back_populates="ingredients")
    ingredient: Mapped["Ingredient"] = relationship(back_populates="recipes_link")


class RecipeStep(Base):
    """
    Пошаговая обучающая инструкция для приготовления (Cookbook Standard).
    """
    __tablename__ = "recipe_steps"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    recipe_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    instruction: Mapped[Text] = mapped_column(Text, nullable=False)
    duration_sec: Mapped[int] = mapped_column(Integer, default=180, nullable=False)
    heat_level: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    visual_marker: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    chef_tip: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    recipe: Mapped["Recipe"] = relationship(back_populates="steps")

    __table_args__ = (
        Index("ix_recipe_steps_recipe_order", "recipe_id", "step_number", unique=True),
    )


class UserPantryItem(Base):
    """
    Состояние домашнего склада (Pantry) конкретного пользователя.
    """
    __tablename__ = "user_pantry_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    pantry_code: Mapped[str] = mapped_column(String(64), nullable=False)
    item_name: Mapped[str] = mapped_column(String(128), nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped["User"] = relationship(back_populates="pantry_items")

    __table_args__ = (
        Index("ix_user_pantry_unique", "user_id", "pantry_code", unique=True),
    )


class SavedMenuPlan(Base):
    """
    Сгенерированный план питания и корзина покупок пользователя.
    """
    __tablename__ = "saved_menu_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    days_count: Mapped[int] = mapped_column(Integer, nullable=False)
    people_count: Mapped[int] = mapped_column(Integer, nullable=False)
    city_code: Mapped[CityCodeEnum] = mapped_column(Enum(CityCodeEnum), nullable=False)
    
    # Полная структура сгенерированных дней с блюдами (JSONB)
    menu_days_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    # Рассчитанная корзина покупок со всеми упаковками и ценами 3 сетей
    basket_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="saved_menus")