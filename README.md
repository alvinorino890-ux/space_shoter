# space_shoter
🎮 PENJELASAN GAME (DESKRIPSI UMUM)

Game ini adalah game Space Invader berbasis Python menggunakan Pygame, di mana pemain mengendalikan sebuah pesawat untuk mengalahkan musuh yang datang dari atas layar. Pemain harus menembak semua musuh sambil menghindari serangan dan menjaga jumlah nyawa agar tidak habis.

Game ini memiliki sistem level yang akan meningkat seiring pemain berhasil mengalahkan semua musuh. Semakin tinggi level, tingkat kesulitan juga meningkat, seperti jumlah musuh bertambah, kecepatan meningkat, dan frekuensi tembakan musuh lebih sering.

Selain itu, game ini dilengkapi dengan fitur skor, nyawa, efek visual seperti ledakan, serta penyimpanan high score.

🔄 FLOW GAME (ALUR PERMAINAN)
1. ▶️ Game Dimulai

Saat game dijalankan:

Pygame diinisialisasi
Layar dibuat
Player, musuh, dan background dibuat

Kode:

pygame.init()
screen = pygame.display.set_mode(...)
2. 🌌 Inisialisasi Objek

Game membuat:

Player (pesawat)
Musuh (enemy)
Background (bintang, asteroid, planet)

Kode:

player = Player()
enemies = spawn_enemies(level)
3. 🎬 Tampilan Level Awal

Sebelum mulai:

Muncul tulisan “LEVEL 1”
Memberi waktu pemain bersiap

Kode:

show_level_banner(...)
4. 🎮 Game Loop (Perulangan Utama)

Game berjalan terus dalam loop:

while running:

Di dalam loop ini semua proses terjadi:

5. 🎹 Input Player

Game membaca input:

← → untuk bergerak
SPACE untuk menembak

Kode:

keys = pygame.key.get_pressed()
player.move(keys)
6. 🚀 Pergerakan Objek

Semua objek bergerak:

Player bergerak
Peluru naik/turun
Musuh bergerak kiri-kanan
Background bergerak
7. 🔫 Sistem Menembak
Player menembak ke atas
Musuh menembak ke bawah secara random

Kode:

if random.random() < cfg["enemy_shoot"]:
8. 💥 Collision (Tabrakan)

Game mengecek tabrakan:

Peluru player vs musuh
Peluru musuh vs player

Jika kena:

Musuh hilang
Player kehilangan nyawa
Muncul efek ledakan

Kode:

colliderect()
9. ❤️ Sistem Nyawa
Player punya 3 nyawa
Jika kena peluru → nyawa berkurang
Ada invincible sementara
10. 📈 Sistem Skor
Setiap musuh mati → skor bertambah
Bonus saat naik level
11. ⬆️ Naik Level

Jika semua musuh mati:

Level bertambah
Musuh baru muncul
Kesulitan meningkat

Kode:

if len(enemies) == 0:
12. 💀 Game Over / Menang

Game berakhir jika:

Nyawa habis → kalah
(Secara logika bisa menang terus, tapi tetap masuk end state)
13. 🏆 Penyimpanan Skor

Saat game selesai:

Skor disimpan ke file JSON
Ditampilkan leaderboard
14. 🔁 Restart / Keluar
Tekan R → ulang game
Tekan Q → keluar
