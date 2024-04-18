-- Создание таблицы Users для хранения данных о пользователях
CREATE TABLE "public"."Users" (
    "id" SERIAL PRIMARY KEY,
    "email" VARCHAR(255) UNIQUE NOT NULL,
    "phone" VARCHAR(20),
    "fam" TEXT,
    "name" TEXT,
    "otc" TEXT
);

-- Создание таблицы Coords для хранения координат перевалов
CREATE TABLE "public"."Coords" (
    "id" SERIAL PRIMARY KEY,
    "latitude" FLOAT,
    "longitude" FLOAT,
    "height" INT
);

-- Создание таблицы pereval_added для хранения информации о перевалах
CREATE TABLE "public"."pereval_added" (
    "id" SERIAL PRIMARY KEY,
    "date_added" TIMESTAMP,
    "status" VARCHAR(20),
    "raw_data" JSON,
    "beautyTitle" TEXT,
    "title" TEXT,
    "other_titles" TEXT,
    "connect" TEXT,
    "add_time" TIMESTAMP,
    "summer_level" TEXT,
    "autumn_level" TEXT,
    "coords_id" INT REFERENCES "Coords" ("id")
);

-- Создание таблицы pereval_images для хранения информации об изображениях перевалов
CREATE TABLE "public"."pereval_images" (
    "id" SERIAL PRIMARY KEY,
    "pereval_id" INT REFERENCES "pereval_added" ("id"),
    "img" BYTEA NOT NULL
);

-- Добавление внешнего ключа для связи между таблицей pereval_added и таблицей Coords
ALTER TABLE "public"."pereval_added"
ADD CONSTRAINT "fk_coords"
FOREIGN KEY ("coords_id")
REFERENCES "Coords" ("id");

-- Добавление индекса для улучшения производительности запросов по полю status в таблице pereval_added
CREATE INDEX "idx_pereval_added_status" ON "public"."pereval_added" ("status");