"""Feedback and pulse survey handlers."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from telegram_bot.i18n import t
from telegram_bot.keyboards.feedback_kb import (
    get_experience_rating_keyboard,
    get_feedback_menu_keyboard,
)
from telegram_bot.services.feedback_client import feedback_client
from telegram_bot.states.feedback_states import FeedbackStates
from telegram_bot.utils.formatters import format_feedback_menu

router = Router()

MIN_PULSE_RATING = 1
MAX_PULSE_RATING = 10
MIN_COMMENT_LENGTH = 10


@router.message(Command("feedback"))
@router.message(F.text == "\U0001f4ca Feedback")
@router.callback_query(F.data == "feedback_menu")
async def feedback_menu(
    update: Message | CallbackQuery, state: FSMContext, *, locale: str = "en"
) -> None:
    """Show feedback menu."""
    if isinstance(update, CallbackQuery):
        msg = update.message
        await update.answer()
    else:
        msg = update

    text = format_feedback_menu(locale=locale)

    if isinstance(update, CallbackQuery):
        await msg.edit_text(
            text,
            reply_markup=get_feedback_menu_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )
    else:
        await msg.answer(
            text,
            reply_markup=get_feedback_menu_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )


@router.callback_query(F.data == "pulse_survey")
async def start_pulse_survey(
    callback: CallbackQuery, state: FSMContext, *, locale: str = "en"
) -> None:
    """Start daily pulse survey."""
    if callback.message:
        await callback.message.edit_text(
            f"*\U0001f4ca {t('feedback.pulse_title', locale=locale)}*\n\n{t('feedback.pulse_prompt', locale=locale)}",
            parse_mode="Markdown",
        )
    await state.set_state(FeedbackStates.waiting_for_pulse_rating)
    await callback.answer()


@router.message(FeedbackStates.waiting_for_pulse_rating)
async def process_pulse_rating(
    message: Message,
    state: FSMContext,
    user: dict,
    auth_token: str,
    *,
    locale: str = "en",
) -> None:
    """Process pulse survey rating."""
    try:
        rating = int((message.text or "").strip())
        if MIN_PULSE_RATING <= rating <= MAX_PULSE_RATING:
            if user and auth_token:
                success = await feedback_client.submit_pulse_survey(
                    user["id"], rating, auth_token
                )
                if not success:
                    await message.answer(t("feedback.submit_failed", locale=locale))
                    return

            await message.answer(
                t("feedback.pulse_thanks", locale=locale, rating=rating)
            )
            await state.clear()
        else:
            await message.answer(
                t(
                    "feedback.pulse_invalid",
                    locale=locale,
                    min=MIN_PULSE_RATING,
                    max=MAX_PULSE_RATING,
                )
            )
    except ValueError:
        await message.answer(
            t(
                "feedback.pulse_invalid",
                locale=locale,
                min=MIN_PULSE_RATING,
                max=MAX_PULSE_RATING,
            )
        )


@router.callback_query(F.data == "rate_experience")
async def start_experience_rating(
    callback: CallbackQuery, state: FSMContext, *, locale: str = "en"
) -> None:
    """Start experience rating."""
    if callback.message:
        title = f"*\u2b50 {t('feedback.experience_title', locale=locale)}*"
        prompt = t("feedback.experience_prompt", locale=locale)
        await callback.message.edit_text(
            f"{title}\n\n{prompt}",
            reply_markup=get_experience_rating_keyboard(locale=locale).as_markup(),
            parse_mode="Markdown",
        )
    await callback.answer()


@router.callback_query(F.data.startswith("rate_"))
async def process_experience_rating(
    callback: CallbackQuery, user: dict, auth_token: str, *, locale: str = "en"
) -> None:
    """Process experience rating."""
    rating = int(callback.data.split("_")[1])

    if user and auth_token:
        success = await feedback_client.submit_experience_rating(
            user["id"], rating, auth_token
        )
        if not success:
            await callback.answer(
                t("feedback.submit_failed", locale=locale), show_alert=True
            )
            return

    if callback.message:
        await callback.message.edit_text(
            t("feedback.experience_thanks", locale=locale, rating=rating)
        )
    await callback.answer()


@router.callback_query(F.data == "comments_suggestions")
async def start_comments(
    callback: CallbackQuery, state: FSMContext, *, locale: str = "en"
) -> None:
    """Start comments and suggestions."""
    if callback.message:
        title = f"*\U0001f4ac {t('feedback.comments_title', locale=locale)}*"
        prompt = t("feedback.comments_prompt", locale=locale)
        await callback.message.edit_text(
            f"{title}\n\n{prompt}",
            parse_mode="Markdown",
        )
    await state.set_state(FeedbackStates.waiting_for_comments)
    await callback.answer()


@router.message(FeedbackStates.waiting_for_comments)
async def process_comments(
    message: Message,
    state: FSMContext,
    user: dict,
    auth_token: str,
    *,
    locale: str = "en",
) -> None:
    """Process comments and suggestions."""
    comment = (message.text or "").strip()

    if len(comment) < MIN_COMMENT_LENGTH:
        await message.answer(
            t("feedback.comments_too_short", locale=locale, min=MIN_COMMENT_LENGTH)
        )
        return

    if user and auth_token:
        success = await feedback_client.submit_comment(user["id"], comment, auth_token)
        if not success:
            await message.answer(t("feedback.submit_failed", locale=locale))
            return

    await message.answer(t("feedback.comments_thanks", locale=locale))
    await state.clear()
