# conda activate webservicep2plending webservicep2plending
# uvicorn main:app --reload


from typing import Union  # Mengimpor Union dari modul typing untuk memberikan petunjuk tipe data
from fastapi import FastAPI, Response, Request, HTTPException  # Mengimpor kelas yang diperlukan dari modul FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Mengimpor CORSMiddleware dari modul middleware FastAPI
import sqlite3  # Mengimpor modul sqlite3 untuk bekerja dengan database SQLite

app = FastAPI()  # Membuat instance FastAPI yang akan menjadi aplikasi utama

app.add_middleware(  # Menambahkan middleware CORS ke aplikasi
    CORSMiddleware,  # Menggunakan CORSMiddleware
    allow_origins=["*"],  # Mengizinkan permintaan dari semua sumber
    allow_credentials=True,  # Mengizinkan pengiriman kredensial dalam permintaan lintas sumber
    allow_methods=["*"],  # Mengizinkan metode permintaan apa pun (GET, POST, dll.)
    allow_headers=["*"],  # Mengizinkan header apa pun dalam permintaan
)



@app.get("/")  # Mendefinisikan endpoint untuk permintaan GET ke root path ("/")
def read_root():  # Fungsi yang akan dipanggil saat endpoint diakses
    return {"Hello": "World"}  # Mengembalikan respons berupa dictionary {"Hello": "World"}

@app.get("/mahasiswa/{nim}")  # Mendefinisikan endpoint untuk permintaan GET dengan path parameter "nim"
def ambil_mhs(nim: str):  # Fungsi yang akan dipanggil saat endpoint diakses dengan path parameter "nim"
    return {"nama": "Budi Martami"}  # Mengembalikan respons berupa dictionary {"nama": "Budi Martami"}

@app.get("/mahasiswa2/")  # Mendefinisikan endpoint untuk permintaan GET tanpa path parameter
def ambil_mhs2(nim: str):  # Fungsi yang akan dipanggil saat endpoint diakses
    return {"nama": "Budi Martami 2"}  # Mengembalikan respons berupa dictionary {"nama": "Budi Martami 2"}

@app.get("/daftar_mhs/")  # Mendefinisikan endpoint untuk permintaan GET tanpa path parameter
def daftar_mhs(id_prov: str, angkatan: str):  # Fungsi yang akan dipanggil saat endpoint diakses
    return {  # Mengembalikan respons berupa dictionary
        "query": " idprov: {}; angkatan: {}".format(id_prov, angkatan),  # Mengembalikan informasi query
        "data": [{"nim": "1234"}, {"nim": "1235"}]  # Mengembalikan data daftar mahasiswa
    }

# panggil sekali saja
@app.get("/init/")  # Mendefinisikan endpoint untuk permintaan GET dengan path "/init/"
def init_db():  # Fungsi yang akan dipanggil saat endpoint diakses
    try:
        DB_NAME = "upi.db"  # Nama database
        con = sqlite3.connect(DB_NAME)  # Membuka koneksi ke database SQLite
        cur = con.cursor()  # Membuat objek cursor untuk menjalankan perintah SQL

        # Membuat perintah SQL untuk membuat tabel 'mahasiswa'
        create_table = """CREATE TABLE mahasiswa(
            ID          INTEGER PRIMARY KEY AUTOINCREMENT,
            nim         TEXT            NOT NULL,
            nama        TEXT            NOT NULL,
            id_prov     TEXT            NOT NULL,
            angkatan    TEXT            NOT NULL,
            tinggi_badan INTEGER
        )"""

        cur.execute(create_table)  # Menjalankan perintah SQL untuk membuat tabel
        con.commit()  # Melakukan commit perubahan ke database

    except Exception as e:
        return {"status": "terjadi error"}  # Mengembalikan pesan error jika terjadi kesalahan

    finally:
        con.close()  # Menutup koneksi ke database setelah selesai

    return {"status": "ok, db dan tabel berhasil dicreate"}  # Mengembalikan pesan sukses jika berhasil


from pydantic import BaseModel  # Mengimpor BaseModel dari modul pydantic untuk membuat model Pydantic

