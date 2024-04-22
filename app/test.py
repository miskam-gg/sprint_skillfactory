import unittest
import asyncio
from app import DataBase, PerevalData


class TestDataBase(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.db = DataBase()
        await self.db.connect()

    async def asyncTearDown(self):
        await self.db.close()

    async def test_add_pereval(self):
        pereval_data = PerevalData(
            raw_data="Test raw data",
            beautyTitle="Test beauty title",
            title="Test title",
            add_time="2024-04-19",
            summer_level="Test summer level",
            autumn_level="Test autumn level",
            coords_id=1
        )
        await self.db.add_pereval(pereval_data)
        pereval = await self.db.get_pereval_by_id(1)  # Проверяем, что запись действительно добавлена в базу данных
        self.assertIsNotNone(pereval)
        self.assertEqual(pereval['title'], "Test title")
        self.assertEqual(pereval['raw_data'],"Test raw data")  # Проверяем, что поля записи соответствуют ожидаемым значениям
        self.assertEqual(pereval['beautyTitle'], "Test beauty title")


if __name__ == '__main__':
    unittest.main()
