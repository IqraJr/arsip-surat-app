import os
import shutil
import pandas as pd
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QLineEdit, QHeaderView, QMessageBox, QAbstractItemView,
                             QFileDialog)
from PyQt6.QtCore import Qt
from .db_manager import connect_db
from .form_surat import FormTambahSurat 

class SuratMasuk(QWidget):
    def __init__(self):
        super().__init__()
        self.all_data = []      # Data asli dari DB
        self.filtered_data = [] # Data setelah difilter
        self.current_page = 1
        self.rows_per_page = 10
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(25, 25, 25, 25)
        self.main_layout.setSpacing(15)

        # --- HEADER ---
        header_layout = QHBoxLayout()
        title = QLabel("📥 Manajemen Surat Masuk")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2d3436;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        self.btn_tambah = QPushButton("+ Tambah Surat Masuk")
        self.btn_tambah.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tambah.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white; padding: 10px 20px; 
                font-weight: bold; border-radius: 8px; border: none;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        self.btn_tambah.clicked.connect(self.aksi_tambah)
        header_layout.addWidget(self.btn_tambah)
        self.main_layout.addLayout(header_layout)

        # --- SEARCH BAR ---
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Cari Nomor Surat atau Pengirim...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 12px; border: 1px solid #dcdde1; border-radius: 8px; 
                background: white; color: black; font-size: 13px;
            }
        """)
        self.search_input.textChanged.connect(self.filter_data)
        self.main_layout.addWidget(self.search_input)

        # --- TABLE ---
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        # Nama kolom disesuaikan untuk Surat Masuk (PENGIRIM)
        self.table.setHorizontalHeaderLabels(["NO", "NO. SURAT", "PERIHAL", "PENGIRIM", "TANGGAL", "AKSI"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.setStyleSheet("""
            QTableWidget { background-color: white; color: #2d3436; border: none; outline: none; }
            QHeaderView::section { 
                background-color: #7132CA; color: white; padding: 12px; 
                font-weight: bold; border: none; text-transform: uppercase;
            }
            QTableWidget::item:selected { background-color: #C47BE4; color: white; }
            QTableWidget::item { padding: 10px; border-bottom: 1px solid #f1f2f6; }
        """)
        self.table.setSortingEnabled(True)
        self.main_layout.addWidget(self.table)

        # --- PAGINATION ---
        pagination_layout = QHBoxLayout()
        self.btn_prev = QPushButton("◀")
        self.btn_next = QPushButton("▶")
        self.label_page = QLabel("Halaman 1 of 1")
        self.label_page.setStyleSheet("color: black; font-weight: bold;")
        
        style_nav = "QPushButton { color: black; background:#dfe4ea; border-radius:5px; padding:5px 15px; font-weight:bold; }"
        self.btn_prev.setStyleSheet(style_nav)
        self.btn_next.setStyleSheet(style_nav)
        
        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next.clicked.connect(self.next_page)
        
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.btn_prev)
        pagination_layout.addWidget(self.label_page)
        pagination_layout.addWidget(self.btn_next)
        pagination_layout.addStretch()
        self.main_layout.addLayout(pagination_layout)

        # --- BOTTOM BUTTONS ---
        bottom_layout = QHBoxLayout()
        
        self.btn_delete = QPushButton("🗑 Hapus Terpilih")
        self.btn_delete.setStyleSheet("background-color: #ff6b6b; color: white; padding: 10px 20px; font-weight: bold; border-radius: 8px; border: none;")
        self.btn_delete.clicked.connect(self.aksi_hapus)
        
        self.btn_excel = QPushButton("📊 Export Excel")
        self.btn_excel.setStyleSheet("background-color: #27ae60; color: white; padding: 10px 20px; font-weight: bold; border-radius: 8px; border: none;")
        self.btn_excel.clicked.connect(self.export_to_excel)
        
        bottom_layout.addWidget(self.btn_delete)
        bottom_layout.addWidget(self.btn_excel)
        bottom_layout.addStretch()
        self.main_layout.addLayout(bottom_layout)

        self.load_data()

    def display_data(self, data):
        self.filtered_data = data
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        
        start_idx = (self.current_page - 1) * self.rows_per_page
        page_data = data[start_idx : start_idx + self.rows_per_page]
        
        total_pages = max(1, (len(data) + self.rows_per_page - 1) // self.rows_per_page)
        self.label_page.setText(f"Halaman {self.current_page} dari {total_pages}")
        self.btn_prev.setEnabled(self.current_page > 1)
        self.btn_next.setEnabled(self.current_page < total_pages)

        for i, row in enumerate(page_data):
            self.table.insertRow(i)
            
            no_item = QTableWidgetItem()
            no_item.setData(Qt.ItemDataRole.DisplayRole, start_idx + i + 1)
            no_item.setData(Qt.ItemDataRole.UserRole, row[0])
            no_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 0, no_item)

            for j in range(1, 5):
                val = str(row[j])
                if j == 4: # Tanggal
                    try:
                        if hasattr(row[j], 'strftime'): val = row[j].strftime('%d/%m/%Y')
                    except: pass
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(i, j, item)
            
            # Kolom AKSI
            btn_container = QWidget()
            btn_container.setStyleSheet("background: transparent;")
            btn_l = QHBoxLayout(btn_container)
            btn_l.setContentsMargins(5, 2, 5, 2)
            btn_l.setSpacing(8)
            
            btn_view = QPushButton("Lihat")
            btn_view.setStyleSheet("background:#5c7cfa; color:white; border-radius:4px; padding:5px 2px; font-size:11px; min-width: 45px;font-weight:bold;")
            btn_view.clicked.connect(lambda checked, p=row[5]: self.buka_berkas(p))
            
            btn_edit = QPushButton("✏️")
            btn_edit.setStyleSheet("background:#f1c40f; color:white; border-radius:4px; padding:5px; min-width:30px;")
            btn_edit.clicked.connect(lambda checked, r=row: self.aksi_edit(r))
            
            btn_l.addWidget(btn_view)
            btn_l.addWidget(btn_edit)
            self.table.setCellWidget(i, 5, btn_container)
            self.table.setRowHeight(i, 50)

        self.table.setSortingEnabled(True)

    def load_data(self):
        try:
            db = connect_db()
            if db:
                cursor = db.cursor()
                cursor.execute("SELECT id, nomor_surat, judul_surat, asal_surat, tanggal, file_path FROM surat WHERE kategori='masuk' ORDER BY id DESC")
                self.all_data = cursor.fetchall()
                self.current_page = 1
                self.display_data(self.all_data)
                db.close()
        except Exception as e: print(f"Error Load: {e}")

    def filter_data(self):
        text = self.search_input.text().lower()
        self.filtered_data = [d for d in self.all_data if text in str(d[1]).lower() or text in str(d[2]).lower()]
        self.current_page = 1
        self.display_data(self.filtered_data)

    def prev_page(self):
        self.current_page -= 1
        self.display_data(self.filtered_data)

    def next_page(self):
        self.current_page += 1
        self.display_data(self.filtered_data)

    def export_to_excel(self):
        data_exp = self.filtered_data if self.filtered_data else self.all_data
        if not data_exp: return
        path, _ = QFileDialog.getSaveFileName(self, "Simpan Laporan", f"Laporan_Surat_Masuk_{datetime.now().strftime('%d%m%Y')}.xlsx", "Excel Files (*.xlsx)")
        if path:
            try:
                df = pd.DataFrame(data_exp, columns=["ID", "Nomor Surat", "Perihal", "Pengirim", "Tanggal", "Path File"])
                df.to_excel(path, index=False)
                self.notifikasi_custom("Sukses", "Laporan berhasil disimpan!", QMessageBox.Icon.Information)
            except Exception as e: self.notifikasi_custom("Error", str(e), QMessageBox.Icon.Critical)

    def aksi_tambah(self):
        # Pastikan kategori diatur ke "Masuk" agar label berubah jadi 'Pengirim'
        dialog = FormTambahSurat(self, kategori="Masuk")
        if dialog.exec():
            # AMBIL DATA MENGGUNAKAN ent_pihak
            nomor = dialog.ent_nomor.text().strip()
            perihal = dialog.ent_perihal.text().strip()
            pengirim = dialog.ent_pihak.text().strip() # Ini perubahan kuncinya
            tgl = dialog.ent_tanggal.date().toString("yyyy-MM-dd")
            path_asal = dialog.file_path

            if not nomor or not path_asal:
                self.notifikasi_custom("Peringatan", "Nomor dan Berkas wajib diisi!", QMessageBox.Icon.Warning)
                return

            try:
                up_dir = os.path.join("uploads", "surat_masuk")
                os.makedirs(up_dir, exist_ok=True)
                ext = os.path.splitext(path_asal)[1]
                path_dest = os.path.join(up_dir, f"IN_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}")
                shutil.copy(path_asal, path_dest)
                
                db = connect_db()
                cursor = db.cursor()
                # Simpan ke DB (kategori='masuk')
                cursor.execute("INSERT INTO surat (nomor_surat, judul_surat, asal_surat, kategori, tanggal, file_path) VALUES (%s,%s,%s,'masuk',%s,%s)",
                               (nomor, perihal, pengirim, tgl, path_dest))
                db.commit()
                db.close()
                self.load_data()
                self.notifikasi_custom("Berhasil", "Surat Masuk berhasil diarsipkan!", QMessageBox.Icon.Information)
            except Exception as e: self.notifikasi_custom("Error", str(e), QMessageBox.Icon.Critical)

    def aksi_hapus(self):
        row = self.table.currentRow()
        if row < 0: return
        db_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        msg = QMessageBox(self)
        msg.setWindowTitle("Hapus")
        msg.setText("Hapus data ini?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setStyleSheet("QMessageBox { background: white; } QLabel { color: black; }")
        if msg.exec() == QMessageBox.StandardButton.Yes:
            try:
                db = connect_db()
                cursor = db.cursor()
                cursor.execute("DELETE FROM surat WHERE id=%s", (db_id,))
                db.commit()
                db.close()
                self.load_data()
            except Exception as e: print(e)

    def aksi_edit(self, data):
        from PyQt6.QtCore import QDate
        dialog = FormTambahSurat(self, kategori="Masuk")
        dialog.setWindowTitle("Edit Surat Masuk")
        
        # Isi data lama ke form (Gunakan ent_pihak)
        dialog.ent_nomor.setText(str(data[1]))
        dialog.ent_perihal.setText(str(data[2]))
        dialog.ent_pihak.setText(str(data[3])) # Perubahan di sini
        
        tgl = data[4]
        if hasattr(tgl, 'year'): 
            dialog.ent_tanggal.setDate(QDate(tgl.year, tgl.month, tgl.day))
        else:
            dialog.ent_tanggal.setDate(QDate.fromString(str(tgl), "yyyy-MM-dd"))
            
        dialog.file_path = data[5]

        if dialog.exec():
            try:
                db = connect_db()
                cursor = db.cursor()
                # Update menggunakan ent_pihak
                cursor.execute("UPDATE surat SET nomor_surat=%s, judul_surat=%s, asal_surat=%s, tanggal=%s, file_path=%s WHERE id=%s",
                               (dialog.ent_nomor.text(), dialog.ent_perihal.text(), dialog.ent_pihak.text(), 
                                dialog.ent_tanggal.date().toString("yyyy-MM-dd"), dialog.file_path, data[0]))
                db.commit()
                db.close()
                self.load_data()
                self.notifikasi_custom("Sukses", "Data berhasil diperbarui!", QMessageBox.Icon.Information)
            except Exception as e: self.notifikasi_custom("Error", str(e), QMessageBox.Icon.Critical)

    def buka_berkas(self, path):
        if path and os.path.exists(path): os.startfile(os.path.abspath(path))
        else: self.notifikasi_custom("Error", "File tidak ada!", QMessageBox.Icon.Critical)

    def notifikasi_custom(self, judul, pesan, ikon):
        msg = QMessageBox(self)
        msg.setWindowTitle(judul)
        msg.setText(pesan)
        msg.setIcon(ikon)
        msg.setStyleSheet("QMessageBox { background-color: white; } QLabel { color: black; font-size: 13px; } QPushButton { color: black; min-width: 80px; }")
        msg.exec()