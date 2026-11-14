import requests

TOKEN = "9029977584:AAGl1HLOVQENnneIzTq8akmZkhcuN1KHjXw"
CHAT_ID = "1605532858"

def send_order_notification(name, item, price, phone):
    """Формирует сообщение о заказе и отправляет в Telegram."""
    message = (
        "🍰 Новый заказ!\n\n"
        f"👤 Клиент: {name}\n"
        f"📞 Телефон: {phone}\n"
        f"🎁 Товар: {item}\n"
        f"💰 Сумма: {price} руб."
    )
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        response = requests.get(url, params={"chat_id": CHAT_ID, "text": message})
        response.raise_for_status()
        print("Уведомление о заказе отправлено!")
    except Exception as e:
        print(f"Ошибка: {e}")

# --- Это имитация данных, которые позже будет присылать форма на сайте ---
if __name__ == "__main__":
    send_order_notification(
        name="Анна",
        item="Торт «Медовик»",
        price=2500,
        phone="+7 900 123-45-67"
    )