from fastapi import FastAPI, HTTPException
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
                print("Record inserted successfully")
            except asyncpg.PostgresError as e:
                print("Error: Could not insert record")
                print(e)


db = DataBase()  # Экземпляр класса для работы с базой данных


@app.post("/submitData")  # Метод для добавления нового перевала
async def submit_data(pereval_data: PerevalData):
    await db.add_pereval(pereval_data)
    return {"message": "Данные успешно переданы."}


@app.on_event("startup")  # Запуск подключения к базе данных при старте приложения
async def startup():
    await db.connect()


@app.on_event("shutdown")  # Закрытие соединения с базой данных при остановке приложения
async def shutdown():
    await db.close()