from typing import Optional  # Mengimpor Optional dari modul typing untuk mendefinisikan atribut opsional

class Mhs(BaseModel):  # Mendefinisikan kelas Mhs yang merupakan turunan dari BaseModel
   nim: str  # Atribut untuk nomor induk mahasiswa bertipe string
   nama: str  # Atribut untuk nama mahasiswa bertipe string
   id_prov: str  # Atribut untuk identitas provinsi mahasiswa bertipe string
   angkatan: str  # Atribut untuk tahun masuk mahasiswa bertipe string
   tinggi_badan: Optional[int] | None = None  # Atribut untuk tinggi badan mahasiswa bertipe integer, boleh null (opsional)


#status code 201 standard return creation
#return objek yang baru dicreate (response_model tipenya Mhs)
@app.post("/tambah_mhs/", response_model=Mhs, status_code=201)  # Mendefinisikan endpoint untuk permintaan POST dengan path "/tambah_mhs/", menggunakan model respons Mhs, dan kode status 201 (Created)
def tambah_mhs(m: Mhs, response: Response, request: Request):  # Fungsi yang akan dipanggil saat endpoint diakses dengan metode POST
    try:
        DB_NAME = "upi.db"  # Nama database
        con = sqlite3.connect(DB_NAME)  # Membuka koneksi ke database SQLite
        cur = con.cursor()  # Membuat objek cursor untuk menjalankan perintah SQL

        # Menjalankan perintah SQL untuk memasukkan data mahasiswa ke dalam tabel
        cur.execute("""INSERT INTO mahasiswa (nim, nama, id_prov, angkatan, tinggi_badan) 
                       VALUES ("{}", "{}", "{}", "{}", {})""".format(m.nim, m.nama, m.id_prov, m.angkatan, m.tinggi_badan))
        con.commit()  # Melakukan commit perubahan ke database

    except Exception as e:
        print("oioi error")  # Mencetak pesan error jika terjadi kesalahan
        return {"status": "terjadi error"}  # Mengembalikan pesan error jika terjadi kesalahan

    finally:
        con.close()  # Menutup koneksi ke database setelah selesai

    response.headers["Location"] = "/mahasiswa/{}".format(m.nim)  # Menetapkan header "Location" untuk mengarahkan ke URL mahasiswa yang baru ditambahkan
    print(m.nim)  # Mencetak nomor induk mahasiswa
    print(m.nama)  # Mencetak nama mahasiswa
    print(m.angkatan)  # Mencetak tahun angkatan mahasiswa

    return m  # Mengembalikan data mahasiswa yang baru ditambahkan sebagai respons




@app.get("/tampilkan_semua_mhs/")  # Mendefinisikan endpoint untuk permintaan GET dengan path "/tampilkan_semua_mhs/"
def tampil_semua_mhs():  # Fungsi yang akan dipanggil saat endpoint diakses
    try:
        DB_NAME = "upi.db"  # Nama database
        con = sqlite3.connect(DB_NAME)  # Membuka koneksi ke database SQLite
        cur = con.cursor()  # Membuat objek cursor untuk menjalankan perintah SQL
        recs = []  # List untuk menyimpan data mahasiswa

        # Melakukan iterasi melalui hasil kueri SQL dan menyimpan setiap baris ke dalam list recs
        for row in cur.execute("SELECT * FROM mahasiswa"):
            recs.append(row)

    except Exception as e:
        return {"status": "terjadi error"}  # Mengembalikan pesan error jika terjadi kesalahan

    finally:
        con.close()  # Menutup koneksi ke database setelah selesai

    return {"data": recs}  # Mengembalikan data mahasiswa sebagai respons

from fastapi.encoders import jsonable_encoder  # Mengimpor fungsi jsonable_encoder dari modul fastapi.encoders



