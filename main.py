# import asyncio
# from datetime import datetime, time, timedelta, timezone
#
# from aiogram import Bot, Dispatcher
# from aiogram.filters import Command
#
# tg_token = "8112532328:AAGh4RgUwkNXpoGdZhvZV7Q3m4kMt0R3QzA"
# bot = Bot(token=tg_token)
# dp = Dispatcher()
#
# TARGET_CHAT_ID = None
#
# @dp.message(Command(commands=["start"]))
# async def start_handler(message):
#     global TARGET_CHAT_ID
#     TARGET_CHAT_ID = message.chat.id
#     await message.reply("Напоминания будут отправляться с 20:00 до 23:00 каждый день (UTC+6).")
#
# async def schedule_daily_reminders():
#     # фиксированный часовой пояс +06:00
#     tz = timezone(timedelta(hours=6))
#     while True:
#         now = datetime.now(tz)
#
#         # когда сегодня в 20:00, иначе завтра
#         today_20 = datetime.combine(now.date(), time(20, 0), tz)
#         next_start = today_20 if now < today_20 else today_20 + timedelta(days=1)
#
#         # ждём до 20:00
#         await asyncio.sleep((next_start - now).total_seconds())
#
#         # отправляем в 20, 21, 22 и 23 часа
#         for hour in range(20, 24):
#             send_time = datetime.combine(next_start.date(), time(hour, 0), tz)
#             now_inner = datetime.now(tz)
#             delay = max(0, (send_time - now_inner).total_seconds())
#             await asyncio.sleep(delay)
#             if TARGET_CHAT_ID:
#                 await bot.send_message(chat_id=TARGET_CHAT_ID, text="Выпейте лекарство")
#         # и цикл повторяется
#
# async def main():
#     asyncio.create_task(schedule_daily_reminders())
#     await dp.start_polling(bot)
#
# if __name__ == "__main__":
#     asyncio.run(main())
