def seriously_give_role(superuser_type, name):
    d = {
        "superadmin": "суперадмина",
        "admin": "админа",
        "accountant": "бухгалтера",
    }
    return f"Вы действительно хотите выдать {name} роль {d[superuser_type]}?"


def really_delete_person(superuser):
    return f"Вы действительно хотите удалить {superuser.name} из Базы Данных администрации?"


no_access = "У вас нет доступа"
hello_superadmin = "Вы - суперадмин."
seriously_complete = "Вы точно хотите завершить заявку?"
no_complete = "Статус заявки остался неизменным. Вы можете выйти в главное меню"
sent_to_achieve = "Заявка отправлена в архив"
choice_newsletter_text = "Выберите адрес для рассылки"
give_role = "Ваш функционал"
select_an_employee_for_settings = "Выберите сотрудника для настроек"
add_new_user_name_text = "Введите имя пользователя"
add_new_user_inn_text = "Введите ИНН пользователя"
add_new_user_phone_number_text = (
    "Введите номер телефона пользователя.\nФормат: начинается с 79"
)
add_new_user_due_date_text = "Введите срок оплаты аренды пользователя.\nНапример: 13"
sent_new_superuser = "Отправьте user_id в телеграмме нового сотрудника"
sent_new_superuser_user_id_please = "Отправьте user_id в числовом типе"
sent_name = "Введите имя пользователя"
sent_superuser_role = "Выберите роль для пользователя"
add_new_user_office_address_text = "Введите адрес офиса пользователя."
add_new_user_office_office_number_text = "Введите номер офиса пользователя."
add_new_user_office_meters_text = "Введите счетчики через пробел. 1 - Электричество, 2 - Вода"
work_with_db_text = "Работа с Базой"
