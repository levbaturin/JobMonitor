import sqlite3

# Подключиться к БД
conn = sqlite3.connect('data/data.db')
cursor = conn.cursor()

# Добавить колонку source
try:
    cursor.execute("ALTER TABLE groups ADD COLUMN source VARCHAR(10) DEFAULT 'vk'")
    print("✅ Колонка source добавлена")
except sqlite3.OperationalError as e:
    print(f"⚠️ Ошибка: {e}")

# Обновить существующие записи
cursor.execute("UPDATE groups SET source = 'vk' WHERE source IS NULL")
conn.commit()
print("✅ Данные обновлены")

# Проверить результат
cursor.execute("PRAGMA table_info(groups)")
columns = cursor.fetchall()
print("\n✅ Структура таблицы groups:")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

conn.close()
