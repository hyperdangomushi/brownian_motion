"""メニュー、設定バー、軌跡、振動グラフの描画。"""
# UIの描写を担当するモジュール

from pathlib import Path

import cv2
from matplotlib import pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont

MENU_WIDTH = 30
ROW_HEIGHT = 30
ACTIONS = ('menu', 'exit', 'reset', 'camera', 'trajectory', 'vibration')


def menu_action(x, y, menu_open):
    # 左端の30画素をメニューに使い、縦30画素ごとに操作を割り当てる。
    if not (0 <= x < MENU_WIDTH and y >= 0):
        return None
    row = y // ROW_HEIGHT
    if not menu_open:
        return 'menu' if row == 0 else None
    return ACTIONS[row] if row < len(ACTIONS) else None


class Controls:
    def __init__(self):
        # H・S・Vは色の許容幅、RECTは探索範囲の直径を調整する。
        self.background = np.zeros((250, 512, 3), dtype=np.uint8)
        cv2.namedWindow('bar')
        for name, value, maximum in (
            ('H', 30, 360), ('S', 30, 360), ('V', 30, 360), ('RECT', 20, 200)
        ):
            cv2.createTrackbar(name, 'bar', value, maximum, lambda value: None)

    def read(self):
        # 探索では中心からの距離を使うため、直径を半径に変換する。
        tolerance = [cv2.getTrackbarPos(name, 'bar') for name in ('H', 'S', 'V')]
        radius = cv2.getTrackbarPos('RECT', 'bar') // 2
        return tolerance, radius

    def show(self):
        cv2.imshow('bar', self.background)


def draw_path(img, points, color):
    # 軌跡を線分ごとにPythonで描く代わりに、折れ線としてまとめて描く。
    if len(points) > 1:
        vertices = np.asarray(points, dtype=np.int32).reshape(-1, 1, 2)
        cv2.polylines(img, [vertices], False, color, 1)


def draw_vibration(img, points, scale=1):
    # 振動の原点を(80, 50)に置き、表示倍率を掛けて描画する。
    cv2.line(img, (80, 0), (80, 100), (0, 0, 0), 1)
    cv2.line(img, (30, 50), (130, 50), (0, 0, 0), 1)
    translated = [(80 + int(x * scale), 50 + int(y * scale)) for x, y in points]
    draw_path(img, translated, (255, 0, 0))


class Display:
    def __init__(self):
        # フォントは一度だけ読み込む。日本語フォントがなければ英語表記にする。
        font_path = Path(__file__).resolve().parent.parent / 'fonts' / 'meiryo.ttc'
        self.font = (ImageFont.truetype(str(font_path), 10)
                     if font_path.exists() else ImageFont.load_default())
        self.labels = ('^', 'X', 'R', '切替', '軌跡', '振動')
        if not font_path.exists():
            self.labels = ('^', 'X', 'R', 'CAM', 'PATH', 'VIB')
        self.figure, self.axes = plt.subplots()
        self.x_line, = self.axes.plot([], [], color='blue')
        self.y_line, = self.axes.plot([], [], color='red')
        self.axes.set_ylim(-250, 250)
        plt.show(block=False)

    def plot(self, analysis):
        # 直近の取得コマ数分だけ表示し、既存の線のデータを更新する。
        if analysis.samples > analysis.window:
            samples = np.asarray(list(analysis.history)[-analysis.window:])
            self.x_line.set_data(samples[:, 0], samples[:, 1])
            self.y_line.set_data(samples[:, 0], samples[:, 2])
            self.axes.set_xlim(max(1, analysis.samples - analysis.window), analysis.samples)
        self.figure.canvas.draw_idle()
        self.figure.canvas.flush_events()

    def draw_menu(self, img, menu_open, trajectory, vibration, reset_flash=False):
        # 有効な表示とリセット直後のボタンを緑で示す。
        if menu_open:
            cv2.rectangle(img, (0, 0), (30, 180), (255, 255, 255), -1)
            for row, active in ((2, reset_flash), (4, trajectory), (5, vibration)):
                if active:
                    cv2.rectangle(img, (0, row * 30), (30, (row + 1) * 30), (0, 255, 0), -1)
        # OpenCVのBGRとPillowのRGBを変換して、色を保ったまま文字を描く。
        image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        painter = ImageDraw.Draw(image)
        if menu_open:
            for row, label in enumerate(self.labels):
                painter.text((5, row * 30 + 10), label, font=self.font, fill=(0, 0, 0))
        else:
            painter.text((10, 10), 'v', font=self.font, fill=(0, 0, 0))
        return cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)

    def close(self):
        plt.close(self.figure)
