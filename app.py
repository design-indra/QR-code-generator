from flask import Flask, render_template, request, send_file, redirect
import qrcode
import qrcode.image.svg
import os
import io
import base64

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=template_dir)

def generate_qr(text, color="#000000", bg_color="#ffffff", size=10):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=size,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color=color, back_color=bg_color)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return img_base64

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    text = ""
    color = "#000000"
    bg_color = "#ffffff"
    qr_type = "url"

    if request.method == "POST":
        qr_type = request.form.get("type", "url")
        color = request.form.get("color", "#000000")
        bg_color = request.form.get("bg_color", "#ffffff")

        # Build text based on type
        if qr_type == "url":
            text = request.form.get("url", "").strip()
        elif qr_type == "whatsapp":
            phone = request.form.get("phone", "").strip().replace("+", "").replace(" ", "")
            msg = request.form.get("message", "").strip()
            text = f"https://wa.me/{phone}?text={msg}"
        elif qr_type == "wifi":
            ssid = request.form.get("ssid", "").strip()
            password = request.form.get("password", "").strip()
            encryption = request.form.get("encryption", "WPA")
            text = f"WIFI:T:{encryption};S:{ssid};P:{password};;"
        elif qr_type == "text":
            text = request.form.get("text_content", "").strip()
        elif qr_type == "email":
            email = request.form.get("email", "").strip()
            subject = request.form.get("subject", "").strip()
            text = f"mailto:{email}?subject={subject}"
        elif qr_type == "phone":
            phone = request.form.get("phone_number", "").strip()
            text = f"tel:{phone}"

        if not text:
            error = "Mohon isi data yang diperlukan."
        else:
            try:
                img_base64 = generate_qr(text, color, bg_color)
                result = {"image": img_base64, "text": text}
            except Exception as e:
                print(f"QR error: {e}")
                error = "Gagal membuat QR Code. Coba lagi."

    return render_template("index.html", result=result, error=error,
                           qr_type=qr_type, color=color, bg_color=bg_color)

@app.route("/download")
def download():
    text = request.args.get("text", "")
    color = request.args.get("color", "#000000")
    bg_color = request.args.get("bg", "#ffffff")
    if not text:
        return "Invalid", 400
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=15,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color=color, back_color=bg_color)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return send_file(buffer, mimetype="image/png",
                         as_attachment=True, download_name="QRSave.png")
    except Exception as e:
        print(f"Download error: {e}")
        return redirect("/")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

if __name__ == "__main__":
    app.run(debug=True)
