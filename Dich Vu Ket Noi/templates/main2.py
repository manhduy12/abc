from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route("/sinhvien", methods=["GET"])
def tra_cuu():
    ma_sv = request.args.get("MaSV")
    if not ma_sv:
        return render_template("form.html", error="Vui lòng nhập mã sinh viên.")

    try:
        response = requests.get(f"http://127.0.0.1:8000/api/students/{ma_sv}")
        data = response.json()
        if response.status_code == 200:
            return render_template("sinhvien.html", sv=[data])  # list để dễ lặp
        else:
            return render_template("form.html", error=data.get("detail", "Không tìm thấy."))
    except Exception:
        return render_template("form.html", error="Lỗi kết nối đến API.")

if __name__ == "__main__":
    app.run(port=5001)
