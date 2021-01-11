# Tugas Akhir
Repositori ini berisi kode, eksperimen, dan hasil eksperimen dari tugas akhir yang berjudul "Model *Interpretable Machine Learning* Berbasis MaxSAT Untuk Permasalahan Klasifikasi". Tugas akhir ini termotivasi oleh MLIC [1] dan IMLI [2].

- Implementasi IMLI dapat dilihat pada file `IMLI.py`.
- Dokumentasi tentang cara menggunakan `IMLI.py` dapat dilihat pada file `dokumentasi.ipynb`.
- Hasil mentah dari eksperimen yang dilakukan serta *script* yang digunakan dapat dilihat pada folder `experiment`.
- Hasil eksperimen yang sudah diolah menjadi `csv` serta beberapa *plot* terkait hasil tersebut dapat dilihat pada folder `olah-data`.
- *Datasets* yang digunakan dapat dilihat pada folder `datasets`. Hasil *preprocessing* setiap *dataset* agar dapat digunakan oleh `IMLI.py` dapat dilihat pada folder `experiment/<nama-dataset>/holdout`.

## Prasyarat
Sebelum dapat digunakan, perlu dilakukan peng-*install*-an MaxSAT *solver* yang kemudian didaftarkan pada PATH *variable*. Dua MaxSAT *solver* yang dapat digunakan adalah Open-WBO dan MaxHS. Dapat digunakan MaxSAT *solver* lainnya, tetapi penggunaannya tidak dibahas pada README ini.
### Open-WBO
1. *Clone* repositori Open-WBO berikut https://github.com/sat-group/open-wbo
2. Jalankan perintah
   ```
   make
   ```
   Untuk meng-*compile* Open-WBO tersebut menjadi sebuah *file* *binary* bernama `open-wbo`.
3. Masukkan folder yang mengandung `open-wbo` tersebut ke dalam PATH.
   
    Untuk **Ubuntu**, ini dapat dilakukan sebagai berikut.

      1. Buka file `~/.bashrc`
      2. Tambahkan baris berikut di akhir file tersebut.
         ```
         export PATH="$HOME/<path-to-open-wbo>:$PATH"
         ```
         Misalnya,
         ```
         export PATH="$HOME/Documents/Skripsi/open-wbo:$PATH"
         ```
      3. *Load* ulang file `~/.bashrc` pada terminal yang digunakan dengan perintah
         ```
         source ~/.bashrc
         ```
      4. Pastikan Open-WBO dapat langsung diakses pada terminal menggunakan perintah
         ```
         open-wbo
         ```
         Jika berhasil, seharusnya akan dikeluarkan *output* seperti berikut.
         ```
         c
         c Open-WBO:	 a Modular MaxSAT Solver -- based on Glucose4.1 (core version)
         c Version:	 September 2018 -- Release: 2.1
         ...
         ```
    Untuk **Windows**, ini dapat dilakukan sebagai berikut.

      1. Buka `System Properties` pada *tab* `Advanced`.
      2. Buka `Environment Variables` pada bagian kiri bawah.
      3. Tambahkan `User variables` dengan cara menekan `Edit` dan memasukkan *path* total lokasi dari Open-WBO. Misalnya,
            ```
            D:\Skripsi\open-wbo
            ```
      4. Simpan perubahan tersebut dengan menekan tombol `OK`.
      5. Buka *command prompt* baru. Pastikan* Open-WBO dapat langsung digunakan dari *command prompt* yang baru dibuka dengan perintah.
            ```
            open-wbo
            ```
         Jika berhasil, seharusnya akan dikeluarkan *output* seperti berikut.
         ```
         c
         c Open-WBO:	 a Modular MaxSAT Solver -- based on Glucose4.1 (core version)
         c Version:	 September 2018 -- Release: 2.1
         ...
         ```
4. Untuk menggunakan Open-WBO pada kode di repositori ini, cukup gunakan parameter `solver="open-wbo"`
### MaxHS
1. Ikuti tutorial peng-*install*-an MaxHS yang dapat diperoleh pada *link* https://github.com/fbacchus/MaxHS
2. Masukkan folder yang mengandung *binary* `maxhs` (**Ubuntu**) atau *executable* `maxhs.exe` (**Windows**) pada PATH *variable* sistem yang digunakan. *Binary* atau *executable* tersebut seharusnya terletak pada folder `<path-to-maxhs>/build/release/bin/` (**Ubuntu**) atau `<path-to-maxhs>\build\release\bin\` (**Windows**). Cara menambahkan *full path* dari folder ini ke PATH serupa dengan tutorial Open-WBO sebelumnya pada poin ke 3.
3. Untuk menggunakan MaxHS pada kode di respositori ini, gunakan parameter `solver="maxhs -printBstSoln"`.

## Penggunaan
Untuk menggunakan `IMLI.py`, dibutuhkan dua buah *library* Python, yaitu `Numpy` dan `Orange3`. *Install* *libraries* tersebut menggunakan perintah.
```
pip install -r requirements.txt
```
Setelah itu, `IMLI.py` siap digunakan. Contoh penggunaannya dapat dilihat pada file `dokumentasi.ipynb`.

## Referensi
[1] Malioutov, D., & Meel, K. S. (2018). MLIC: A MaxSAT-based framework for learning interpretable classification rules. *Proceedings of International Conference onConstraint Programming (CP)*.

[2] Ghosh, B., & Meel, K. S. (2019). IMLI: An incremental framework for MaxSAT-based learning of interpretable classification rules *Proceedings of the 2019 AAAI/ACMConference on AI, Ethics, and Society*, 203–210.