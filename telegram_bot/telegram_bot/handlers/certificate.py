"""Certificate management handlers."""

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

logger = logging.getLogger(__name__)

from telegram_bot.i18n import t
from telegram_bot.services.certificates_client import certificates_client

router = Router()


@router.message(Command("certificate"))
async def show_certificates(
    message: Message,
    auth_token: str,
    user: dict,
    *,
    locale: str = "en",
) -> None:
    """Show user's certificates."""
    if not auth_token or not user:
        await message.answer(t("auth.required", locale=locale))
        return

    certificates = await certificates_client.get_my_certificates(auth_token)

    if not certificates:
        await message.answer(t("certificate.none", locale=locale))
        return

    text = f"*\U0001f4c6 {t('certificate.title', locale=locale)}*\n\n"

    keyboard = InlineKeyboardBuilder()
    for cert in certificates:
        text += f"\U0001f3c7 Certificate ID: `{cert['cert_uid']}`\n"
        text += f"   Issued: {cert['issued_at'] or 'N/A'}\n\n"
        keyboard.button(
            text=f"\U0001f4e5 Download {cert['cert_uid'][:8]}...", callback_data=f"download_cert:{cert['cert_uid']}"
        )

    await message.answer(text, reply_markup=keyboard.as_markup(), parse_mode="Markdown")


@router.callback_query(F.data.startswith("download_cert:"))
async def download_certificate(
    callback: CallbackQuery,
    auth_token: str,
    user: dict,
    *,
    locale: str = "en",
) -> None:
    """Download certificate PDF."""
    if not auth_token or not user:
        await callback.answer(t("auth.required", locale=locale))
        return

    cert_uid = callback.data.split(":", 1)[1]

    try:
        pdf_bytes = await certificates_client.download_certificate(cert_uid, locale, auth_token)

        pdf_file = BufferedInputFile(pdf_bytes, filename=f"certificate_{cert_uid}.pdf")

        await callback.message.answer_document(pdf_file, caption=t("certificate.downloaded", locale=locale))
        await callback.answer()
    except Exception:
        logger.exception("Failed to download certificate")
        await callback.answer(t("certificate.download_error", locale=locale))
