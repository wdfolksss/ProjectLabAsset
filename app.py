from flask import Flask, render_template, request, redirect, flash, session
from datetime import datetime
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

@app.template_filter("tgl_indo")
def tgl_indo(date):
    bulan = [
        "Januari",
        "Februari",
        "Maret",
        "April",
        "Mei",
        "Juni",
        "Juli",
        "Agustus",
        "September",
        "Oktober",
        "November",
        "Desember",
    ]
    return f"{date.day} {bulan[date.month - 1]} {date.year}"

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
    
    sql_aset = """
        SELECT aset.id_aset,
               aset.nama_aset,
               aset.kode,
               aset.id_kategori,
               aset.kondisi,
               aset.lokasi,
               aset.jumlah,
               aset.tanggal_masuk,
               kategori.nama_kategori
        FROM aset
        LEFT JOIN kategori ON aset.id_kategori = kategori.id_kategori
        ORDER BY aset.id_aset DESC
    """
    cursor.execute(sql_aset)
    daftar_aset = cursor.fetchall()

    sql_kategori = "SELECT * FROM kategori ORDER BY nama_kategori ASC"
    cursor.execute(sql_kategori)
    daftar_kategori = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin/aset.html", 
        active="aset", 
        aset=daftar_aset,
        kategori=daftar_kategori
    )

