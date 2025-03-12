# -*- coding: utf-8 -*-

# Developer: Nethanter-del
# Github: https://github.com/Nethanter-del
# Date Created: 2025-12-03
# Version: 1.0.0

# License: MIT License
#
# Copyright (c) 2025 Nethanter-del

from aiogram import types
from aiogram.filters.command import Command
from aiogram import F
from aiogram.enums import ParseMode
from .messages import messages
from .keyboards import keyboard

class client_handlers:
    def __init__(self, bot, dp, db_instance):
        self.bot = bot
        self.dp = dp
        self.db_instance = db_instance
        
    async def main(self):
        # start message 
        @self.dp.message(Command("start"))
        async def start(message: types.Message):
            user = await self.db_instance.get_user(message.from_user.id)
            if len(user) == 0:
                await self.db_instance.create_user(message.from_user.id, message.from_user.username)
            await message.answer(
                text = messages.welcome_message(user[0]["username"]), 
                reply_markup = await keyboard.main_keyboard())
        # state manager get|set state
        async def state_manager(id, action='get'):
            states = ["polling", "waiting", "free"]
            if action == 'get':
                state = await self.db_instance.get_state(id)
                return state
            elif action in states:
                await self.db_instance.set_state(id, action)
        # create ticket
        async def create_ticket(callback_query):
            user = await self.db_instance.get_user(callback_query.from_user.id)
            if str(user[0]["is_admin"]) == "True":
                await callback_query.message.answer(text="❌ Вы не можетe создавать вопросы!")
            else:
                state = await state_manager(callback_query.from_user.id, 'get')
                await self.bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
                if state[0]["state"] != "waiting":
                    await callback_query.message.answer(text="✍️ Введите ваш вопрос:")
                    print(callback_query.message.message_id)
                    await state_manager(callback_query.from_user.id, 'polling')
                else:
                    await callback_query.message.answer(text="Вы не можете создавать более одного вопроса за раз!")
        # show profile      
        async def open_profile(callback_query):
            user = await self.db_instance.get_user(callback_query.from_user.id)
            role = "Пользователь"
            if str(user[0]["is_admin"]) == "True":
                role = "Администратор"
            await callback_query.message.answer(text=messages.profile_message(user,role), reply_markup=await keyboard.finish_ticket())
        # send ticket
        async def send_ticket(callback_query):
            await self.bot.edit_message_reply_markup(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, reply_markup=None)
            await self.db_instance.register_ticket(callback_query.from_user.id)
            await state_manager(callback_query.from_user.id, 'waiting')
            await callback_query.message.answer(text="🕐 Ваш вопрос зарегестрирован.")
            print(callback_query.message.message_id)
            admins = await self.db_instance.select_admins()
            ticketraw = await self.db_instance.get_ticket(callback_query.from_user.id)
            ticket = ticketraw[0]
            for admin in admins:
                await self.bot.send_message(
                    chat_id=int(admin["user_id"]), 
                    text=messages.notify_ticket_message(
                        ticket["ticket_id"], 
                        ticket["user_id"], 
                        ticket["status"], 
                        ticket["ticket"]), 
                    parse_mode = ParseMode.HTML, 
                    reply_markup = await keyboard.process_ticket(ticket["ticket_id"])
                    )
        # answer ticket - admin
        async def answer_ticket(callback_query):
            ticket_id = callback_query.data.split("_")
            ticketraw = await self.db_instance.get_ticket(ticket_id=ticket_id[1])
            ticket = ticketraw[0]
            await self.db_instance.process_ticket(ticket_id[1], callback_query.from_user.id, "opened", "claimed")
            await self.bot.send_message(
                        chat_id = int(ticket["user_id"]),
                        text = f"✅ Ваш вопрос принят.")
            await state_manager(callback_query.from_user.id, 'polling')
            await callback_query.message.answer(
                        text = ("Вопрос принят, напишите свой ответ:"))
        # delete ticket - client|admin    
        async def cancel_ticket(callback_query, query_from='user'):
            if query_from == 'user':
                user_id = callback_query.from_user.id
                await self.bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
                await self.db_instance.del_ticket(user_id)
            elif query_from == 'admin':
                ticket_id = callback_query.data.split("_")
                ticketraw = await self.db_instance.get_ticket(ticket_id=ticket_id[1])
                ticket = ticketraw[0]
                user_id = ticket["user_id"]
                await self.db_instance.del_ticket(user_id=0, ticket_id=ticket["ticket_id"])
                await self.bot.edit_message_reply_markup(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, reply_markup=None)
            await self.bot.send_message(user_id, text = ("❌Вопрос отклонен"))
            await state_manager(user_id, 'free')
        # get input from - client|admin    
        @self.dp.message(F.text)
        async def process__ticket(message: types.Message):
            state = await state_manager(message.from_user.id, 'get')
            user = await self.db_instance.get_user(message.from_user.id)
            if state[0]["state"] == "polling":
                admin = await self.db_instance.check_admin(message.from_user.id)
                if admin == False:
                        await message.answer(
                            text = messages.submit_ticket_message(message.text), 
                            parse_mode = ParseMode.HTML, 
                            reply_markup = await keyboard.create_ticket()
                            )
                        await self.db_instance.set_state(message.from_user.id, "free")
                        await self.db_instance.create_ticket(message.from_user.id, message.text)
                        print(message.message_id)
                        await self.bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
                        await self.bot.delete_message(chat_id=message.from_user.id, message_id=(int(message.message_id)-1))
                else:
                    ticket_id = user[0]["current_ticket"]
                    ticket = await self.db_instance.get_ticket(ticket_id = ticket_id)
                    print(ticket)
                    await message.answer(
                        text = "Ответ отправлен!", 
                        )
                    await state_manager(message.from_user.id, 'free')
                    await self.bot.send_message(
                        chat_id = int(ticket[0]["user_id"]),
                        text = f"💬Получен ответ на \nваш вопрос №{ticket_id}:\n\n<b>{message.text}</b>",
                        reply_markup=await keyboard.finish_ticket(),
                        parse_mode = ParseMode.HTML)
                    await self.db_instance.process_ticket(ticket_id, message.from_user.id, "claimed", "completed")
                    await state_manager(int(ticket[0]["user_id"]), 'free')
            else:
                return
        # process callbacks 
        @self.dp.callback_query()
        async def process_callback(callback_query: types.CallbackQuery):
            if callback_query.data == "create_ticket":
                await create_ticket(callback_query)
            elif callback_query.data == "open_profile":
                await open_profile(callback_query)
            elif callback_query.data == "send":
                await send_ticket(callback_query)
            elif callback_query.data == "cancel":
                await cancel_ticket(callback_query, 'user')
            elif callback_query.data.startswith("answer"):
                await answer_ticket(callback_query)
            elif callback_query.data.startswith("decline"):
                await cancel_ticket(callback_query, 'admin')
            elif callback_query.data == "back":
                await start(callback_query.message)

        