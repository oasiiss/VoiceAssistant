import openai, datetime

api_key = "<your api>"

months = {
    "january": "Ocak",
    "february": "Şubat",
    "march": "Mart",
    "april": "Nisan",
    "may": "Mayıs",
    "june": "Haziran",
    "july": "Temmuz",
    "august": "Ağustos",
    "september": "Eylül",
    "october": "Ekim",
    "november": "Kasım",
    "december": "Aralık"
}

days = {
    "monday": "Pazartesi",
    "tuesday": "Salı",
    "wednesday": "Çarşamba",
    "thursday": "Perşembe",
    "friday": "Cuma",
    "saturday": "Cumartesi",
    "sunday": "Pazar"
}


def ChatAnswer(text):
    openai.api_key = api_key
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": text},
                {"role": "user", "content": "cevabın maksimum 20 kelimeden oluşsun, bir arkadaşmış gibi cevap ver, birden fazla soru sorma ve Türkçe cevap ver"},
            ]
        )
        message = response['choices'][0]['message']['content']
        return [True, message]
    except Exception as e:
        return [False, e]
    
def CreateImage(prompt):
    openai.api_key = api_key
    try:
        response = openai.Image.create(
            model="dall-e-2",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        return [True, image_url]
    except Exception as e:
        return [False, str(e)]

def get_current_datetime():
    now = datetime.datetime.now()
    return f"Bugün günlerden {now.strftime('%d')} {months[str(now.strftime('%B')).lower()]} {days[str(now.strftime('%A')).lower()]} saat {now.strftime('%H')}:{now.strftime('%M')}"

def MainAnswer(text):
    text = str(text).strip().lower()

    if text in ["programı kapat", "programı sonlandır", "kendini kapat", "kendini sonlandır"]:
        answer = [True, "Görüşmek üzere, kendine iyi bak.", 4]

    elif text in ["resim çiz", "resim oluştur", "resim yap", "çiz"]:
        answer = [True, "Ne çizmemi istersin ?", 2]

    elif text in ["günlerden ne", "saat kaç", "hangi aydayız", "hangi gündeyiz", "aylardan ne", "tarih", "hangi tarihteyiz"]:
        answer = [True, get_current_datetime(), 3]

    else:
        result = ChatAnswer(text)
        if result[0]:
            answer = [True, result[1], 0]
        else:
            answer = [False, "10 Saniye sonra tekrar konuşmayı dene", 1]

    return answer
    
    