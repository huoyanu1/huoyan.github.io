from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于会话管理

# 数据库配置
db = mysql.connector.connect(
    host="localhost",
    user="root",  # 替换为你的数据库用户名
    password="Cxg14230",  # 替换为你的数据库密码
    database="student_management"
)
cursor = db.cursor(dictionary=True)

# 登录页面
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # 查询数据库，获取管理员信息
        cursor.execute("SELECT * FROM admins WHERE username=%s", (username,))
        admin = cursor.fetchone()

        if admin and password == admin["password"]:
            session["admin_id"] = admin["admin_id"]
            session["username"] = admin["username"]
            flash("Welcome back!", "success")
            return redirect("/")
        else:
            flash("Invalid username or password", "danger")

    return render_template("login.html")

# 登出功能
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect("/login")

# 首页 - 显示学生信息，带分页
@app.route("/", methods=["GET"])
def index():
    if "admin_id" not in session:
        return redirect("/login")

    # 获取分页参数，默认第1页
    page = request.args.get('page', 1, type=int)
    per_page = 5  # 每页显示的学生数量
    offset = (page - 1) * per_page

    # 查询学生信息并分页
    cursor.execute("SELECT * FROM students LIMIT %s OFFSET %s", (per_page, offset))
    students = cursor.fetchall()

    # 获取学生总数
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()["COUNT(*)"]

    # 计算总页数
    total_pages = (total_students + per_page - 1) // per_page

    return render_template("index.html", students=students, page=page, total_pages=total_pages)

# 添加学生页面
@app.route("/add", methods=["GET", "POST"])
def add_student():
    if "admin_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        name = request.form["name"]
        department = request.form["department"]
        major = request.form["major"]
        address = request.form["address"]
        phone_number = request.form["phone_number"]
        email = request.form["email"]

        cursor.execute(
            "INSERT INTO students (name, department, major, address, phone_number, email) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, department, major, address, phone_number, email)
        )
        db.commit()
        flash("Student added successfully!", "success")
        return redirect("/")

    return render_template("add_student.html")

# 编辑学生页面
@app.route("/edit/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    if "admin_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        name = request.form["name"]
        department = request.form["department"]
        major = request.form["major"]
        address = request.form["address"]
        phone_number = request.form["phone_number"]
        email = request.form["email"]

        cursor.execute(
            "UPDATE students SET name=%s, department=%s, major=%s, address=%s, phone_number=%s, email=%s WHERE student_id=%s",
            (name, department, major, address, phone_number, email, student_id)
        )
        db.commit()
        flash("Student updated successfully!", "success")
        return redirect("/")

    cursor.execute("SELECT * FROM students WHERE student_id=%s", (student_id,))
    student = cursor.fetchone()
    return render_template("edit_student.html", student=student)

# 删除学生
@app.route("/delete/<int:student_id>")
def delete_student(student_id):
    if "admin_id" not in session:
        return redirect("/login")

    cursor.execute("DELETE FROM students WHERE student_id=%s", (student_id,))
    db.commit()
    flash("Student deleted successfully!", "success")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
