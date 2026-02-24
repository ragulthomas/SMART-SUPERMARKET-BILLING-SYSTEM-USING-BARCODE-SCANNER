from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session
from reportlab.pdfgen import canvas
from database import products
import razorpay
import os

app = Flask(__name__,
            template_folder="../frontend/templates",
            static_folder="../frontend/static")

# 🔐 Required for session login
app.secret_key = "super_secret_key_123"

cart = []

# 👤 Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"

# 💳 Razorpay client (TEST MODE)
client = razorpay.Client(auth=(
    "rzp_test_RzNTy4fyaqK3aM",
    "9QsJKPB1cdQG30mJYQ8j3H3p"
))

# =========================
# 🔐 ADMIN LOGIN SYSTEM
# =========================

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))
        else:
            return render_template("admin_login.html", error="Invalid credentials")

    return render_template("admin_login.html")


@app.route("/admin-logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))


@app.route("/admin")
def admin():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    return render_template("admin.html", products=products)


@app.route("/add-product", methods=["POST"])
def add_product():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    barcode = request.form.get("barcode")
    name = request.form.get("name")
    price = request.form.get("price")

    if barcode and name and price:
        products[barcode] = {
            "name": name,
            "price": int(price)
        }

    return redirect(url_for("admin"))


@app.route("/delete-product/<barcode>")
def delete_product(barcode):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    if barcode in products:
        del products[barcode]

    return redirect(url_for("admin"))

# =========================
# 🏠 USER SIDE
# =========================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/scan", methods=["POST"])
def scan():
    data = request.get_json()
    barcode = data.get("barcode")

    if barcode in products:
        cart.append({
            "barcode": barcode,
            "name": products[barcode]["name"],
            "price": products[barcode]["price"]
        })
        return jsonify({
            "status": "success",
            "product": products[barcode]
        })

    return jsonify({"status": "error"})


@app.route("/cart")
def view_cart():
    total = sum(i["price"] for i in cart)
    return render_template("cart.html", cart=cart, total=total)


@app.route("/remove-item/<int:index>")
def remove_item(index):
    if 0 <= index < len(cart):
        cart.pop(index)
    return redirect("/cart")


@app.route("/payment")
def payment():
    total = sum(i["price"] for i in cart)
    return render_template("payment.html", total=total)


@app.route("/create-order", methods=["POST"])
def create_order():
    try:
        total = sum(i["price"] for i in cart) * 100

        order = client.order.create({
            "amount": total,
            "currency": "INR",
            "payment_capture": 1
        })

        return jsonify(order)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/generate-bill")
def generate_bill():
    file_path = "bill.pdf"
    pdf = canvas.Canvas(file_path)

    pdf.drawString(100, 800, "Smart Supermarket Bill")
    y = 760
    total = 0

    for item in cart:
        pdf.drawString(100, y, f"{item['name']} - ₹{item['price']}")
        total += item["price"]
        y -= 20

    pdf.drawString(100, y - 20, f"Total: ₹{total}")
    pdf.save()

    cart.clear()
    return send_file(file_path, as_attachment=True)


@app.route("/success")
def success():
    return render_template("success.html")


# =========================
# 🚀 RUN SERVER
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
