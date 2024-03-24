import telebot, datetime, time, random, string, requests
from bs4 import BeautifulSoup as bs

bot = telebot.TeleBot("6376225703:AAFxQL4lEqLMJbzzNTFe_T5RfZ7HnLMP3h0")
user_states = {}
user_info = {}


@bot.message_handler(commands=["start"])
def handle_start(message):
    bot.send_message(message.chat.id, "اكتب رقمك")
    user_states[message.from_user.id] = "waiting_for_phone_number"


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    if user_id in user_states:
        if user_states[user_id] == "waiting_for_phone_number":
            if len(message.text) == 11:
                user_info[user_id] = {"phone_number": message.text}
                bot.send_message(user_id, "اكتب باسورد انا فودافون")
                user_states[user_id] = "waiting_for_password"
            else:
                bot.send_message(user_id, "الرقم غلط يغالي حاول تاني")

        elif user_states[user_id] == "waiting_for_password":
            user_info[user_id]["password"] = message.text
            del user_states[user_id]

            PHONE_NUMBER = user_info.get(user_id)["phone_number"]
            PASSWORD = user_info.get(user_id)["password"]
            TARGET = 85
            CHARGE_THRESHOLD = 1000

            def authenticate(username, password):
                session = requests.Session()

                def generate_random_chars(length):
                    alpha_lower = string.ascii_lowercase
                    return "".join(random.choice(alpha_lower) for _ in range(length))

                url = (
                    "https://web.vodafone.com.eg/auth/realms/vf-realm/protocol/"
                    "openid-connect/auth?client_id=website&redirect_uri=https%3A%2F%2F"
                    "web.vodafone.com.eg%2Fspa%2FmyHome&state=1d6b3a62-f722-4d4e-b122-6facadd2ec5f&"
                    "response_mode=query&response_type=code&scope=openid&"
                    f"nonce={generate_random_chars(10)}&ui_locales=ar"
                )
                response_for_url = session.get(url)
                parsed_url = bs(response_for_url.content, "html.parser")
                get_link = parsed_url.find("form").get("action")

                request_headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Origin": "https://web.vodafone.com.eg",
                    "Connection": "keep-alive",
                }

                data = {
                    "username": f"{username}",
                    "password": f"{password}",
                }
                response = session.post(get_link, headers=request_headers, data=data)
                check_login = response.url

                def get_auth_token():
                    if "realms" not in check_login:
                        token_code = check_login[check_login.index("code=") + 5 :]
                        headers = {
                            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
                            "Accept": "*/*",
                            "Accept-Language": "en-US,en;q=0.5",
                            "Content-type": "application/x-www-form-urlencoded",
                            "Origin": "https://web.vodafone.com.eg",
                            "Connection": "keep-alive",
                            "Referer": "https://web.vodafone.com.eg/spa/myHome",
                        }
                        data_access_token = {
                            "code": token_code,
                            "grant_type": "authorization_code",
                            "client_id": "website",
                            "redirect_uri": "https://web.vodafone.com.eg/spa/myHome",
                        }
                        token_url = "https://web.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
                        send_access_token = session.post(
                            token_url, headers=headers, data=data_access_token
                        )
                        auth_token = f"{send_access_token.json()['token_type']} {send_access_token.json()['access_token']}"
                        return auth_token
                    else:
                        raise Exception("auth_err")

                return get_auth_token()

            def get_promotion_cards(token, phone_number):
                headers = {
                    "Accept": "application/json",
                    "Accept-Language": "AR",
                    "Authorization": token,
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "application/json",
                    "Pragma": "no-cache",
                    "Referer": "https://web.vodafone.com.eg/portal/bf/hub",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
                    "api-host": "PromotionHost",
                    "channel": "APP_PORTAL",
                    "clientId": "WebsiteConsumer",
                    "msisdn": f"{phone_number}",
                    "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                }
                response = requests.get(
                    f"https://web.vodafone.com.eg/services/dxl/ramadanpromo/promotion?@type=RamadanHub&channel=website&msisdn={phone_number}",
                    headers=headers,
                )
                return response.json()

            def filter_cards(cards):
                cards = cards[1].get("pattern")
                parent_cards_dict = {}
                c_id = 0

                for card in cards:
                    card_info = card.get("action")[0].get("characteristics")
                    parent_cards_dict[c_id] = card_info
                    c_id += 1
                    parsed_cards_parent = []
                    for card in parent_cards_dict.values():
                        parsed_cards_child = []
                        for lv1 in card:
                            parsed_cards_child.append(lv1.get("value"))
                        parsed_cards_parent.append(parsed_cards_child)

                    return parsed_cards_parent

            def set_target(cards, target):
                target_cards = []
                for card in cards:
                    if int(float(card[1])) >= int(target):
                        target_cards.append(card)
                return target_cards

            def auto_charge(token, phone_number, serial):
                headers = {
                    "Accept": "application/json",
                    "Accept-Language": "AR",
                    "Authorization": token,
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "application/json",
                    "Origin": "https://web.vodafone.com.eg",
                    "Pragma": "no-cache",
                    "Referer": "https://web.vodafone.com.eg/portal/bf/hub",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
                    "channel": "APP_PORTAL",
                    "clientId": "WebsiteConsumer",
                    "msisdn": f"{phone_number}",
                    "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                }
                json_data = {
                    "msisdn": f"{phone_number}",
                    "promoId": "4940",
                    "channelId": 1,
                    "param1": f"{serial}",
                    "param2": "4",
                    "wlistId": "4661",
                    "category": "Contextual",
                    "triggerId": "876",
                }
                response = requests.post(
                    "https://web.vodafone.com.eg/services/promo/unifiedAssignPromo",
                    headers=headers,
                    json=json_data,
                )
                return response.json()

            def main():
                try:
                    token = authenticate(PHONE_NUMBER, PASSWORD)
                    bot.send_message(
                        message.chat.id, "تمام يزميل اقفل البوت و استني رسالة  😁"
                    )
                    del user_info[user_id]
                    while True:
                        cards = get_promotion_cards(token, PHONE_NUMBER)
                        filtered_cards = filter_cards(cards)
                        target_cards = set_target(filtered_cards, TARGET)
                        if target_cards:
                            for card in target_cards:
                                if int(float(card[1])) >= int(CHARGE_THRESHOLD):
                                    response = auto_charge(
                                        token, PHONE_NUMBER, int(card[3])
                                    )
                                    if response.get("eDescription") == "Success":
                                        success_time = datetime.datetime.now().strftime(
                                            "%H:%M:%S"
                                        )
                                        bot.send_message(
                                            message.chat.id,
                                            f"[Success] Auto charge successful😁:\n[\u2713] Number  =>  {PHONE_NUMBER}\n[\u2713] Card  =>  <code>*858*{card[3]}#</code>\n[\u2713] Amount  =>  {card[1]} Units\n[\u2713] Time  =>   {success_time}\n[-] [ اضغط علي رقم الكارت هيتنسخ ]",
                                            parse_mode="HTML",
                                        )
                                        bot.delete_message(
                                            message.chat.id, message.message_id + 1
                                        )
                                        return
                                    else:
                                        bot.send_message(
                                            message.chat.id,
                                            f"[Failed] Auto charge failed:",
                                            response.get("eDescription"),
                                        )
                                        bot.delete_message(
                                            message.chat.id, message.message_id + 1
                                        )

                        else:
                            pass
                        time.sleep(1)

                except Exception as e:
                    if str(e) == "auth_err":
                        bot.send_message(
                            message.chat.id,
                            f"الرقم او الباسورد غلط او الحساب متعلق مؤقتا , حاول بعد شوية 🔐",
                        )
                        return
                    elif str(e) == "'NoneType' object is not iterable":
                        bot.send_message(
                            message.chat.id,
                            "انت خلصت شحنة النهاردة , تعالا تاني بكرا 😢",
                        )
                        bot.delete_message(message.chat.id, message.message_id + 1)
                        return
                    else:
                        bot.send_message(
                            message.chat.id,
                            f"في مشكلة , حاول تاني",
                        )
                        bot.delete_message(message.chat.id, message.message_id + 1)
                        return

            main()
    else:
        bot.send_message(user_id, "/start  اضغط عشان تشغل البوت")


bot.polling()
