from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import pyodbc

app = FastAPI(title="QuanLySinhVien", version="1.0")

templates = Jinja2Templates(directory="templates")

# ------------------------
# Kết nối SQL Server
# ------------------------
def get_connection():
    return pyodbc.connect(
        "Driver={SQL Server};"
        "Server=DESKTOP-H8MHKI6\\MSSQLSERVER001;"  # đổi tên server của bạn
        "Database=DichVuKetNoi;"
        "Trusted_Connection=yes;"
    )

# ------------------------
# Model
# ------------------------
class Student(BaseModel):
    MaSV: str
    HoTen: str
    Lop: str

# ------------------------
# Trang nhập sinh viên
# ------------------------
@app.get("/", response_class=HTMLResponse)
def form_view(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

# ------------------------
# Xử lý thêm sinh viên
# ------------------------
@app.post("/submit")
def submit_form(
    ma_sv: str = Form(...),
    ho_ten: str = Form(...),
    lop: str = Form(...)
):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Students (MaSV, HoTen, Lop) VALUES (?, ?, ?)",
            (ma_sv, ho_ten, lop)
        )
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
    
    return RedirectResponse(url="/sinhvien", status_code=303)

# ------------------------
# Trang danh sách sinh viên (có tìm kiếm)
# ------------------------
@app.get("/sinhvien", response_class=HTMLResponse)
def show_students(request: Request, keyword: str = None):
    conn = get_connection()
    cursor = conn.cursor()

    if keyword:  # Nếu có từ khóa tìm kiếm
        cursor.execute("""
            SELECT MaSV, HoTen, Lop
            FROM Students
            WHERE MaSV LIKE ? OR HoTen LIKE ?
        """, (f"%{keyword}%", f"%{keyword}%"))
    else:  # Nếu không có từ khóa, lấy toàn bộ
        cursor.execute("SELECT MaSV, HoTen, Lop FROM Students")

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    students = [{"MaSV": r[0], "HoTen": r[1], "Lop": r[2]} for r in rows]

    return templates.TemplateResponse(
        "sinhvien.html",
        {
            "request": request,
            "sv": students,
            "keyword": keyword
        }
    )

# ------------------------
# API: Lấy tất cả sinh viên
# ------------------------
@app.get("/api/students", tags=["Students"])
def get_students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MaSV, HoTen, Lop FROM Students")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"MaSV": r[0], "HoTen": r[1], "Lop": r[2]} for r in rows]

# ------------------------
# API: Lấy sinh viên theo mã
# ------------------------
@app.get("/api/students/{ma_sv}", tags=["Students"])
def get_student(ma_sv: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MaSV, HoTen, Lop FROM Students WHERE MaSV = ?", (ma_sv,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")
    return {"MaSV": row[0], "HoTen": row[1], "Lop": row[2]}
