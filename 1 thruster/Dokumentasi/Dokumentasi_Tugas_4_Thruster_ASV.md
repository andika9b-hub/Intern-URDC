# DOKUMENTASI TUGAS INTERN
# SIMULASI PENGENDALIAN 4 THRUSTER ASV

## 1. Penjelasan Class, Object, Attribute, dan Method

Program Simulasi Pengendalian 4 Thruster ASV dibuat menggunakan bahasa pemrograman Python dengan menerapkan konsep Object-Oriented Programming (OOP) atau pemrograman berorientasi objek. Konsep ini digunakan untuk mengelompokkan data dan fungsi ke dalam class sehingga program menjadi lebih terstruktur dan mudah dikembangkan.

### 1.1 Class

Class merupakan cetakan atau rancangan yang digunakan untuk membuat objek. Dalam program ini terdapat dua class utama, yaitu:

1. **Thruster**: digunakan untuk merepresentasikan setiap thruster yang terdapat pada ASV.
2. **ASVController**: digunakan untuk mengatur dan mengendalikan keempat thruster berdasarkan perintah gerakan.

### 1.2 Object

Object merupakan hasil pembuatan dari sebuah class. Pada program ini, class `Thruster` digunakan untuk membuat empat objek thruster, yaitu:

1. **FL (Front Left)**: thruster bagian depan kiri.
2. **FR (Front Right)**: thruster bagian depan kanan.
3. **RL (Rear Left)**: thruster bagian belakang kiri.
4. **RR (Rear Right)**: thruster bagian belakang kanan.

Keempat objek tersebut dikendalikan melalui class `ASVController` untuk menghasilkan gerakan sesuai perintah pengguna.

### 1.3 Attribute

Attribute merupakan variabel yang menyimpan informasi atau karakteristik suatu objek. Pada class `Thruster`, terdapat beberapa attribute, yaitu:

1. `name`: menyimpan nama atau identitas thruster.
2. `output`: menyimpan nilai keluaran atau daya dorong thruster.

Attribute tersebut digunakan untuk mengetahui identitas dan kondisi keluaran masing-masing thruster.

### 1.4 Method

Method merupakan fungsi yang berada di dalam sebuah class dan digunakan untuk menjalankan tindakan tertentu. Beberapa method yang digunakan dalam program ini adalah:

1. `set_output()`: mengatur nilai output thruster dengan batas minimum -100 dan maksimum 100.
2. `stop()`: menghentikan keluaran thruster dengan mengatur output menjadi 0.
3. `forward()`: mengatur keempat thruster agar ASV bergerak maju.
4. `backward()`: mengatur keempat thruster agar ASV bergerak mundur.
5. `turn_left()`: mengatur distribusi output thruster untuk menghasilkan gerakan belok kiri.
6. `turn_right()`: mengatur distribusi output thruster untuk menghasilkan gerakan belok kanan.
7. `emergency_stop()`: menghentikan seluruh thruster secara langsung.
8. `display_status()`: menampilkan kondisi dan nilai output setiap thruster pada terminal.

Dengan penerapan konsep OOP tersebut, pengendalian setiap thruster dapat dilakukan secara terstruktur melalui objek dan method yang telah dibuat.

---

## 2. Penjelasan Distribusi Output pada Setiap Gerakan

Pengendalian gerakan ASV dalam program ini menggunakan metode **Differential Thrust**. Metode ini mengatur arah dan besar keluaran thruster untuk menghasilkan gerakan maju, mundur, serta berbelok.

Keempat thruster memiliki posisi yang berbeda, yaitu Front Left (FL), Front Right (FR), Rear Left (RL), dan Rear Right (RR). Setiap thruster memiliki peran dalam menghasilkan gaya dorong untuk menggerakkan ASV.

### 2.1 Tabel Distribusi Output Thruster

| Gerakan | FL | FR | RL | RR |
|:---|---:|---:|---:|---:|
| Forward | +S | +S | +S | +S |
| Backward | -S | -S | -S | -S |
| Turn Left | -T | +T | -T | +T |
| Turn Right | +T | -T | +T | -T |
| Stop | 0 | 0 | 0 | 0 |

**Keterangan:**

- FL = Front Left (depan kiri).
- FR = Front Right (depan kanan).
- RL = Rear Left (belakang kiri).
- RR = Rear Right (belakang kanan).
- S = nilai kecepatan atau output yang diberikan.
- T = nilai output yang digunakan untuk gerakan berbelok.
- (+) = output positif.
- (-) = output negatif.

### 2.2 Penjelasan Setiap Gerakan

**a. Forward (Maju)**

Pada gerakan maju, seluruh thruster diberikan output positif dengan nilai yang sama. Hal ini menyebabkan ASV bergerak ke arah depan karena keempat thruster menghasilkan gaya dorong ke arah yang sama.

**b. Backward (Mundur)**

Pada gerakan mundur, seluruh thruster diberikan output negatif dengan nilai yang sama sehingga ASV bergerak ke arah belakang.

**c. Turn Left (Belok Kiri)**

Pada gerakan belok kiri, thruster bagian kiri diberikan output negatif, sedangkan thruster bagian kanan diberikan output positif. Perbedaan arah dorong tersebut menghasilkan gerakan berbelok ke kiri.

**d. Turn Right (Belok Kanan)**

Pada gerakan belok kanan, thruster bagian kiri diberikan output positif, sedangkan thruster bagian kanan diberikan output negatif. Perbedaan arah dorong tersebut menghasilkan gerakan berbelok ke kanan.

**e. Stop (Berhenti)**

Pada kondisi berhenti, seluruh thruster diberikan output sebesar 0 sehingga tidak menghasilkan gaya dorong. Dengan demikian, ASV berada dalam kondisi berhenti.

**f. Emergency Stop (Berhenti Darurat)**

Emergency Stop merupakan perintah penghentian darurat yang mengatur seluruh output thruster menjadi 0 secara langsung. Fitur ini digunakan untuk menghentikan sistem penggerak ketika diperlukan.

---

## 3. Kesimpulan Hasil Pengujian

Berdasarkan proses pembuatan dan pengujian program Simulasi Pengendalian 4 Thruster ASV, dapat disimpulkan bahwa program berhasil dibuat menggunakan bahasa pemrograman Python dengan menerapkan konsep Object-Oriented Programming (OOP).

Program mampu mengendalikan empat thruster, yaitu FL, FR, RL, dan RR, melalui beberapa perintah gerakan yang meliputi Forward, Backward, Turn Left, Turn Right, Stop, dan Emergency Stop. Setiap perintah menghasilkan distribusi output sesuai dengan metode Differential Thrust yang diterapkan dalam program.

Selain itu, program telah dilengkapi dengan validasi input untuk menangani masukan berupa huruf atau nilai kecepatan di luar rentang yang ditentukan. Nilai output thruster juga dibatasi pada rentang -100 hingga +100 agar keluaran tetap sesuai dengan ketentuan program.

Berdasarkan sembilan skenario pengujian, program diuji untuk memastikan fungsi gerakan, penghentian thruster, penanganan input yang tidak valid, serta pengakhiran program berjalan sesuai dengan pilihan pengguna.

Dengan demikian, simulasi pengendalian empat thruster ASV telah berhasil dibuat dan dijalankan melalui terminal Python tanpa menggunakan perangkat keras atau menghubungkan sistem ke Pixhawk maupun perangkat fisik lainnya.