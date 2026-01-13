import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QPushButton, QGraphicsOpacityEffect, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QFont, QColor
from .db_manager import connect_db

# Library untuk diagram
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.fig = None
        self.cards = []
        self.setup_ui()
        # Jalankan animasi kartu setelah UI dimuat
        QTimer.singleShot(100, self.animate_cards)

    def get_stats(self):
        stats = {'masuk': 0, 'keluar': 0, 'dokumen': 0}
        try:
            db = connect_db()
            if db:
                cursor = db.cursor()
                query = "SELECT kategori, COUNT(*) FROM surat GROUP BY kategori"
                cursor.execute(query)
                results = cursor.fetchall()
                for kat, jml in results:
                    if kat in stats:
                        stats[kat] = jml
                db.close()
        except Exception as e:
            print(f"Error stats: {e}")
        return stats

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(25)

        # --- HEADER SECTION ---
        header_layout = QHBoxLayout()
        
        header_text_layout = QVBoxLayout()
        header = QLabel("📊 DASHBOARD ANALITIK")
        header.setStyleSheet("font-size: 26px; font-weight: bold; color: #1a1a2e;")
        subtitle = QLabel("Visualisasi data arsip surat secara real-time")
        subtitle.setStyleSheet("font-size: 13px; color: #6c757d;")
        header_text_layout.addWidget(header)
        header_text_layout.addWidget(subtitle)
        
        header_layout.addLayout(header_text_layout)
        header_layout.addStretch()
        
        # Tombol Refresh Modern
        self.refresh_btn = QPushButton("🔄 Refresh Data")
        self.refresh_btn.setFixedSize(140, 45)
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #4a6cf7;
                border: 2px solid #4a6cf7;
                border-radius: 10px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #4a6cf7;
                color: white;
            }
            QPushButton:pressed {
                background-color: #3752c1;
            }
        """)
        self.refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(self.refresh_btn)
        self.main_layout.addLayout(header_layout)

        # --- CARDS SECTION ---
        self.card_container = QHBoxLayout()
        self.card_container.setSpacing(20)
        self.main_layout.addLayout(self.card_container)
        self.load_cards()

        # --- CHART SECTION ---
        chart_wrapper = QFrame()
        chart_wrapper.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 20px;
                border: 1px solid #e0e0e0;
            }
        """)
        # Tambahkan Shadow pada Frame Chart
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 8)
        chart_wrapper.setGraphicsEffect(shadow)

        self.chart_layout = QVBoxLayout(chart_wrapper)
        self.chart_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.addWidget(chart_wrapper, stretch=1)

        self.update_chart()

    def load_cards(self):
        # Bersihkan kartu lama jika ada
        for card in self.cards:
            self.card_container.removeWidget(card)
            card.deleteLater()
        self.cards.clear()

        data = self.get_stats()
        card_configs = [
            ("Surat Masuk", data['masuk'], "#4e73df", "#224abe"),
            ("Surat Keluar", data['keluar'], "#f6c23e", "#dda20a"),
            ("Dokumen Umum", data['dokumen'], "#1cc88a", "#13855c")
        ]

        for title, val, c1, c2 in card_configs:
            card = self.create_card(title, val, c1, c2)
            self.cards.append(card)
            self.card_container.addWidget(card)

    def create_card(self, title, value, color_start, color_end):
        card = QFrame()
        card.setFixedSize(260, 140)
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                            stop:0 {color_start}, stop:1 {color_end});
                border-radius: 15px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: rgba(255, 255, 255, 0.8); font-size: 14px; font-weight: bold; background: transparent;")
        
        lbl_value = QLabel(str(value))
        lbl_value.setStyleSheet("color: white; font-size: 38px; font-weight: bold; background: transparent;")
        
        lbl_unit = QLabel("Total Arsip")
        lbl_unit.setStyleSheet("color: rgba(255, 255, 255, 0.6); font-size: 11px; background: transparent;")

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        layout.addStretch()
        layout.addWidget(lbl_unit)

        # Efek Opacity untuk Animasi
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0)
        card.setGraphicsEffect(opacity_effect)
        
        return card

    def animate_cards(self):
        for i, card in enumerate(self.cards):
            anim = QPropertyAnimation(card.graphicsEffect(), b"opacity")
            anim.setDuration(600)
            anim.setStartValue(0)
            anim.setEndValue(1)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            # Delay antar kartu agar muncul bergantian
            QTimer.singleShot(i * 150, anim.start)

    def update_chart(self):
        # Bersihkan layout chart
        while self.chart_layout.count():
            item = self.chart_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        data = self.get_stats()
        labels = ['Surat Masuk', 'Surat Keluar', 'Dokumen']
        sizes = [data['masuk'], data['keluar'], data['dokumen']]
        colors = ['#4e73df', '#f6c23e', '#1cc88a']

        if sum(sizes) == 0:
            msg = QLabel("📭 Belum ada data untuk dianalisis")
            msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            msg.setStyleSheet("color: #95a5a6; font-size: 16px;")
            self.chart_layout.addWidget(msg)
            return

        plt.rcParams['font.family'] = 'sans-serif'
        self.fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        self.fig.patch.set_facecolor('none') # Latar belakang transparan

        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, autopct='%1.1f%%', startangle=90, 
            colors=colors, wedgeprops={'width': 0.5, 'edgecolor': 'w', 'linewidth': 3},
            textprops={'color': "#2c3e50", 'weight': 'bold'}
        )
        
        ax.set_title("Distribusi Volume Arsip", pad=20, fontsize=14, weight='bold', color="#2c3e50")
        
        canvas = FigureCanvas(self.fig)
        self.chart_layout.addWidget(canvas)

    def refresh_data(self):
        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setText("⏳ Loading...")
        
        # Simulasi sedikit delay agar animasi terasa
        QTimer.singleShot(500, self._perform_refresh)

    def _perform_refresh(self):
        self.load_cards()
        self.update_chart()
        self.animate_cards()
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("🔄 Refresh Data")

    def __del__(self):
        if hasattr(self, 'fig') and self.fig:
            plt.close(self.fig)