#aset asisten
@app.route("/asisten/aset")
def aset_asisten():
    if "role" not in session or session["role"] != "asisten":
        return redirect("/")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT aset.id_aset,
               aset.kode,
               aset.nama_aset,
               aset.id_kategori,
               aset.jumlah,
               aset.kondisi,
               aset.lokasi,
               aset.tanggal_masuk,
               kategori.nama_kategori
        FROM aset
        LEFT JOIN kategori ON aset.id_kategori = kategori.id_kategori
        ORDER BY aset.id_aset DESC
    """)
    aset = cursor.fetchall()

    cursor.execute("SELECT * FROM kategori ORDER BY nama_kategori ASC")
    kategori = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "asisten/aset.html",
        active="aset",
        aset=aset,
        kategori=kategori
    )

#tambah aset admin
@app.route('/admin/aset/tambah', methods=['POST'])
def tambah_aset():
    print(request.form)

    kode = request.form.get('kode')
    nama_aset = request.form.get('nama_aset')
    id_kategori = request.form.get('id_kategori')
    jumlah = request.form.get('jumlah')
    kondisi = request.form.get('kondisi')
    lokasi = request.form.get('lokasi')
    tanggal_masuk = request.form.get('tanggal_masuk')

    if not kode:
        return "Input kode tidak terkirim. Cek name='kode' di form HTML."

    conn = get_db()
    cursor = conn.cursor()

    sql = """
        INSERT INTO aset 
        (kode, nama_aset, id_kategori, jumlah, kondisi, lokasi, tanggal_masuk)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(sql, (
        kode, nama_aset, id_kategori, jumlah, kondisi, lokasi, tanggal_masuk
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/admin/aset")

#edit aset admin
@app.route('/admin/aset/edit/<int:id_aset>', methods=['POST'])
def edit_aset(id_aset):
    kode = request.form['kode']
    nama_aset = request.form['nama_aset']
    id_kategori = request.form['id_kategori']
    jumlah = request.form['jumlah']
    kondisi = request.form['kondisi']
    lokasi = request.form['lokasi']
    tanggal_masuk = request.form['tanggal_masuk']

    conn = get_db()
    cursor = conn.cursor()

    sql = """
        UPDATE aset
        SET kode = %s,
            nama_aset = %s,
            id_kategori = %s,
            jumlah = %s,
            kondisi = %s,
            lokasi = %s,
            tanggal_masuk = %s
        WHERE id_aset = %s
    """

    cursor.execute(sql, (
        kode,
        nama_aset,
        id_kategori,
        jumlah,
        kondisi,
        lokasi,
        tanggal_masuk,
        id_aset
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/admin/aset")

#edit aset asisten
@app.route('/asisten/aset/edit/<int:id_aset>', methods=['POST'])
def edit_aset_asisten(id_aset):
    if "role" not in session or session["role"] != "asisten":
        return redirect("/")

    kode = request.form['kode']
    nama_aset = request.form['nama_aset']
    id_kategori = request.form['id_kategori']
    jumlah = request.form['jumlah']
    kondisi = request.form['kondisi']
    lokasi = request.form['lokasi']
    tanggal_masuk = request.form['tanggal_masuk']

    conn = get_db()
    cursor = conn.cursor()

    sql = """
        UPDATE aset
        SET kode = %s,
            nama_aset = %s,
            id_kategori = %s,
            jumlah = %s,
            kondisi = %s,
            lokasi = %s,
            tanggal_masuk = %s
        WHERE id_aset = %s
    """

    cursor.execute(sql, (
        kode, nama_aset, id_kategori, jumlah, kondisi, lokasi, tanggal_masuk, id_aset
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/asisten/aset")

#hapus aset admin
@app.route("/admin/aset/hapus/<int:id_aset>")
def hapus_aset(id_aset):
    conn = get_db()
    cursor = conn.cursor()

    sql = "DELETE FROM aset WHERE id_aset=%s"
    cursor.execute(sql, (id_aset,))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/admin/aset")


#dashboard admin
@app.route("/admin/dashboard")
def dashboard_admin():
    if "role" not in session or session["role"] != "admin":
        return redirect("/")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS total FROM kategori")
    total_kategori = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM aset")
    total_jenis = cursor.fetchone()["total"]

    cursor.execute("SELECT COALESCE(SUM(jumlah), 0) AS total FROM aset")
    total_unit = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM aset WHERE kondisi='Baik'")
    total_baik = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM aset WHERE kondisi='Perbaikan'")
    total_perbaikan = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM aset WHERE kondisi='Rusak'")
    total_rusak = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT kategori.nama_kategori, COUNT(aset.id_aset) AS total
        FROM kategori
        LEFT JOIN aset ON aset.id_kategori = kategori.id_kategori
        GROUP BY kategori.id_kategori, kategori.nama_kategori
    """)
    grafik_kategori = cursor.fetchall()

    cursor.execute("""
        SELECT aset.kode, aset.nama_aset, aset.kondisi, aset.tanggal_masuk, kategori.nama_kategori
        FROM aset
        LEFT JOIN kategori ON aset.id_kategori = kategori.id_kategori
        ORDER BY aset.id_aset DESC
        LIMIT 5
    """)
    aset_terbaru = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin/dashboard.html",
        active="dashboard",
        total_kategori=total_kategori,
        total_jenis=total_jenis,
        total_unit=total_unit,
        total_baik=total_baik,
        total_perbaikan=total_perbaikan,
        total_rusak=total_rusak,
        grafik_kategori=grafik_kategori,
        aset_terbaru=aset_terbaru
    )


#dashboard asisten
@app.route("/asisten/dashboard")
def dashboard_asisten():
    if "role" not in session or session["role"] != "asisten":
        return redirect("/")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS total FROM kategori")
    total_kategori = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM aset")
    total_jenis = cursor.fetchone()["total"]

    cursor.execute("SELECT COALESCE(SUM(jumlah), 0) AS total FROM aset")
    total_unit = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM aset WHERE kondisi='Baik'")
    total_baik = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM aset WHERE kondisi='Perbaikan'")
    total_perbaikan = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM aset WHERE kondisi='Rusak'")
    total_rusak = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT kategori.nama_kategori, COUNT(aset.id_aset) AS total
        FROM kategori
        LEFT JOIN aset ON aset.id_kategori = kategori.id_kategori
        GROUP BY kategori.id_kategori, kategori.nama_kategori
    """)
    grafik_kategori = cursor.fetchall()

    cursor.execute("""
        SELECT aset.kode, aset.nama_aset, aset.kondisi, aset.tanggal_masuk, kategori.nama_kategori
        FROM aset
        LEFT JOIN kategori ON aset.id_kategori = kategori.id_kategori
        ORDER BY aset.id_aset DESC
        LIMIT 5
    """)
    aset_terbaru = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "asisten/dashboard.html",
        active="dashboard",
        total_kategori=total_kategori,
        total_jenis=total_jenis,
        total_unit=total_unit,
        total_baik=total_baik,
        total_perbaikan=total_perbaikan,
        total_rusak=total_rusak,
        grafik_kategori=grafik_kategori,
        aset_terbaru=aset_terbaru
    )

#laporan admin
@app.route('/admin/laporan')
def laporan_admin():
    if "role" not in session or session["role"] != "admin":
        return redirect("/")

    filter_kondisi = request.args.get("filter", "semua")

    conn = get_db()
    cursor = conn.cursor()

    sql_aset = """
        SELECT aset.id_aset,
               aset.nama_aset,
               aset.kode,
               aset.id_kategori,
               aset.kondisi,
               aset.lokasi,
               aset.jumlah,
               aset.tanggal_masuk,
               kategori.nama_kategori
        FROM aset
        LEFT JOIN kategori ON aset.id_kategori = kategori.id_kategori
    """

    params = ()

    if filter_kondisi == "baik":
        sql_aset += " WHERE aset.kondisi = %s"
        params = ("Baik",)

    elif filter_kondisi == "rusak_perbaikan":
        sql_aset += " WHERE aset.kondisi IN (%s, %s)"
        params = ("Rusak", "Perbaikan")

    sql_aset += " ORDER BY aset.id_aset DESC"

    cursor.execute(sql_aset, params)
    daftar_aset = cursor.fetchall()

    total_jenis = len(daftar_aset)
    total_unit = sum(int(a["jumlah"]) for a in daftar_aset)

    cursor.execute("SELECT * FROM kategori ORDER BY nama_kategori ASC")
    daftar_kategori = cursor.fetchall()

    cursor.close()
    conn.close()

    if filter_kondisi == "baik":
        judul_laporan = "Laporan Aset Kondisi Baik"
    elif filter_kondisi == "rusak_perbaikan":
        judul_laporan = "Laporan Aset Rusak & Perbaikan"
    else:
        judul_laporan = "Laporan Semua Aset"

    return render_template(
        "admin/laporan.html",
        active="laporan",
        aset=daftar_aset,
        total_jenis=total_jenis,
        total_unit=total_unit,
        kategori=daftar_kategori,
        sekarang=datetime.now(),
        filter=filter_kondisi,
        judul_laporan=judul_laporan
    )

#laporan asisten
@app.route('/asisten/laporan')
def laporan_asisten():
    
    conn = get_db()
    cursor = conn.cursor()
    
    sql_aset = """
        SELECT aset.id_aset,
               aset.nama_aset,
               aset.kode,
               aset.id_kategori,
               aset.kondisi,
               aset.lokasi,
               aset.jumlah,
               aset.tanggal_masuk,
               kategori.nama_kategori
        FROM aset
        LEFT JOIN kategori ON aset.id_kategori = kategori.id_kategori
        ORDER BY aset.id_aset DESC
    """
    cursor.execute(sql_aset)
    daftar_aset = cursor.fetchall()

    sql_kategori = "SELECT * FROM kategori ORDER BY nama_kategori ASC"
    cursor.execute(sql_kategori)
    daftar_kategori = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) AS total FROM aset")
    total_jenis = cursor.fetchone()["total"]

    cursor.execute("SELECT COALESCE(SUM(jumlah), 0) AS total FROM aset")
    total_unit = cursor.fetchone()["total"]

    cursor.close()
    conn.close()

    return render_template(
        "asisten/laporan.html", 
        active="laporan", 
        aset=daftar_aset,
        total_jenis=total_jenis,
        total_unit=total_unit,
        kategori=daftar_kategori,
        sekarang=datetime.now()
    )


#logout
@app.route("/logout")
def logout():
    session.clear()
    flash("Anda telah berhasil logout.")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)