"""Feedback and pulse survey handlers."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from telegram_bot.i18n import t
from telegram_bot.keyboards.feedback_kb import (
    get_anonymity_choice_keyboard,
    get_experience_rating_keyboard,
    get_feedback_menu_keyboard,
    get_pulse_rating_keyboard,
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
@router.message(F.text == "Feedback")
@router.message(F.text == "\U0001f4ca \u041e\u0431\u0440\u0430\u0442\u043d\u0430\u044f \u0441\u0432\u044f\u0437\u044c")
@router.message(F.text == "\u041e\u0431\u0440\u0430\u0442\u043d\u0430\u044f \u0441\u0432\u044f\u0437\u044c")
@router.callback_query(F.data == "feedback_menu")
async def feedback_menu(update: Message | CallbackQuery, state: FSMContext, *, locale: str = "en") -> None:
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
            reply_markup=get_feedback_menu_keyboard(locale=locale),
            parse_mode="Markdown",
        )
    else:
        await msg.answer(
            text,
            reply_markup=get_feedback_menu_keyboard(locale=locale),
            parse_mode="Markdown",
        )


@router.callback_query(F.data == "pulse_survey")
async def start_pulse_survey(callback: CallbackQuery, state: FSMContext, *, locale: str = "en") -> None:
    """Start daily pulse survey - first ask for anonymity choice."""
    if callback.message:
        await callback.message.edit_text(
            f"*\U0001f4ca {t('feedback.pulse_title', locale=locale)}*\n\n{t('feedback.anonymity_prompt', locale=locale)}",
            reply_markup=get_anonymity_choice_keyboard(locale=locale, survey_type="pulse"),
            parse_mode="Markdown",
        )
    await state.set_state(FeedbackStates.waiting_for_anonymity_choice)
    await callback.answer()


@router.callback_query(F.data.startswith("pulse_anon_choice_"))
async def process_pulse_anonymity_choice(
    callback: CallbackQuery,
    state: FSMContext,
    *,
    locale: str = "en",
) -> None:
    """Process anonymity choice for pulse survey."""
    # Parse is_anonymous from callback data: pulse_anon_choice_{true/false}
    try:
        is_anonymous = callback.data.split("_")[-1] == "true"
    except (IndexError, ValueError):
        await callback.answer(t("feedback.invalid_choice", locale=locale), show_alert=True)
        return

    # Store anonymity choice in state
    await state.update_data(is_anonymous=is_anonymous)

    # Show rating keyboard
    anon_text = t("feedback.anonymous_suffix", locale=locale) if is_anonymous else ""
    if callback.message:
        await callback.message.edit_text(
            f"*\U0001f4ca {t('feedback.pulse_title', locale=locale)}*{anon_text}\n\n{t('feedback.pulse_prompt', locale=locale)}",
            reply_markup=get_pulse_rating_keyboard(locale=locale, is_anonymous=is_anonymous),
            parse_mode="Markdown",
        )
    await state.set_state(FeedbackStates.waiting_for_pulse_rating)
    await callback.answer()


@router.callback_query(F.data.startswith("pulse_"))
async def process_pulse_rating(
    callback: CallbackQuery,
    state: FSMContext,
    user: dict,
    auth_token: str,
    *,
    locale: str = "en",
) -> None:
    """Process pulse survey rating from button click."""
    from loguru import logger
    logger.info("Processing pulse rating - user: {}, auth_token: {}", user, auth_token[:20] if auth_token else None)
    # Parse rating from callback data: pulse_{rating}_anon_{is_anonymous}
    try:
        parts = callback.data.split("_")
        rating = int(parts[1])
        is_anonymous = parts[-1] == "true" if len(parts) >= 4 else False
    except (IndexError, ValueError):
        await callback.answer(t("feedback.pulse_invalid", locale=locale), show_alert=True)
        return

    if not (MIN_PULSE_RATING <= rating <= MAX_PULSE_RATING):
        await callback.answer(t("feedback.pulse_invalid", locale=locale), show_alert=True)
        return

    if user and auth_token:
        success = await feedback_client.submit_pulse_survey(
            rating=rating,
            is_anonymous=is_anonymous,
            auth_token=auth_token,
        )
        if not success:
            await callback.answer(t("feedback.submit_failed", locale=locale), show_alert=True)
            return

    # Show appropriate thank you message
    thanks_key = "feedback.pulse_thanks_anon" if is_anonymous else "feedback.pulse_thanks"
    if callback.message:
        await callback.message.edit_text(
            t(thanks_key, locale=locale, rating=rating),
            reply_markup=get_feedback_menu_keyboard(locale=locale),
        )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "rate_experience")
async def start_experience_rating(callback: CallbackQuery, state: FSMContext, *, locale: str = "en") -> None:
    """Start experience rating - first ask for anonymity choice."""
    if callback.message:
        await callback.message.edit_text(
            f"*\u2b50 {t('feedback.experience_title', locale=locale)}*\n\n{t('feedback.anonymity_prompt', locale=locale)}",
            reply_markup=get_anonymity_choice_keyboard(locale=locale, survey_type="experience"),
            parse_mode="Markdown",
        )
    await state.set_state(FeedbackStates.waiting_for_anonymity_choice)
    await callback.answer()


@router.callback_query(F.data.startswith("experience_anon_choice_"))
async def process_experience_anonymity_choice(
    callback: CallbackQuery,
    state: FSMContext,
    *,
    locale: str = "en",
) -> None:
    """Process anonymity choice for experience rating."""
    # Parse is_anonymous from callback data: experience_anon_choice_{true/false}
    try:
        is_anonymous = callback.data.split("_")[-1] == "true"
    except (IndexError, ValueError):
        await callback.answer(t("feedback.invalid_choice", locale=locale), show_alert=True)
        return

    # Store anonymity choice in state
    await state.update_data(is_anonymous=is_anonymous)

    # Show rating keyboard
    anon_text = t("feedback.anonymous_suffix", locale=locale) if is_anonymous else ""
    if callback.message:
        title = f"*\u2b50 {t('feedback.experience_title', locale=locale)}*{anon_text}"
        prompt = t("feedback.experience_prompt", locale=locale)
        await callback.message.edit_text(
            f"{title}\n\n{prompt}",
            reply_markup=get_experience_rating_keyboard(locale=locale, is_anonymous=is_anonymous),
            parse_mode="Markdown",
        )
    await state.set_state(FeedbackStates.waiting_for_experience_rating)
    await callback.answer()


@router.callback_query(F.data.startswith("rate_"))
async def process_experience_rating(
    callback: CallbackQuery, state: FSMContext, user: dict, auth_token: str, *, locale: str = "en"
) -> None:
    """Process experience rating."""
    # Parse rating from callback data: rate_{rating}_anon_{is_anonymous}
    try:
        parts = callback.data.split("_")
        rating = int(parts[1])
        is_anonymous = parts[-1] == "true" if len(parts) >= 4 else False
    except (IndexError, ValueError):
        await callback.answer(t("feedback.invalid_choice", locale=locale), show_alert=True)
        return

    if user and auth_token:
        success = await feedback_client.submit_experience_rating(
            rating=rating,
            is_anonymous=is_anonymous,
            auth_token=auth_token,
        )
        if not success:
            await callback.answer(t("feedback.submit_failed", locale=locale), show_alert=True)
            return

    # Show appropriate thank you message
    thanks_key = "feedback.experience_thanks_anon" if is_anonymous else "feedback.experience_thanks"
    if callback.message:
        await callback.message.edit_text(
            t(thanks_key, locale=locale, rating=rating),
            reply_markup=get_feedback_menu_keyboard(locale=locale),
        )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "comments_suggestions")
async def start_comments(callback: CallbackQuery, state: FSMContext, *, locale: str = "en") -> None:
    """Start comments and suggestions - first ask for anonymity choice."""
    if callback.message:
        await callback.message.edit_text(
            f"*\U0001f4ac {t('feedback.comments_title', locale=locale)}*\n\n{t('feedback.anonymity_prompt', locale=locale)}",
            reply_markup=get_anonymity_choice_keyboard(locale=locale, survey_type="comment"),
            parse_mode="Markdown",
        )
    await state.set_state(FeedbackStates.waiting_for_comment_anonymity)
    await callback.answer()


@router.callback_query(F.data.startswith("comment_anon_choice_"))
async def process_comment_anonymity_choice(
    callback: CallbackQuery,
    state: FSMContext,
    *,
    locale: str = "en",
) -> None:
    """Process anonymity choice for comments."""
    # Parse is_anonymous from callback data: comment_anon_choice_{true/false}
    try:
        is_anonymous = callback.data.split("_")[-1] == "true"
    except (IndexError, ValueError):
        await callback.answer(t("feedback.invalid_choice", locale=locale), show_alert=True)
        return

    # Store anonymity choice in state
    await state.update_data(is_anonymous=is_anonymous)

    # Show comment prompt
    anon_text = t("feedback.anonymous_suffix", locale=locale) if is_anonymous else ""
    if callback.message:
        await callback.message.edit_text(
            f"*\U0001f4ac {t('feedback.comments_title', locale=locale)}*{anon_text}\n\n{t('feedback.comments_prompt', locale=locale)}",
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
        await message.answer(t("feedback.comments_too_short", locale=locale, min=MIN_COMMENT_LENGTH))
        return

    # Get anonymity choice from state
    data = await state.get_data()
    is_anonymous = data.get("is_anonymous", False)

    if user and auth_token:
        success = await feedback_client.submit_comment(
            comment=comment,
            is_anonymous=is_anonymous,
            auth_token=auth_token,
        )
        if not success:
            await message.answer(t("feedback.submit_failed", locale=locale))
            return

    # Show appropriate thank you message
    thanks_key = "feedback.comments_thanks_anon" if is_anonymous else "feedback.comments_thanks"
    await message.answer(
        t(thanks_key, locale=locale),
        reply_markup=get_feedback_menu_keyboard(locale=locale),
    )
    await state.clear()
