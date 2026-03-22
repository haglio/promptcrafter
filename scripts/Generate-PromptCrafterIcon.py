from pathlib import Path

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QFont, QGuiApplication, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap


def main() -> int:
    app = QGuiApplication([])
    root = Path(__file__).resolve().parent.parent
    icon_path = root / "icon.ico"
    png_path = root / "icon.png"

    size = 256
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing, True)

    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0.0, QColor("#1f3c88"))
    gradient.setColorAt(0.55, QColor("#2563eb"))
    gradient.setColorAt(1.0, QColor("#0f766e"))

    card = QPainterPath()
    card.addRoundedRect(12, 12, size - 24, size - 24, 48, 48)
    painter.fillPath(card, gradient)

    accent_pen = QPen(QColor("#dbeafe"))
    accent_pen.setWidth(10)
    accent_pen.setCapStyle(Qt.RoundCap)
    painter.setPen(accent_pen)
    painter.drawLine(QPointF(56, 78), QPointF(200, 78))
    painter.drawLine(QPointF(56, 128), QPointF(168, 128))
    painter.drawLine(QPointF(56, 178), QPointF(184, 178))

    painter.setPen(QColor("#ffffff"))
    font = QFont("Segoe UI", 92, QFont.Bold)
    font.setLetterSpacing(QFont.PercentageSpacing, 94)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "PC")

    painter.end()

    pixmap.save(str(png_path))
    pixmap.save(str(icon_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
