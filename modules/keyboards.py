# -*- coding: utf-8 -*-

# Developer: Nethanter-del
# Github: https://github.com/Nethanter-del
# Date Created: 2025-12-03
# Version: 1.0.0

# License: MIT License
#
# Copyright (c) 2025 Nethanter-del

from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
class keyboard:
    async def main_keyboard():
        builder = InlineKeyboardBuilder()
        button_create_ticket = InlineKeyboardButton(text = "❓Задать вопрос❓", callback_data = "create_ticket")
        button_open_profile = InlineKeyboardButton(text = "🧑‍💻Мой профиль🧑‍💻", callback_data = "open_profile")
        builder.add(button_create_ticket, button_open_profile)
        return builder.as_markup()
    async def create_ticket():
        builder = InlineKeyboardBuilder()
        button_create_ticket = InlineKeyboardButton(text = "✅Отправить", callback_data = "send")
        button_open_profile = InlineKeyboardButton(text = "❌Отмена", callback_data = "cancel")
        builder.add(button_create_ticket, button_open_profile)
        return builder.as_markup()
    async def process_ticket(id):
        builder = InlineKeyboardBuilder()
        button_claim_ticket = InlineKeyboardButton(text = "✅Ответить", callback_data = f"answer_{id}")
        button_decline_ticket = InlineKeyboardButton(text = "❌Отклонить", callback_data = f"decline_{id}")
        builder.add(button_claim_ticket, button_decline_ticket)
        return builder.as_markup()
    async def finish_ticket():
        builder = InlineKeyboardBuilder()
        button_start = InlineKeyboardButton(text = "✅Вернуться в меню", callback_data = f"back")
        builder.add(button_start)
        return builder.as_markup()