from flask import Flask, render_template, request, redirect, flash, session
import pymysql
from pymysql.cursors import DictCursor

app = Flask(__name__)
app.secret_key = "labasset123"

#database
def get_db():
    return pymysql.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="lab_asset",
        cursorclass=DictCursor
    )

#login
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            conn = get_db()
            cursor = conn.cursor()
            sql = "SELECT * FROM users WHERE username=%s AND password=%s"
            cursor.execute(sql, (username, password))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user:
                session["id"] = user["id"]
                session["username"] = user["username"]
                session["role"] = user["role"]
                
                if user["role"] == "admin":
                    return redirect("/admin/dashboard")
                elif user["role"] == "asisten":
                    return redirect("/asisten/dashboard")
            else:
                flash("Username atau Password salah!")
        except Exception as e: flash(f"Error: {e}")
    return render_template("login.html")

#admin kategori
@app.route("/admin/kategori")
def kategori():

    if "role" not in session or session["role"] != "admin":
        return redirect("/")

    conn = get_db()
    cursor = conn.cursor()
    sql = "SELECT * FROM kategori ORDER BY id_kategori DESC"
    cursor.execute(sql)
    kategori = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        "admin/kategori.html",
        active="kategori",
        kategori=kategori
    )

# tambah kategori admin
@app.route("/admin/kategori/tambah_kategori", methods=["GET", "POST"])
def tambah_kategori():
    if request.method == "POST":
        nama_kategori = request.form["nama_kategori"]
        deskripsi = request.form["deskripsi"]
        conn = get_db()
        cursor = conn.cursor()

        sql = """INSERT INTO kategori(nama_kategori, deskripsi) VALUES(%s, %s)"""
        cursor.execute(sql, (nama_kategori, deskripsi))
        conn.commit()
        cursor.close()
        conn.close()    
    return redirect("/admin/kategori")

# Edit kategori admin
@app.route("/admin/kategori/edit_kategori/<int:id>", methods=["POST"])
def edit_kategori(id):
    conn = get_db()
    cursor = conn.cursor()
    
    nama_kategori = request.form["nama_kategori"]
    deskripsi = request.form["deskripsi"]
    
    sql = """ UPDATE kategori SET nama_kategori=%s, deskripsi=%s WHERE id_kategori=%s """
    cursor.execute(sql, (nama_kategori, deskripsi, id))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect("/admin/kategori")

#hapus kategori admin
@app.route("/admin/kategori/hapus/<int:id_kategori>")
def hapus_kategori(id_kategori):
    conn = get_db()
    cursor = conn.cursor()
    sql = "DELETE FROM kategori WHERE id_kategori=%s"
    cursor.execute(sql, (id_kategori,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect("/admin/kategori")

#aset admin   
@app.route("/admin/aset")
def data_aset():
    if "role" not in session or session["role"] != "admin":
        return redirect("/")
        
    conn = get_db()
    cursor = conn.cursor()
    
    sql = """
        SELECT aset.id_aset AS id_aset, 
               aset.nama_aset, 
               aset.kondisi, 
               aset.lokasi, 
               aset.jumlah, 
               aset.tanggal_masuk, 
               kategori.nama_kategori
        FROM aset
        LEFT JOIN kategori ON aset.id_kategori = kategori.id_kategori
        ORDER BY aset.id_aset DESC
    """
    cursor.execute(sql)
    daftar_aset = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        "admin/aset.html", 
        active="aset", 
        aset=daftar_aset
    )

#laporan admin
@app.route("/admin/laporan")
def laporan():
    if "role" not in session or session["role"] != "admin":
        return redirect("/")
    conn = get_db()
    cursor = conn.cursor()
    
    sql_tabel = """
        SELECT aset.id_aset AS id_aset, 
               aset.nama_aset, 
               aset.kondisi, 
               aset.lokasi, 
               aset.jumlah, 
               aset.tanggal_masuk, 
               kategori.nama_kategori
        FROM aset
        LEFT JOIN kategori ON aset.id_kategori = kategori.id_kategori
        ORDER BY aset.id_aset ASC
    """
    cursor.execute(sql_tabel)
    daftar_aset = cursor.fetchall()
    sql_total = "SELECT COUNT(*) AS total_jenis, SUM(jumlah) AS total_unit FROM aset"
    cursor.execute(sql_total)
    ringkasan = cursor.fetchone()
    
    cursor.close()
    conn.close()
    total_jenis = ringkasan['total_jenis'] if ringkasan else 0
    total_unit = ringkasan['total_unit'] if ringkasan and ringkasan['total_unit'] else 0

    return render_template(
        "admin/laporan.html", 
        active="laporan", 
        aset=daftar_aset,
        total_jenis=total_jenis,
        total_unit=total_unit
    )

# aset asisten
@app.route("/asisten/aset")
def data_aset_asisten():
    if "role" not in session or session["role"] != "asisten":
        return redirect("/")
        
    conn = get_db()
    cursor = conn.cursor()
    sql = """
        SELECT aset.id_aset AS id_aset, 
               aset.nama_aset, 
               aset.kondisi, 
               aset.lokasi, 
               aset.jumlah, 
               aset.tanggal_masuk, 
               kategori.nama_kategori
        FROM aset
        LEFT JOIN kategori ON aset.id_kategori = kategori.id_kategori
        ORDER BY aset.id_aset DESC
    """
    cursor.execute(sql)
    daftar_aset = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        "asisten/aset.html", 
        active="aset", 
        aset=daftar_aset
    )

#laporan asisten
@app.route("/asisten/laporan")
def laporan_asisten():
    if "role" not in session or session["role"] != "asisten":
        return redirect("/")
        
    conn = get_db()
    cursor = conn.cursor()

    sql_tabel = """
        SELECT aset.id_aset AS id_aset, 
               aset.nama_aset, 
               aset.kondisi, 
               aset.lokasi, 
               aset.jumlah, 
               aset.tanggal_masuk, 
               kategori.nama_kategori
        FROM aset
        LEFT JOIN kategori ON aset.id_kategori = kategori.id_kategori
        ORDER BY aset.id_aset ASC
    """
    cursor.execute(sql_tabel)
    daftar_aset = cursor.fetchall()
    
    sql_total = "SELECT COUNT(*) AS total_jenis, SUM(jumlah) AS total_unit FROM aset"
    cursor.execute(sql_total)
    ringkasan = cursor.fetchone()
    cursor.close()
    conn.close()
    
    total_jenis = ringkasan['total_jenis'] if ringkasan else 0
    total_unit = ringkasan['total_unit'] if ringkasan and ringkasan['total_unit'] else 0

    return render_template(
        "asisten/laporan.html", 
        active="laporan", 
        aset=daftar_aset,
        total_jenis=total_jenis,
        total_unit=total_unit
    )

#dashboard admin
@app.route("/admin/dashboard")
def dashboard_admin():
    return render_template("admin/dashboard.html",active="dashboard", )


#dashboard asisten
@app.route("/asisten/dashboard")
def dashboard_asisten():
    return render_template("asisten/dashboard.html", active="dashboard")

#logout
@app.route("/logout")
def logout():
    session.clear()
    flash("Anda telah berhasil logout.")
    return redirect("/")    

if __name__ == "__main__":
    app.run(debug=True)