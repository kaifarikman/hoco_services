# Рассылка по пользователям о напоминании оплаты чтоли + показания счетчиков
import bot.db.crud.users as crud_users
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from bot.bot import bot


async def send_message_(user_id, days_before):
    message = f"Уважаемый пользователь, до срока оплаты аренды осталось {days_before} дня(ей). Пожалуйста, убедитесь, что оплата будет произведена своевременно."
    try:
        await bot.send_message(
            chat_id=user_id,
            text=message
        )
    except Exception as e:
        print(e)


async def send_message2(user_id, current_day):
    if current_day == 20:
        message = f"Уважаемый пользователь, напомним, что 20-е число месяца — время подать показания счетчиков."
    elif current_day == 22:
        message = f"Уважаемый пользователь, 22-е число месяца — не забудьте подать показания счетчиков."
    elif current_day == 25:
        message = f"Уважаемый пользователь, сегодня 25-е число месяца. Это ваш последний шанс подать показания счетчиков вовремя!"
    else:
        return "botva"
    try:
        await bot.send_message(
            chat_id=user_id,
            text=message
        )
    except Exception as e:
        print(e)


async def mailer():
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    days_before_list = [5, 2]
    all_users = crud_users.get_all_users()
    for user in all_users:
        if not user.auth:
            continue
        if user.was_deleted:
            continue
        user_id = user.user_id
        if user.meter_notification:
            days_list = [20, 22, 25]

            for day in days_list:
                scheduler.add_job(
                    send_message2,
                    CronTrigger(day=day, hour=12, minute=0),
                    args=[user_id, day]
                )
        if user.rent_notification:
            due_date = user.due_date
            for days_before in days_before_list:
                due_date_obj = datetime.now().replace(day=due_date, hour=14, minute=0, second=0, microsecond=0)
                task_date = due_date_obj - timedelta(days=days_before)

                if task_date >= datetime.now():
                    scheduler.add_job(
                        send_message_,
                        CronTrigger(day=task_date.day, month=task_date.month, hour=14, minute=0),
                        args=[user_id, days_before]
                    )
    scheduler.start()
