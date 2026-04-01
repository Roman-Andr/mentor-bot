"""FAQ (rule-based dialogues) handlers."""

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from telegram_bot.keyboards.dialogue_kb import (
    get_dialogue_step_keyboard,
    get_faq_menu_keyboard,
)
from telegram_bot.keyboards.main_menu import get_inline_main_menu
from telegram_bot.services.knowledge_client import knowledge_client

logger = logging.getLogger(__name__)

router = Router()

FAQ_STORAGE_KEY = "faq_scenarios"
STEP_STORAGE_KEY = "faq_steps"


async def load_scenarios(locale: str = "en") -> list[dict]:
    """Load FAQ scenarios from knowledge service."""
    try:
        response = await knowledge_client.get_active_scenarios()
        if response.get("scenarios"):
            return response["scenarios"]
    except Exception as e:
        logger.error(f"Failed to load FAQ scenarios: {e}")
    return []


async def load_scenario_steps(scenario_id: int) -> list[dict]:
    """Load steps for a scenario from knowledge service."""
    try:
        response = await knowledge_client.get_scenario(scenario_id)
        if response.get("steps"):
            return response["steps"]
    except Exception as e:
        logger.error(f"Failed to load scenario steps: {e}")
    return []


def build_step_map(steps: list[dict]) -> dict[int, dict]:
    """Build a map of step_id -> step data."""
    return {step["id"]: step for step in steps}


@router.message(Command("faq"))
@router.message(F.text == "\U0001f4ac FAQ")
@router.message(F.text == "FAQ")
@router.callback_query(F.data == "faq_menu")
async def faq_menu(update: Message | CallbackQuery, *, locale: str = "ru") -> None:
    """Show FAQ menu with scenarios."""
    if isinstance(update, CallbackQuery):
        msg = update.message
        if msg is None:
            return
        await update.answer()
    else:
        msg = update

    scenarios = await load_scenarios(locale)

    if not scenarios:
        text = (
            "\U0001f4ac *Часто задаваемые вопросы*\n\n"
            "В данный момент список FAQ пуст. Обратитесь к HR для настройки."
        )
        if isinstance(update, CallbackQuery):
            await msg.edit_text(text, parse_mode="Markdown")
        else:
            await msg.answer(text, parse_mode="Markdown")
        return

    text = "\U0001f4ac *Часто задаваемые вопросы*\n\nВыберите тему:"

    keyboard = get_faq_menu_keyboard(scenarios)

    if isinstance(update, CallbackQuery):
        await msg.edit_text(
            text, reply_markup=keyboard.as_markup(), parse_mode="Markdown"
        )
    else:
        await msg.answer(text, reply_markup=keyboard.as_markup(), parse_mode="Markdown")


@router.callback_query(F.data.startswith("faq_scenario_"))
async def start_dialogue(
    callback: CallbackQuery, state: FSMContext, *, locale: str = "ru"
) -> None:
    """Start a dialogue scenario."""
    if callback.message is None:
        return

    scenario_id = int(callback.data.replace("faq_scenario_", ""))
    steps = await load_scenario_steps(scenario_id)

    if not steps:
        await callback.answer("Сценарий не найден", show_alert=True)
        return

    step_map = build_step_map(steps)
    first_step = next((s for s in steps if s.get("step_number") == 1), None)

    if not first_step:
        await callback.answer("Шаги не найдены", show_alert=True)
        return

    await state.update_data(
        current_scenario_id=scenario_id,
        current_step_id=first_step["id"],
        steps_map=step_map,
    )

    keyboard = get_dialogue_step_keyboard(first_step)
    await callback.message.edit_text(
        first_step.get("question", "Вопрос"),
        reply_markup=keyboard.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("faq_next_"))
async def next_dialogue_step(
    callback: CallbackQuery, state: FSMContext, *, locale: str = "ru"
) -> None:
    """Move to next dialogue step."""
    if callback.message is None:
        return

    data = await state.get_data()
    step_map: dict[int, dict] = data.get("steps_map", {})

    next_step_id = int(callback.data.replace("faq_next_", ""))

    if next_step_id == 0:
        await faq_menu(callback, locale=locale)
        return

    next_step = step_map.get(next_step_id)
    if not next_step:
        await callback.answer("Шаг не найден", show_alert=True)
        return

    await state.update_data(current_step_id=next_step_id)

    keyboard = get_dialogue_step_keyboard(next_step)
    await callback.message.edit_text(
        next_step.get("question", "Вопрос"),
        reply_markup=keyboard.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_menu")
async def back_to_main_menu(callback: CallbackQuery, *, locale: str = "ru") -> None:
    """Return to main menu."""
    if callback.message is None:
        return

    text = "\U0001f4cb *Главное меню*\n\nВыберите раздел:"
    keyboard = get_inline_main_menu()

    await callback.message.edit_text(
        text, reply_markup=keyboard.as_markup(), parse_mode="Markdown"
    )
    await callback.answer()
