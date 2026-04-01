from aiogram import Router, types
from loguru import logger


router = Router()


@router.errors()
async def error_handler(event: types.ErrorEvent):
    logger.exception("An unhandled exception occurred: {}", event.exception)
    
    # Можно отправить сообщение пользователю, если это уместно
    # try:
    #     if event.update.message:
    #         await event.update.message.answer("Произошла ошибка при обработке запроса. Попробуйте позже.")
    #     elif event.update.callback_query:
    #         await event.update.callback_query.answer("Произошла ошибка. Попробуйте позже.", show_alert=True)
    # except Exception as e:
    #     logger.error("Could not send error message to user: {}", e)
