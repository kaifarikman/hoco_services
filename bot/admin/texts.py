from bot.db.crud.statements import Statements


def get_statement_shell(statement: Statements):
    return "botva"


def input_newsletter_text(address):
    return f"Введите текст для рассылки по адресу: {address}"


no_access = "У вас нет доступа к правам админа"
access_admin = "Заявки на рассмотрение"
always_edited = "Данная заявка уже взята в работу"
set_theme = "Введите тему заявки одним словом"
theme_changed = "Тема заявки сменилась"
choice_newsletter_text = "Выберите адрес для рассылки"
newsletter_sent = "Ваше сообщение отправлено"
status_changed = """Статус заявки сменился на "В работе" """
sent_answer_to_user = "Напишите ответ по заявке"
no_format_to_create_statement = "Данный формат ответа на заявку не поддерживается."
to_long = "Слишком много медии в одном сообщении. Данный формат не поддерживается. Отправьте ответ заново"
successfully_sent = "Ответ по заявке успешно отправлен пользователю"
