from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from app.config import settings
from app.db.repository import UserRepository

router = Router()


@router.callback_query(F.data.startswith("fav:add:"))
async def add_favorite(call: CallbackQuery, user_repo: UserRepository) -> None:
    vacancy_id = call.data.split(":")[2]
    text = call.message.text or ""
    title = text.split("\n")[0].replace("🔥 ", "").replace("*", "")[:250] or "Вакансия"
    city = "Не указан"
    salary = "Не указана"
    if "\n" in text:
        second_line = text.split("\n")[1]
        if "•" in second_line:
            parts = [part.strip("📍💰 ").strip() for part in second_line.split("•")]
            if len(parts) >= 2:
                city, salary = parts[0], parts[1]
    url = ""
    if call.message.reply_markup and call.message.reply_markup.inline_keyboard:
        first_button = call.message.reply_markup.inline_keyboard[0][0]
        url = first_button.url or ""

    ok = await user_repo.add_favorite(
        call.from_user.id,
        {"vacancy_id": vacancy_id, "title": title, "salary": salary, "city": city, "url": url},
    )
    await call.answer("Добавлено в избранное ⭐" if ok else "Уже есть в избранном")


@router.message(F.text == "⭐ Избранное")
async def show_favorites(message: Message, user_repo: UserRepository) -> None:
    items = await user_repo.list_favorites(message.from_user.id)
    if not items:
        await message.answer("Пока избранное пусто.")
        return
    await message.answer("Твое избранное:")
    for item in items:
        await message.answer(
            f"⭐ *{item['title']}*\n📍 {item['city']} • 💰 {item['salary']}\n👉 {item['url']}"
        )
