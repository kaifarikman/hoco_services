def meter_readings(meter_type, unit):
    return f"Введите показания счетчика {str(meter_type)} в {str(unit)}"


def check_reading(office_address,office_number, meter_type, readings, unit):
    s = "Ваша заявка:\n"
    s += f"{office_address}, {office_number}\nТип счетчика:{meter_type}\n{readings} {unit}\n"
    s += f"Отправить показания?"
    return s


def get_user_statement_shell(statement):
    return "botva"


start_true_text = "Главное меню пользователя"
start_false_text = "У вас нет доступа"
send_inn = "Введите ИНН"
send_number = "Введите номер телефона"
no_access = "Вас нет в Базе Данных. Для продолжения пользования ботом нажмите /start"
yes_access = (
    "Вы успешно зарегистрированы. Нажмите на /start для дальнейшего пользования ботом"
)
new_statement_text = "Введите описание вашей заявки или вопроса"
you_cant_send_voice_messages = "Запрещено отправлять голосовые сообщения и документы. Пожалуйста, введите в текстовом формате или в формате медиа"

no_format_to_create_statement = "Данный формат заявки не поддерживается. Выйдите в главное меню или отправьте заявку заново"
to_long = "Слишком много медии в одном сообщении, не более 3-х файлов одновременно. Данный формат не поддерживается. Можете отправить данные заново или выйти в главное меню"
application_sent_for_moderation = "Заявка отправлена на модерацию. Ожидайте ответа"
submitting_meter_readings_text = (
    "Необходимо подать показания счетчиков до 25 числа включительно"
)
no_offices_yet = "У вас нет офисов"
no_statements_yet = "На данный момент вы не создали ни одной заявки"
user_statements_text = "Ваши заявки"
meter_readings_sent_text = "Показания счетчиков отправлены"
no_meter_readings_sent_text = "Вы отменили отправку показаний счетчиков"
select_counter_text = "Выберите тип счетчика"
request_for_other_documentation_text = "Введите необходимую документацию для запроса"
documentation_sent = "Документация отправлена на обработку"
ku_text = (
    """Ваша заявка начисление КУ принята, ожидайте ответ в разделе "Мои заявки" """
)
rent_accuracy_text = (
    """Ваша заявка начисление Аренды принята, ожидайте ответ в разделе "Мои заявки" """
)
request_for_reconciliation_report_text = """Ваша заявка запроса Акта сверки принята, ожидайте ответ в разделе "Мои заявки" """
my_statement_answer = "Введите ваш ответ на заявку №{number}"
successfully_sent = "Ваш ответ успешно отправлен"
statement_status_completed = "Заявка уже завершена. На нее невозможно ответить"
error_format_message = "Неверный формат сообщения. Необходимо создать «Новую заявку» или нажать «Ответить»."