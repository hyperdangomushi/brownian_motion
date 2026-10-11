import numpy as np


class Calcdot:
    def __init__(self):
        self.value = [0,0]
        self.old = [0,0]
        self.delta = [0,0]
        self.bibe = [0,0]
        self.range = [0,0]

    def update(self, x, y):
        self.old[0] = self.value[0]
        self.old[1] = self.value[1]
        self.value[0] = x
        self.value[1] = y
        self.delta[0] = self.value[0] - self.old[0]
        self.delta[1] = self.value[1] - self.old[1]

    def calc_coodinate(self, h, s, v, width, height, hsv, img=None):
        """HSV条件に合う画素の重心を更新し、(x, y, img)を返す。

        hsvにはCalcHSVを渡す。imgを渡した場合は検出画素を青くする。
        検出画素がない場合は座標を更新せず、Noneを返す。
        """
        # 現在の座標を中心に、画像内の探索範囲を求める。
        center_x, center_y = self.value
        radius_x, radius_y = self.range
        x_min = max(0, int(center_x - radius_x))
        x_max = min(width, int(center_x + radius_x))
        y_min = max(0, int(center_y - radius_y))
        y_max = min(height, int(center_y + radius_y))

        if x_min >= x_max or y_min >= y_max:
            return None

        # 探索範囲内の画素を、HSVの各しきい値でまとめて判定する。
        region = np.s_[y_min:y_max, x_min:x_max]
        hue = h[region]
        saturation = s[region]
        brightness = v[region]
        h_min, s_min, v_min = hsv.min
        h_max, s_max, v_max = hsv.max
        mask = (
            (hue > h_min) & (hue < h_max)
            & (saturation > s_min) & (saturation < s_max)
            & (brightness > v_min) & (brightness < v_max)
        )

        # 全検出画素の座標の平均が重心。画像全体の座標に戻す。
        rows, columns = np.nonzero(mask)
        if columns.size == 0:
            return None

        centroid_x = float(columns.mean() + x_min)
        centroid_y = float(rows.mean() + y_min)
        self.update(centroid_x, centroid_y)

        if img is not None: ##imgが渡された場合は検出画素を青くする
            img[region][mask] = [255, 0, 0]

        return centroid_x, centroid_y, img

class CalcHSV:
    def __init__(self):
        self.value = [0,0,0]
        self.min = [0,0,0]
        self.max = [0,0,0]
        self.range = [0,0,0]

