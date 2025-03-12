# -*- coding: utf-8 -*-

# Developer: Nethanter-del
# Github: https://github.com/Nethanter-del
# Date Created: 2025-12-03
# Version: 1.0.0

# License: MIT License
#
# Copyright (c) 2025 Nethanter-del

import asyncpg
from dotenv import dotenv_values

class bd:
    def __init__(self, host, user, password, database, owner):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.owner = owner
        self.conn = None

    async def init_db(self):
        try:
            self.conn = await asyncpg.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            await self.create_tables()
        except Exception:
            print(f"CRITICAL:-Connection to {self.database} corrupted")
            exit()
    async def create_tables(self):
        tables = '''CREATE TABLE IF NOT EXISTS public.tickets
(
    ticket_id SERIAL NOT NULL,
    user_id bigint NOT NULL,
    ticket text COLLATE pg_catalog."default" NOT NULL,
    status text COLLATE pg_catalog."default",
    CONSTRAINT tickets_pkey PRIMARY KEY (ticket_id)
)

TABLESPACE pg_default;

CREATE TABLE IF NOT EXISTS public.users
(
    id SERIAL NOT NULL,
    user_id bigint NOT NULL,
    username text COLLATE pg_catalog."default",
    is_admin boolean NOT NULL,
    state text COLLATE pg_catalog."default",
    current_ticket bigint,
    CONSTRAINT users_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;'''
        await self.conn.execute(tables)
    # unformated response to dictionary        
    async def format_response(self, values):
        return  [dict(record) for record in values]
    # create user
    async def create_user(self, user_id, username):
        is_admin = False
        if str(user_id) == str(self.owner):
            is_admin = True
        await self.conn.execute("INSERT INTO users (user_id, username, is_admin) VALUES ($1, $2, $3)", user_id, username, is_admin)
    # fetch user info   
    async def get_user(self, user_id):
        values = await self.conn.fetch(f"SELECT * FROM users WHERE user_id = {user_id}")
        return await self.format_response(values)
    
    # check admin status True|False
    async def check_admin(self, user_id):
        values = await self.conn.fetch(f"SELECT * FROM users WHERE user_id = {user_id} AND is_admin = true")
        if len(values) > 0:
            return True
        else:
            return False
    # fetch all admins 
    async def select_admins(self):
        values = await self.conn.fetch(f"SELECT user_id FROM users WHERE is_admin = True")
        return await self.format_response(values)
    # get user state polling|waiting|free
    async def get_state(self, user_id):
        values = await self.conn.fetch(f"SELECT state FROM users WHERE user_id = {user_id}")
        return await self.format_response(values)
    # set user state polling|waiting|free
    async def set_state(self, user_id, state):
        await self.conn.execute("UPDATE users SET state = $1 WHERE user_id = $2", state, user_id)
    # create new ticket    
    async def create_ticket(self, user_id, ticket_text):
        await self.conn.execute("INSERT INTO tickets (user_id, ticket, status) VALUES ($1, $2, $3)", user_id, ticket_text, 'waiting')
    # register created ticket 
    async def register_ticket(self, user_id):
        await self.conn.execute("UPDATE tickets SET status = $1 WHERE user_id = $2 AND status = 'waiting'", 'opened', user_id)
    # fetch created ticket info by user_id OR ticked_id
    async def get_ticket(self, user_id = 0, ticket_id = 0):
        values = await self.conn.fetch(f"SELECT * FROM tickets WHERE (user_id = $1 AND status = 'opened') OR ticket_id = $2", int(user_id), int(ticket_id))
        return await self.format_response(values)
    # delete ticket by user_id OR ticked_id
    async def del_ticket(self, user_id, ticket_id = 0):
        if user_id > 1:
            await self.conn.execute("DELETE FROM tickets WHERE user_id = $1::bigint AND status = 'waiting'", (user_id))
        else:
            await self.conn.execute("DELETE FROM tickets WHERE ticket_id = $1 OR (user_id = $2::bigint AND status = 'waiting')", int(ticket_id), int(user_id))
    # update ticket status        
    async def process_ticket(self, ticket_id=0, user_id=0, Fstatus="opened", Dstatus="claimed"):
        if Dstatus == "claimed":
            await self.conn.execute("UPDATE users SET current_ticket = $1 WHERE user_id = $2", int(ticket_id), int(user_id), )
        elif Dstatus == "completed":
            await self.conn.execute("UPDATE users SET current_ticket = $1 WHERE user_id = $2", 0, int(user_id), )
        await self.conn.execute("UPDATE tickets SET status = $1 WHERE ticket_id = $2 AND status = $3", Dstatus, int(ticket_id), Fstatus)
    
    