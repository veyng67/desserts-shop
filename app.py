import os
import re
from flask import Flask, render_template, request, session, redirect, url_for
import requests

app = Flask(__name__)
app.secret_key = "super_secret_mama_shop_key"

TOKEN = os.environ.get("TELEGRAM_TOKEN", "9029977584:AAG6lHLOVQENnneIzTq8akmZkhcuN1KHjXw")
CHAT_ID = "1605532858"

CAKES = [
    {"id": "milk_slice",      "name": "Молочный ломтик",     "desc": "Нежный молочный бисквит со сливочным кремом",   "price": 2400, "weight": "1.2 кг", "filling": "Сгущенка, сливочный крем"},
    {"id": "three_choc",      "name": "Три шоколада",        "desc": "Тёмный, молочный и белый шоколад в одном торте", "price": 3200, "weight": "1.5 кг", "filling": "Шоколадный ганаш, какао-бисквит"},
    {"id": "cheesecake_stick","name": "Чизкейк на палочке",  "desc": "Порционный чизкейк на палочке, удобно есть",     "price": 350,  "weight": "100 г",  "filling": "Сливочный сыр, песочная крошка"},
    {"id": "mousse_bears",    "name": "Муссовые мишки",      "desc": "Лёгкие муссовые фигурки, нежные и воздушные",    "price": 450,  "weight": "150 г",  "filling": "Фруктовый мусс, бельгийский шоколад"},
    {"id": "carrot_citrus",   "name": "Морковно-цитрусовый", "desc": "Морковный бисквит с яркой цитрусовой ноткой",    "price": 2600, "weight": "1.3 кг", "filling": "Апельсиновый курд, крем-чиз"},
    {"id": "bento",           "name": "Бенто-торт",          "desc": "Мини-торт на двоих с вашей надписью",            "price": 1800, "weight": "500 г",  "filling": "Ванильный бисквит, крем с ягодами"},
    {"id": "eclairs",         "name": "Эклеры ассорти",      "desc": "Набор из 6 эклеров: ваниль, шоколад, фисташка",  "price": 1200, "weight": "300 г",  "filling": "Заварной крем, шоколад, фисташка"},
]

def find_cake(cake_id):
    return next((c for c in CAKES if c["id"] == cake_id), None)

def get_cart():
    return session.get("cart", {})

def save_cart(cart):
    session["cart"] = cart

def cart_details():
    cart = get_cart()
    items = []
    total = 0
    for cake_id, qty in cart.items():
        cake = find_cake(cake_id)
        if cake and qty > 0:
            subtotal = cake["price"] * qty
            total += subtotal
            items.append({"cake": cake, "qty": qty, "subtotal": subtotal})
    return items, total

def send_order_notification(name, phone, items, total):
    lines = [
        "Новый заказ!",
        "",
        f"Клиент: {name}",
        f"Телефон: {phone}",
        "",
        "Состав заказа:",
    ]
    for it in items:
        lines.append(f"— {it['cake']['name']} × {it['qty']} = {it['subtotal']} руб.")
    lines.append("")
    lines.append(f"Итого: {total} руб.")

    message = "\n".join(lines)
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    try:
        response = requests.get(url, params={"chat_id": CHAT_ID, "text": message}, timeout=10)
        response.raise_for_status()
        print("Уведомление успешно отправлено!")
    except Exception as e:
        print(f"Ошибка отправки: {e}")

@app.route("/")
def index():
    cart = get_cart()
    cart_count = sum(cart.values())
    return render_template("index.html", cakes=CAKES, cart_count=cart_count)

@app.route("/cake/<cake_id>")
def cake_page(cake_id):
    cake = find_cake(cake_id)
    if not cake:
        return redirect(url_for("index"))
    cart = get_cart()
    cart_count = sum(cart.values())
    return render_template("cake.html", cake=cake, cart_count=cart_count)

@app.route("/add/<cake_id>", methods=["POST"])
def add_to_cart(cake_id):
    cake = find_cake(cake_id)
    if not cake:
        return redirect(url_for("index"))
    cart = get_cart()
    cart[cake_id] = cart.get(cake_id, 0) + 1
    save_cart(cart)
    return redirect(request.referrer or url_for("index"))

@app.route("/cart")
def cart_page():
    items, total = cart_details()
    return render_template("cart.html", items=items, total=total)

@app.route("/cart/inc/<cake_id>", methods=["POST"])
def cart_inc(cake_id):
    cart = get_cart()
    if cake_id in cart:
        cart[cake_id] += 1
        save_cart(cart)
    return redirect(url_for("cart_page"))

@app.route("/cart/dec/<cake_id>", methods=["POST"])
def cart_dec(cake_id):
    cart = get_cart()
    if cake_id in cart:
        cart[cake_id] -= 1
        if cart[cake_id] <= 0:
            del cart[cake_id]
        save_cart(cart)
    return redirect(url_for("cart_page"))

@app.route("/cart/remove/<cake_id>", methods=["POST"])
def cart_remove(cake_id):
    cart = get_cart()
    cart.pop(cake_id, None)
    save_cart(cart)
    return redirect(url_for("cart_page"))

@app.route("/checkout", methods=["POST"])
def checkout():
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    items, total = cart_details()

    if not items:
        return redirect(url_for("cart_page"))
    if not name or not phone:
        return render_template("cart.html", items=items, total=total, error="Укажите имя и телефон")

    if not re.match(r'^[\d\s\+\-\(\)]+$', phone):
        return render_template("cart.html", items=items, total=total, error="Телефон должен содержать только цифры")

    try:
        send_order_notification(name, phone, items, total)
        session["cart"] = {}
        return render_template("cart.html", items=[], total=0, success=True)
    except Exception as e:
        return render_template("cart.html", items=items, total=total, error=str(e))

if __name__ == "__main__":
    app.run(debug=True)