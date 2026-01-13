import os
from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QPushButton, 
                             QVBoxLayout, QLabel, QHBoxLayout, QFileDialog, QDateEdit)
from PyQt6.QtCore import Qt, QDate

class FormTambahSurat(QDialog):
    def __init__(self, parent=None, kategori="Keluar"):
        """
        kategori: "Masuk" atau "Keluar"
        Digunakan untuk menyesuaikan Label Pihak Luar (Pengirim/Tujuan)
        """
        super().__init__(parent)
        self.kategori = kategori
        self.setWindowTitle(f"Form Arsip Surat {self.kategori}")
        self.setFixedWidth(450)
        self.file_path = ""
        
        # --- STYLING ---
        self.setStyleSheet("""
            QDialog { background-color: #ffffff; }
            QLabel { color: #2c3e50; font-weight: bold; font-size: 12px; }
            QLineEdit, QDateEdit { 
                padding: 10px; 
                border: 1px solid #dcdde1; 
                border-radius: 6px; 
                color: #2f3640; 
                background: #f5f6fa;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
                background: #ffffff;
            }
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(25, 20, 25, 25)
        self.layout.setSpacing(10)
        
        # --- HEADER ---
        # Warna Hijau untuk Keluar, Biru untuk Masuk
        warna_header = "#27ae60" if self.kategori == "Keluar" else "#2980b9"
        header = QLabel(f"FORM INPUT SURAT {self.kategori.upper()}")
        header.setStyleSheet(f"font-size: 18px; color: {warna_header}; margin-bottom: 15px; font-weight: bold;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(header)

        # --- FORM INPUT ---
        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(15)
        
        self.ent_nomor = QLineEdit()
        self.ent_nomor.setPlaceholderText("Contoh: 001/SK/2026")
        
        self.ent_perihal = QLineEdit()
        self.ent_perihal.setPlaceholderText("Isi ringkasan perihal surat")
        
        # Penentuan Label Berdasarkan Kategori
        label_pihak = "Pengirim / Asal:" if self.kategori == "Masuk" else "Tujuan Surat:"
        placeholder_pihak = "Nama Instansi/Orang pengirim" if self.kategori == "Masuk" else "Nama Instansi/Orang tujuan"
        
        self.ent_pihak = QLineEdit()
        self.ent_pihak.setPlaceholderText(placeholder_pihak)
        
        # Input Tanggal
        self.ent_tanggal = QDateEdit()
        self.ent_tanggal.setCalendarPopup(True) 
        self.ent_tanggal.setDate(QDate.currentDate()) 
        self.ent_tanggal.setDisplayFormat("yyyy-MM-dd")
        
        
        # Styling Kalender (Perbaikan agar teks bulan terlihat jelas)
        self.ent_tanggal.calendarWidget().setStyleSheet("""
            /* Warna angka tanggal di kalender utama */
            QCalendarWidget QAbstractItemView:enabled {
                color: #2c3e50;
                selection-background-color: #3498db;
                selection-color: white;
            }

            /* PERBAIKAN: Warna teks pada dropdown menu (Januari, Februari, dst) */
            QCalendarWidget QMenu {
                background-color: white;
                color: black; /* Teks menu bulan menjadi hitam */
            }

            /* Bagian Header (Navigation Bar) */
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: white;
            }

            /* Warna teks untuk tombol bulan dan tahun di header */
            QCalendarWidget QToolButton {
                color: black;
                font-weight: bold;
                background-color: transparent;
            }
            
            /* Warna teks hari (Sun, Mon, dst) */
            QCalendarWidget QWidget {
                color: #2c3e50;
            }
        """)
        
        self.form_layout.addRow("No. Surat:", self.ent_nomor)
        self.form_layout.addRow("Perihal:", self.ent_perihal)
        self.form_layout.addRow(label_pihak, self.ent_pihak)
        self.form_layout.addRow("Tanggal Surat:", self.ent_tanggal) 
        
        self.layout.addLayout(self.form_layout)
        
        # --- LAMPIRAN ---
        self.layout.addSpacing(10)
        lbl_lampiran = QLabel("Lampiran Berkas (PDF/Gambar):")
        self.layout.addWidget(lbl_lampiran)
        
        file_layout = QHBoxLayout()
        self.btn_browse = QPushButton("📁 Pilih File")
        self.btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_browse.setStyleSheet("""
            QPushButton {
                background-color: #f1f2f6; color: #2f3640; padding: 8px 15px; 
                border: 1px solid #dcdde1; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #dfe4ea; }
        """)
        self.btn_browse.clicked.connect(self.pilih_berkas)
        
        self.lbl_file = QLabel("Belum ada berkas...")
        self.lbl_file.setStyleSheet("font-weight: normal; color: #7f8c8d; font-style: italic;")
        
        file_layout.addWidget(self.btn_browse)
        file_layout.addWidget(self.lbl_file, 1)
        self.layout.addLayout(file_layout)

        # --- TOMBOL AKSI ---
        self.layout.addSpacing(15)
        self.btn_simpan = QPushButton("💾 SIMPAN KE ARSIP")
        self.btn_simpan.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_simpan.setStyleSheet(f"""
            QPushButton {{
                background-color: {warna_header}; color: white; border-radius: 6px;
                padding: 15px; font-weight: bold; font-size: 13px; border: none;
            }}
            QPushButton:hover {{ background-color: #2d3436; }}
        """)
        self.btn_simpan.clicked.connect(self.accept) 
        self.layout.addWidget(self.btn_simpan)

    def pilih_berkas(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Pilih File Scan", "", "Images/PDF (*.jpg *.jpeg *.png *.pdf)"
        )
        if file:
            self.file_path = file
            self.lbl_file.setText(os.path.basename(file))
            self.lbl_file.setStyleSheet("color: #27ae60; font-weight: bold; font-style: normal;")