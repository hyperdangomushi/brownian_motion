"""マウス操作で変更する状態と、OpenCV用のコールバック。"""

from dataclasses import dataclass

import cv2

from lib import analyze, ui


@dataclass
class Interaction:
    # 処理はmain.pyで進め、ここには操作によって変わる状態だけを置く。
    running: bool = True
    tracking: bool = False
    menu_open: bool = False
    show_trajectory: bool = False
    show_vibration: bool = True
    reset_flash: int = 0
    hsv_image: object = None  # 着色前のHSV画像。クリックした画素の色を取得する。


def on_mouse(event, x, y, flags, params):
    # OpenCVに渡すために必要なコールバック。メニュー外では対象を選択する。
    if event != cv2.EVENT_LBUTTONDOWN:
        return
    state, camera, coordinate, hsv, analysis, trajectory, vibration_path = params
    action = ui.menu_action(x, y, state.menu_open)
    if action == 'menu':
        # 切り替えボタンに対応
        state.menu_open = not state.menu_open
    elif action == 'exit':
        # Xボタンに対応
        state.running = False
    elif action == 'trajectory':
        state.show_trajectory = not state.show_trajectory
    elif action == 'vibration':
        state.show_vibration = not state.show_vibration
    else:
        if action == 'camera':
            # 切り替えに失敗した場合は、現在のカメラで追跡を続ける。
            try:
                camera.switch()
            except RuntimeError as error:
                print(error)
                return
            state.tracking = False
            state.hsv_image = None
        elif action == 'reset':
            # Rボタンに対応。追跡位置と選択した色は維持する。
            print('リセットしました。')
        else:
            # クリック位置を探索の中心、その画素のHSVを色判定の基準にする。
            if state.hsv_image is None:
                return
            height, width = state.hsv_image.shape[:2]
            if not (0 <= x < width and 0 <= y < height):
                return
            coordinate.update(x, y)
            hsv.value = [int(value) for value in state.hsv_image[y, x]]
            state.tracking = True

        # リセット、対象の選び直し、カメラ切り替えでは履歴を初期化する。
        analysis.reset()
        trajectory.clear()
        vibration_path.clear()
        analyze.reset_frames()
        state.reset_flash = 5
