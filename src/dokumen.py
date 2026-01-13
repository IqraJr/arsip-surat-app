# src/dokumen.py
import os
import shutil
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFileDialog, QMessageBox, QFrame)
from PyQt6.QtCore import Qt
from .db_manager import connect_db

class KelolaDokumen(QWidget):
    def __init__(self):
        super().__init__()
        self.file_asal = ""
        self.setup_ui()

    def setup_ui(self):
        # Layout Utama
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        self.main_layout.setSpacing(20)

        # Header
        header = QLabel("Kelola Dokumen (Upload PDF/JPG)")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        self.main_layout.addWidget(header)

        # Container Form (Card Style)
        self.card_frame = QFrame()
        self.card_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #dcdde1;
            }
        """)
        card_layout = QVBoxLayout(self.card_frame)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(15)

        # Input Judul
        card_layout.addWidget(QLabel("Judul Dokumen:"))
        self.ent_judul = QLineEdit()
        self.ent_judul.setPlaceholderText("Masukkan judul dokumen...")
        self.ent_judul.setStyleSheet("padding: 10px; border: 1px solid #bdc3c7; border-radius: 5px;")
        card_layout.addWidget(self.ent_judul)

        # Pilih File
        card_layout.addWidget(QLabel("Pilih Berkas:"))
        file_layout = QHBoxLayout()
        self.btn_pilih = QPushButton("📁 Browse File")
        self.btn_pilih.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pilih.setStyleSheet("background-color: #ecf0f1; padding: 8px; border-radius: 5px;")
        self.btn_pilih.clicked.connect(self.pilih_file)
        file_layout.addWidget(self.btn_pilih)

        self.lbl_path = QLabel("Belum ada file dipilih")
        self.lbl_path.setStyleSheet("color: #7f8c8d; font-style: italic; border: none;")
        file_layout.addWidget(self.lbl_path)
        file_layout.addStretch()
        card_layout.addLayout(file_layout)

        # Tombol Simpan
        self.btn_simpan = QPushButton("🚀 Simpan & Upload")
        self.btn_simpan.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_simpan.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        self.btn_simpan.clicked.connect(self.simpan_dokumen)
        card_layout.addWidget(self.btn_simpan)

        self.main_layout.addWidget(self.card_frame)
        self.main_layout.addStretch() # Mendorong form ke atas

    def pilih_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Pilih Dokumen", 
            "", 
            "Image/PDF files (*.jpg *.jpeg *.png *.pdf)"
        )
        if file_path:
            self.file_asal = file_path
            self.lbl_path.setText(os.path.basename(file_path))

    def simpan_dokumen(self):
        judul = self.ent_judul.text()
        if not judul or not self.file_asal:
            QMessageBox.warning(self, "Peringatan", "Isi judul dan pilih file terlebih dahulu!")
            return

        try:
            # 1. Pastikan folder uploads ada
            upload_dir = "uploads"
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)

            # 2. Buat nama file unik
            ext = os.path.splitext(self.file_asal)[1]
            nama_file_baru = f"DOC_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
            path_tujuan = os.path.join(upload_dir, nama_file_baru)

            # 3. Salin file secara fisik
            shutil.copy(self.file_asal, path_tujuan)

            # 4. Simpan ke Database
            db = connect_db()
            if db:
                cursor = db.cursor()
                query = "INSERT INTO surat (judul_surat, kategori, tanggal, file_path) VALUES (%s, %s, %s, %s)"
                val = (judul, 'dokumen', datetime.now().date(), path_tujuan)
                
                cursor.execute(query, val)
                db.commit()
                db.close()
                
                QMessageBox.information(self, "Berhasil", f"Dokumen berhasil diupload sebagai: {nama_file_baru}")
                
                # Reset Form
                self.ent_judul.clear()
                self.lbl_path.setText("Belum ada file dipilih")
                self.file_asal = ""

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan: {str(e)}")