@app.put("/update_mhs_put/{nim}", response_model=Mhs)  # Mendefinisikan endpoint untuk permintaan PUT dengan path "/update_mhs_put/{nim}", menggunakan model respons Mhs
def update_mhs_put(response: Response, nim: str, m: Mhs):  # Fungsi yang akan dipanggil saat endpoint diakses dengan metode PUT
    # Update keseluruhan data mahasiswa kecuali nim
    try:
        DB_NAME = "upi.db"  # Nama database
        con = sqlite3.connect(DB_NAME)  # Membuka koneksi ke database SQLite
        cur = con.cursor()  # Membuat objek cursor untuk menjalankan perintah SQL

        # Melakukan kueri SQL untuk mengambil data mahasiswa dengan nim yang sesuai
        cur.execute("SELECT * FROM mahasiswa WHERE nim = ?", (nim,))  # Tambahkan koma untuk menandakan tuple
        existing_item = cur.fetchone()  # Mengambil satu baris hasil kueri

    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e)))  # Mengembalikan respons HTTP 500 jika terjadi kesalahan

    if existing_item:  # Jika data ditemukan
        print(m.tinggi_badan)  # Mencetak tinggi badan mahasiswa yang baru
        # Melakukan update data mahasiswa kecuali nim
        cur.execute("UPDATE mahasiswa SET nama = ?, id_prov = ?, angkatan = ?, tinggi_badan = ? WHERE nim = ?", 
                    (m.nama, m.id_prov, m.angkatan, m.tinggi_badan, nim))
        con.commit()  # Melakukan commit perubahan ke database
        response.headers["location"] = "/mahasiswa/{}".format(m.nim)  # Menetapkan header "location" untuk mengarahkan ke URL mahasiswa yang diperbarui

    else:  # Jika data tidak ditemukan
        print("item not found")  # Mencetak pesan bahwa data tidak ditemukan
        raise HTTPException(status_code=404, detail="Item Not Found")  # Mengembalikan respons HTTP 404 "Not Found"

    con.close()  # Menutup koneksi ke database
    return m  # Mengembalikan data mahasiswa yang diperbarui sebagai respons



# khusus untuk patch, jadi boleh tidak ada
# menggunakan "kosong" dan -9999 supaya bisa membedakan apakah tdk diupdate ("kosong") atau mau
# diupdate dengan dengan None atau 0
class MhsPatch(BaseModel):  # Mendefinisikan kelas MhsPatch yang merupakan turunan dari BaseModel
   nama: str | None = "kosong"  # Atribut untuk nama mahasiswa bertipe string atau None, default "kosong"
   id_prov: str | None = "kosong"  # Atribut untuk identitas provinsi mahasiswa bertipe string atau None, default "kosong"
   angkatan: str | None = "kosong"  # Atribut untuk tahun masuk mahasiswa bertipe string atau None, default "kosong"
   tinggi_badan: Optional[int] | None = -9999  # Atribut untuk tinggi badan mahasiswa bertipe integer, boleh null (opsional), default -9999


