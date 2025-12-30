from aiogram.filters import BaseFilter
from aiogram.types import Message
from data.database import db

class IsAdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        """Проверить, является ли отправитель сообщения админом."""

        if not message.from_user:
            await message.answer("❌ Ошибка: не удалось получить данные пользователя")
            return False

        return db.check_is_admin(message.from_user.id)