from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import asyncpg
import os

app = FastAPI()


class PerevalData(BaseModel):  # Модель данных для запроса на добавление нового перевала
    raw_data: str
    beautyTitle: str
    title: str
    other_titles: str = ""
    connect: str = ""
    add_time: str
    summer_level: str
    autumn_level: str
    coords_id: int


class PerevalEdit(BaseModel):  # Модель данных для запроса на редактирование перевала
    raw_data: str
    beautyTitle: str
    title: str
    other_titles: str = ""
    connect: str = ""
    add_time: str
    summer_level: str
    autumn_level: str
    coords_id: int


class DataBase:  # Класс для работы с базой данных
    def __init__(self):
        self.db_host = os.getenv("FSTR_DB_HOST")
        self.db_port = os.getenv("FSTR_DB_PORT")
        self.db_login = os.getenv("FSTR_DB_LOGIN")
        self.db_pass = os.getenv("FSTR_DB_PASS")

    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(
                host=self.db_host,
                port=self.db_port,
                user=self.db_login,
                password=self.db_pass,
                database="pereval"
            )
            print("Подключен к базе данных.")
        except asyncpg.PostgresError as e:
            print("Ошибка: Не удалось подключиться к базе данных.")
            print(e)

    async def close(self):
        await self.pool.close()

    async def add_pereval(self, data):
        async with self.pool.acquire() as conn:
            try:
                await conn.execute("""
                    INSERT INTO pereval_added (date_added, status, raw_data, beautyTitle, title, other_titles, connect, add_time, summer_level, autumn_level, coords_id)
                    VALUES (CURRENT_TIMESTAMP, 'new', $1, $2, $3, $4, $5, $6, $7, $8, $9)
                """, data.raw_data, data.beautyTitle, data.title, data.other_titles, data.connect, data.add_time,
                                   data.summer_level, data.autumn_level, data.coords_id)
                print("Запись успешно вставлена.")
            except asyncpg.PostgresError as e:
                print("Ошибка: Не удалось вставить запись.")
                print(e)

    async def get_pereval_by_id(self, pereval_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("SELECT * FROM pereval_added WHERE id = $1", pereval_id)

    async def edit_pereval(self, pereval_id, data):
        async with self.pool.acquire() as conn:
            try:
                await conn.execute("""
                    UPDATE pereval_added
                    SET raw_data = $1, beautyTitle = $2, title = $3, other_titles = $4,
                    connect = $5, add_time = $6, summer_level = $7, autumn_level = $8, coords_id = $9
                    WHERE id = $10 AND status = 'new'
                """, data.raw_data, data.beautyTitle, data.title, data.other_titles,
                                   data.connect, data.add_time, data.summer_level, data.autumn_level,
                                   data.coords_id, pereval_id)
                return {"state": 1, "message": "Запись успешно обновлена."}
            except asyncpg.PostgresError as e:
                return {"state": 0, "message": f"Ошибка: не удалось обновить запись. {e}"}

    async def get_perevals_by_user_email(self, user_email):
        async with self.pool.acquire() as conn:
            return await conn.fetch("SELECT * FROM pereval_added WHERE raw_data->'user'->>'email' = $1", user_email)


db = DataBase()  # Экземпляр класса для работы с базой данных


@app.post("/submitData")  # Метод для добавления нового перевала
async def submit_data(pereval_data: PerevalData):
    await db.add_pereval(pereval_data)
    return {"message": "Данные успешно переданы."}


@app.get("/submitData/{pereval_id}")  # Метод для получения одной записи (перевала) по её id
async def get_pereval(pereval_id: int):
    return await db.get_pereval_by_id(pereval_id)


@app.patch("/submitData/{pereval_id}")  # Метод для редактирования существующей записи (замены)
async def edit_pereval(pereval_id: int, pereval_data: PerevalEdit):
    return await db.edit_pereval(pereval_id, pereval_data)


@app.get("/submitData/")  # Метод для получения списка данных обо всех объектах, отправленных пользователем с указанным email
async def get_perevals_by_user_email(user_email: str = Query(...)):
    return await db.get_perevals_by_user_email(user_email)


@app.on_event("startup")  # Запуск подключения к базе данных при старте приложения
async def startup():
    await db.connect()


@app.on_event("shutdown")  # Закрытие соединения с базой данных при остановке приложения
async def shutdown():
    await db.close()