@app.patch("/update_mhs_patch/{nim}", response_model=MhsPatch)  # Mendefinisikan endpoint untuk permintaan PATCH dengan path "/update_mhs_patch/{nim}", menggunakan model respons MhsPatch
def update_mhs_patch(response: Response, nim: str, m: MhsPatch):  # Fungsi yang akan dipanggil saat endpoint diakses dengan metode PATCH
    try:
        print(str(m))  # Mencetak data yang diterima dari request
        DB_NAME = "upi.db"  # Nama database
        con = sqlite3.connect(DB_NAME)  # Membuka koneksi ke database SQLite
        cur = con.cursor()  # Membuat objek cursor untuk menjalankan perintah SQL

        # Melakukan kueri SQL untuk mengambil data mahasiswa dengan nim yang sesuai
        cur.execute("SELECT * FROM mahasiswa WHERE nim = ?", (nim,))  # Tambahkan koma untuk menandakan tuple
        existing_item = cur.fetchone()  # Mengambil satu baris hasil kueri

    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e)))  # Mengembalikan respons HTTP 500 jika terjadi kesalahan saat mengakses database

    if existing_item:  # Jika data ditemukan, lakukan pembaruan
        sqlstr = "UPDATE mahasiswa SET "  # Query SQL untuk pembaruan data mahasiswa
        # Loop melalui atribut mhs yang diterima dari request dan membangun query SQL untuk pembaruan
        if m.nama != "kosong":  # Cek apakah nama mahasiswa ingin diubah
            if m.nama is not None:  # Cek apakah nilai nama bukan None
                sqlstr += "nama = '{}', ".format(m.nama)  # Tambahkan nama ke dalam query SQL
            else:  # Jika nama None, set nilai kolom nama menjadi NULL
                sqlstr += "nama = null, "
        
        if m.angkatan != "kosong":  # Cek apakah angkatan mahasiswa ingin diubah
            if m.angkatan is not None:  # Cek apakah nilai angkatan bukan None
                sqlstr += "angkatan = '{}', ".format(m.angkatan)  # Tambahkan angkatan ke dalam query SQL
            else:  # Jika angkatan None, set nilai kolom angkatan menjadi NULL
                sqlstr += "angkatan = null, "
        
        if m.id_prov != "kosong":  # Cek apakah id provinsi mahasiswa ingin diubah
            if m.id_prov is not None:  # Cek apakah nilai id provinsi bukan None
                sqlstr += "id_prov = '{}', ".format(m.id_prov)  # Tambahkan id provinsi ke dalam query SQL
            else:  # Jika id provinsi None, set nilai kolom id provinsi menjadi NULL
                sqlstr += "id_prov = null, "
        
        if m.tinggi_badan != -9999:  # Cek apakah tinggi badan mahasiswa ingin diubah
            if m.tinggi_badan is not None:  # Cek apakah nilai tinggi badan bukan None
                sqlstr += "tinggi_badan = {}, ".format(m.tinggi_badan)  # Tambahkan tinggi badan ke dalam query SQL
            else:  # Jika tinggi badan None, set nilai kolom tinggi badan menjadi NULL
                sqlstr += "tinggi_badan = null, "

        sqlstr = sqlstr[:-2] + " WHERE nim = '{}'".format(nim)  # Hapus dua karakter terakhir (", ") dari query SQL dan tambahkan WHERE clause untuk mengupdate berdasarkan NIM
        print(sqlstr)  # Mencetak query SQL yang akan dieksekusi

        try:
            cur.execute(sqlstr)  # Eksekusi query SQL untuk melakukan pembaruan data
            con.commit()  # Melakukan commit perubahan ke dalam database
            response.headers["location"] = "/mahasixswa/{}".format(nim)  # Menetapkan header "location" untuk mengarahkan ke URL mahasiswa yang diperbarui
        except Exception as e:
            raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e)))  # Mengembalikan respons HTTP 500 jika terjadi kesalahan saat eksekusi query SQL

    else:  # Jika data tidak ditemukan
        raise HTTPException(status_code=404, detail="Item Not Found")  # Mengembalikan respons HTTP 404 "Not Found"

    con.close()  # Menutup koneksi ke database
    return m  # Mengembalikan data mahasiswa yang diperbarui sebagai respons

  
    
@app.delete("/delete_mhs/{nim}")  # Mendefinisikan endpoint untuk permintaan DELETE dengan path "/delete_mhs/{nim}"
def delete_mhs(nim: str):  # Fungsi yang akan dipanggil saat endpoint diakses
    try:
        DB_NAME = "upi.db"  # Nama database
        con = sqlite3.connect(DB_NAME)  # Membuka koneksi ke database SQLite
        cur = con.cursor()  # Membuat objek cursor untuk menjalankan perintah SQL
        sqlstr = "DELETE FROM mahasiswa WHERE nim='{}'".format(nim)  # Query SQL untuk menghapus data mahasiswa berdasarkan NIM
        print(sqlstr)  # Mencetak query SQL untuk keperluan debug
        cur.execute(sqlstr)  # Menjalankan query SQL untuk menghapus data mahasiswa
        con.commit()  # Melakukan commit perubahan ke dalam database

    except Exception as e:
        return {"status": "terjadi error"}  # Mengembalikan pesan error jika terjadi kesalahan

    finally:
        con.close()  # Menutup koneksi ke database setelah selesai

    return {"status": "ok"}  # Mengembalikan pesan sukses setelah data berhasil dihapus
