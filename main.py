"""ブラウン運動の追跡アプリ。画像をクリックして追跡対象を選択する。"""

from collections import deque
import time

import cv2

from lib import analyze, calc, camera, interaction, ui

# MacBook Air（Apple M4・10コアCPU・24GBメモリ）向けの初期設定。
# カメラへ要求する画像サイズ。実際の探索には取得した画像サイズを使う。
WIDTH = 1920
HEIGHT = 1080
CAMERA_FPS = 30  # カメラの取得フレームレート（対応する値はカメラ次第）
CAMERA_COUNT = 2  # カメラの台数（内蔵カメラと連係カメラのiPhoneを確認）
CAMERA_INDEX = 1  # 実機で映像を取得できた番号。番号0は黒画像を返すことを確認。
FRAMERATE = 15  # フレームレートの設定（解析ループの目標。実測値ではない）
ANALYSIS_WINDOW = round(FRAMERATE * 6.25)  # 取得するコマ数（従来の50コマ÷8FPS相当）
HISTORY_LIMIT = FRAMERATE * 250  # メモリの増加を抑えるための履歴の上限（約250秒分）
VIBRATION_SCALE = 1.0  # 振動の表示の拡大率


if __name__ == '__main__':
    # import時にはカメラやウィンドウを開かない。
    # 各モジュールの処理対象をここでまとめて用意する。
    device = camera.Camera(WIDTH, HEIGHT, CAMERA_FPS, CAMERA_COUNT)
    coordinate = calc.Calcdot()
    hsv = calc.CalcHSV()
    motion = analyze.MotionAnalysis(ANALYSIS_WINDOW, HISTORY_LIMIT)
    trajectory = deque(maxlen=HISTORY_LIMIT)
    vibration_path = deque(maxlen=HISTORY_LIMIT)
    state = interaction.Interaction()
    display = None

    # カメラとGUIは起動時に作成し、途中で例外が起きてもfinallyで解放する。
    try:
        device.open(CAMERA_INDEX)
        controls = ui.Controls()
        display = ui.Display()
        cv2.namedWindow('img')
        cv2.setMouseCallback(
            'img', interaction.on_mouse,
            (state, device, coordinate, hsv, motion, trajectory, vibration_path),
        )
        analyze.reset_frames()

        while state.running:
            # 1. カメラから画像を取得し、現在の探索範囲と色の許容幅を読む。
            begin_time = time.monotonic()
            frame = device.read()
            height, width = frame.shape[:2]
            tolerance, radius = controls.read()
            coordinate.range = [radius, radius]
            hsv.range = tolerance
            state.hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            if state.tracking:
                # 2. 対象の色はクリック時に保存し、しきい値だけを更新して重心を求める。
                hsv.min = [value - margin for value, margin in zip(hsv.value, tolerance)]
                hsv.max = [value + margin for value, margin in zip(hsv.value, tolerance)]
                h, s, v = cv2.split(state.hsv_image)
                centroid = coordinate.calc_coodinate(h, s, v, width, height, hsv, frame)

                if centroid is not None:
                    # 3. 重心が見つかったフレームだけを振動の解析と履歴に追加する。
                    x, y = centroid[:2]
                    trajectory.append((x, y))
                    # 元の解析と同じく、画像座標と逆向きの変位を解析する。
                    vibration = motion.update(-x, -y)
                    if motion.samples > ANALYSIS_WINDOW:
                        if state.show_vibration:
                            vibration_path.append(tuple(vibration))
                        if motion.angle is not None:
                            print('角度:', motion.angle)
                    print('振動:', motion.mean_amplitude)
                    display.plot(motion)

                # 4. 重心の小数は保持したまま、描画用の座標だけを整数に変換する。
                x, y = coordinate.value
                top_left = (max(0, int(x - radius)), max(0, int(y - radius)))
                bottom_right = (min(width - 1, int(x + radius)), min(height - 1, int(y + radius)))
                cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 1)

            # 軌跡、振動、メニューを描き、画像と設定バーを表示する。
            if state.show_trajectory:
                ui.draw_path(frame, trajectory, (0, 255, 0))
            if state.show_vibration and motion.samples > ANALYSIS_WINDOW:
                ui.draw_vibration(frame, vibration_path, VIBRATION_SCALE)
            frame = display.draw_menu(
                frame, state.menu_open, state.show_trajectory,
                state.show_vibration, state.reset_flash > 0,
            )
            state.reset_flash = max(0, state.reset_flash - 1)
            controls.show()
            cv2.imshow('img', frame)

            # 5. キー・マウス入力を処理し、終了操作があればループを抜ける。
            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord('q')) or not state.running:
                break
            if cv2.getWindowProperty('img', cv2.WND_PROP_VISIBLE) < 1:
                break

            # 6. loopが終了すべき時間まで待ち、コマ落ち率を表示する。
            analyze.wait_loop_end(FRAMERATE, begin_time)
            print('フレームレート:', FRAMERATE)
            print('コマ落ち率:', analyze.dropped_rate())

    except (RuntimeError, KeyboardInterrupt) as error:
        print(error)
    finally:
        # 終了時は、カメラとグラフとOpenCVのウィンドウを必ず解放する。
        device.close()
        if display is not None:
            display.close()
        cv2.destroyAllWindows()
