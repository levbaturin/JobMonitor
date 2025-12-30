import asyncio
from telethon import TelegramClient
import json

API_ID = int(input("Введите API_ID: "))
API_HASH = input("Введите API_HASH: ")

async def check_credentials():
    try:
        client = TelegramClient('session', API_ID, API_HASH)

        print("🔄 Подключаюсь к Telegram...")
        await client.start()

        print("✅ Успешно подключился!")

        me = await client.get_me()
        print(f"\n👤 Текущий пользователь: {me.first_name}")

        return client

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

async def get_messages_sample(client, entity):
    """Получить примеры сообщений"""

    try:
        print(f"\n📨 Получаю последние сообщения...")

        messages = []
        async for message in client.iter_messages(entity, limit=5):
            messages.append(message)

        print(f"\n📝 Последние {len(messages)} сообщений:")
        print("-" * 80)

        for i, msg in enumerate(reversed(messages), 1):
            print(f"\n{i}. Сообщение ID: {msg.id}")
            print(f"   Дата: {msg.date}")
            print(f"   Текст: {msg.text[:100] if msg.text else '[БЕЗ ТЕКСТА]'}...")
            print()

    except Exception as e:
        print(f"❌ Ошибка: {e}")

async def main():
    print("=" * 80)
    print("🔐 Проверка Telegram Credentials")
    print("=" * 80)

    client = await check_credentials()

    if not client:
        return

    while True:
        print("\n" + "=" * 80)
        print("Что вы хотите сделать?")
        print("1. Список всех диалогов с правильными ID")
        print("2. Получить сообщения из диалога (по названию)")
        print("0. Выход")
        print("=" * 80)

        choice = input("\nВыберите опцию (0-2): ").strip()

        if choice == '0':
            print("👋 До свидания!")
            break

        elif choice == '1':
            await list_dialogs(client)

        elif choice == '2':
            name = input("Введите название группы/чата: ").strip()
            entity = await find_dialog_by_name(client, name)
            if entity:
                print(f"\n✅ Найден диалог: {entity[1]}")
                print(f"   Entity ID: {entity[0]}")
                await get_messages_sample(client, entity[0])

        else:
            print("❌ Неверная опция")

    await client.disconnect()

async def list_dialogs(client):
    """Получить список диалогов с правильными ID"""

    try:
        print("\n📋 Ваши диалоги с правильными entity ID:")
        print("-" * 80)

        dialogs = []
        async for dialog in client.iter_dialogs(limit=20):
            entity = dialog.entity
            name = entity.title if hasattr(entity, 'title') else entity.first_name

            # Правильный entity (объект, а не ID)
            dialogs.append((entity, name))

            print(f"Название: {name}")
            print(f"  Entity: {entity}")
            print(f"  Type: {type(entity).__name__}")
            print()

    except Exception as e:
        print(f"❌ Ошибка: {e}")

async def find_dialog_by_name(client, name):
    """Найти диалог по названию"""

    try:
        async for dialog in client.iter_dialogs():
            entity = dialog.entity
            dialog_name = entity.title if hasattr(entity, 'title') else entity.first_name

            if name.lower() in dialog_name.lower():
                return (entity, dialog_name)

        print(f"❌ Диалог '{name}' не найден")
        return None

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

if __name__ == '__main__':
    asyncio.run(main())
