"""Document access handlers."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.core.enums import ButtonStyle
from telegram_bot.keyboards.utils import create_inline_button
from telegram_bot.services.document_client import document_client

router = Router()


@router.message(Command("documents"))
@router.message(F.text == "📁 Documents")
@router.callback_query(F.data == "documents_menu")
async def documents_menu(update: Message | CallbackQuery, user: dict) -> None:
    """Show documents menu."""
    message = None
    if isinstance(update, CallbackQuery):
        await update.answer()
        message = update.message
    else:
        message = update

    if message is None:
        return

    if not user:
        await message.answer("You need to be registered to view documents.\nUse /start to register.")
        return

    builder = InlineKeyboardBuilder()
    builder.add(
        create_inline_button("📄 My Department Docs", callback_data="dept_docs", style=ButtonStyle.PRIMARY),
        create_inline_button("📋 Company Policies", callback_data="company_policies", style=ButtonStyle.PRIMARY),
        create_inline_button("📚 Training Materials", callback_data="training_materials", style=ButtonStyle.PRIMARY),
        create_inline_button("← Menu", callback_data="menu"),
    )
    builder.adjust(1)

    text = (
        "📁 *Documents & Resources*\n\n"
        "Access documents relevant to your role and department:\n\n"
        "• 📄 My Department Docs - Documents specific to your department\n"
        "• 📋 Company Policies - HR policies and procedures\n"
        "• 📚 Training Materials - Learning resources and guides\n"
    )

    if isinstance(update, CallbackQuery) and isinstance(message, Message):
        await message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    else:
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")


@router.callback_query(F.data == "dept_docs")
async def department_docs(callback: CallbackQuery, user: dict, auth_token: str) -> None:
    """Show department documents."""
    if callback.message is None or not isinstance(callback.message, Message):
        await callback.answer("Unable to show documents. Please try again.")
        return

    message = callback.message

    # Fetch from document service
    if not user or not auth_token:
        await callback.answer("Authentication required", show_alert=True)
        return

    department = user.get("department", "")
    if not department:
        await callback.answer("Department not found for user", show_alert=True)
        return

    docs = await document_client.get_department_documents(department, auth_token)

    text = "📄 *Department Documents*\n\n"
    if docs:
        for i, doc in enumerate(docs, 1):
            title = doc.get("title", "Untitled")
            text += f"{i}. {title}\n"
    else:
        text += "No documents found for your department.\n"

    builder = InlineKeyboardBuilder()
    builder.add(create_inline_button("← Back", callback_data="documents_menu"))

    await message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "company_policies")
async def company_policies(callback: CallbackQuery, user: dict, auth_token: str) -> None:
    """Show company policies."""
    if callback.message is None or not isinstance(callback.message, Message):
        await callback.answer("Unable to show policies. Please try again.")
        return

    message = callback.message

    if not user or not auth_token:
        await callback.answer("Authentication required", show_alert=True)
        return

    policies = await document_client.get_company_policies(auth_token)

    text = "📋 *Company Policies*\n\n"
    if policies:
        for i, policy in enumerate(policies, 1):
            title = policy.get("title", "Untitled")
            text += f"{i}. {title}\n"
    else:
        text += "No company policies found.\n"

    builder = InlineKeyboardBuilder()
    builder.add(create_inline_button("← Back", callback_data="documents_menu"))

    await message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "training_materials")
async def training_materials(callback: CallbackQuery, user: dict, auth_token: str) -> None:
    """Show training materials."""
    if callback.message is None or not isinstance(callback.message, Message):
        await callback.answer("Unable to show materials. Please try again.")
        return

    message = callback.message

    if not user or not auth_token:
        await callback.answer("Authentication required", show_alert=True)
        return

    materials = await document_client.get_training_materials(auth_token)

    text = "📚 *Training Materials*\n\n"
    if materials:
        for i, material in enumerate(materials, 1):
            title = material.get("title", "Untitled")
            text += f"{i}. {title}\n"
    else:
        text += "No training materials found.\n"

    builder = InlineKeyboardBuilder()
    builder.add(create_inline_button("← Back", callback_data="documents_menu"))

    await message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()
