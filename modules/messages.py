# -*- coding: utf-8 -*-

# Developer: Nethanter-del
# Github: https://github.com/Nethanter-del
# Date Created: 2025-12-03
# Version: 1.0.0

# License: MIT License
#
# Copyright (c) 2025 Nethanter-del

class messages:
    def welcome_message(username):
        text = (
f"""👋 Приветствую!

В данном боте вы можете задать свой вопрос в виде заявки.

Чтобы задать свой вопрос нажмите кнопку ниже."""
)
        return text
    def profile_message(user,role):
        text = (
f"""🧑‍💻 Ваш профиль:

💈 Имя: {user[0]["username"]}
🛡 Роль: {role}
💾 Айди: {user[0]["user_id"]}"""
)
        return text
    def submit_ticket_message(text1):
        text = (
f"""✉️ Ваш вопрос:

<b>{text1}</b>"""
)
        return text
    def notify_ticket_message(id, from_id, status, message):
        text = (
f"""💬 Новый вопрос № {id}

🧑‍💻 От: {from_id}
💾 Статус: {status}

📝 Вопрос: <b>{message}</b>"""
)
        return text