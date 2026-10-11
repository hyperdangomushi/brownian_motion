import cv2
from PIL import ImageFont, ImageDraw, Image
from matplotlib import pyplot as plt
import time
import numpy as np
import math
capture = cv2.VideoCapture(0)
x = y = 0
hh = hs = hv = -1
Hmax = Smax = Vmax = 35
ranzatu = 0
capture.set(3,1920)
capture.set(4,1080)
capture.set(5,15)
xmin  = ymax = ymin = xmax = p = q = l = m = 0
rect = 30
delta_x = delta_y = x_old = y_old = 0
kiseki_xy = ranzatwuy = []
fig, ax = plt.subplots(1, 1)
n = shin_x = shin_y = sss = reset = kiseki_line = menu = ranzatsu = 0
katamuki = 1
sindo_x = sindo_y = 0
ax.set_ylim((-250, 250))
plt.pause(0.01)
kisekisw = 0
r_switch = 5
ranzatwu = []
cam = 0
hmin_old =hmax_old= smin_old =smax_old=vmin_old =vmax_old=0
def nothing(x):
    pass
graph = np.zeros((250,512,3), np.uint8)
cv2.namedWindow('bar')
sindo_bairitu = 1#振動の表示の拡大率
cam_daisu = 2#カメラの台数
cam_daisu = cam_daisu - 1
komasuu = 50#取得するコマ数
fpss = 8#フレームレートの設定
fps = 1/fpss
kinji_x = kinji_y =  [0]
x_katamuki = y_katamuki = seppenx = seppeny = x__kkatamuki = y__kkatamuki =0
x__katamuki = y__katamuki = sindd = sind = komaochi = 0
ruikei = 0
cv2.createTrackbar('H','bar',30,360,nothing)
cv2.createTrackbar('S','bar',30,360,nothing)
cv2.createTrackbar('V','bar',30,360,nothing)
cv2.createTrackbar('RECT','bar',20,200,nothing)
def onMouse(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        global Vmax,Vmin,rect,Hmax,Hmin,kisekisw,Smax,r_switch,Smin,kinji_i
        global xmin,ax,capture,ymin,seppenx,seppeny,delta_x,delta_y
        global ymax,n,katamuki,ranzatwu,ranzatwuy
        global xmax,menu,x_katamuki,y_katamuki,kinji_x,kinji_y
        global sss,reset,switch,kiseki_line,ranzatsu,ranzatu,number_vmin
        if menu == 1:
            if x < 30 and y < 30:
                menu = 0
            elif x < 30 and y > 30 and y < 60:
                reset = 300
            elif x < 30 and y > 60 and y < 90:
                x_katamuki = 0
                y_katamuki = 0
                katamuki = 0
                kinji_x = kinji_y = [0]
                n = 0
                x_katamuki = y_katamuki = katamuki = 0
                kiseki_line = 0
                r_switch = 0
                ranzatu = 0
                ranzatwu = ranzatwuy = [0]
                komaochi = 0
                kakudo_d = 0
                print("リセットしました。")
            elif x < 30 and y > 90 and y < 120:
                global cam
                if cam < cam_daisu:
                    cam = cam + 1
                    capture = cv2.VideoCapture(cam)
                    capture.set(3,1944)
                    capture.set(4,2592)
                    capture.set(5,15)
                else:
                    cam = 0
                    capture = cv2.VideoCapture(0)
                    capture.set(3,1944)
                    capture.set(4,2592)
                    capture.set(5,15)
            elif x < 30 and y > 120 and y < 150:
                kisekisw = kisekisw + 1
                if kisekisw == 2:
                    kisekisw = 0
            elif x < 30 and y > 150 and y < 180:
                if ranzatsu == 0:
                    ranzatsu = 1
                else:
                    ranzatsu = 0
            else:
                hsv= cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                h, s, v = cv2.split(hsv)
                x = int(x)
                y = int(y)
                xmin = x - rect
                ymin = y - rect
                xmax = x + rect
                ymax = y + rect
                hh = int(h[y][x])
                hs = int(s[y][x])
                hv = int(v[y][x])
                Hmax = hh + number_hmax
                Hmin = hh - number_hmin
                Smax = hs + number_smax
                Smin = hs - number_smin
                Vmax = hv + number_vmax
                Vmin = hv - number_vmin
                sss = 1
        else:
            if x < 30 and y < 30:
                menu = 1
            else:
                hsv= cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                h, s, v = cv2.split(hsv)
                x = int(x)
                y = int(y)
                xmin = x - rect
                ymin = y - rect
                xmax = x + rect
                ymax = y + rect
                hh = int(h[y][x])
                hs = int(s[y][x])
                hv = int(v[y][x])
                Hmax = hh + number_hmax
                Hmin = hh - number_hmin
                Smax = hs + number_smax
                Smin = hs - number_smin
                Vmax = hv + number_vmax
                Vmin = hv - number_vmin
                sss = 1
kakudo_d = []
while True:
    start = time.time()
    cv2.imshow('bar',graph)
    number_hmax = number_hmin = int(cv2.getTrackbarPos('H','bar'))
    number_smax = number_smin = int(cv2.getTrackbarPos('S','bar'))
    number_vmax = number_vmin = int(cv2.getTrackbarPos('V','bar'))
    rect= int(cv2.getTrackbarPos('RECT','bar'))/2
    if hmin_old == number_hmin and hmax_old == number_hmax and smin_old == number_smin and vmin_old == number_vmin and smax_old == number_smax and vmax_old == number_vmax:
        o=0
    else:
        Hmax = hh + number_hmax
        Hmin = hh - number_hmin
        Smax = hs + number_smax
        Smin = hs - number_smin
        Vmax = hv + number_vmax
        Vmin = hv - number_vmin
    hmin_old = number_hmin
    hmax_old = number_hmax
    smin_old = number_smin
    vmin_old = number_vmin
    smax_old = number_smax
    vmax_old = number_vmax
    rect = int(rect)
    switch = 0
    n += 1
    r_switch = r_switch + 1
    kiseki_xy.append([x,y])
    kiseki_line += 1
    if katamuki == komasuu:
        seppenx = delta_x
        seppeny = delta_y
        katamuki = 0
        x__kkatamuki = x_katamuki/komasuu
        y__kkatamuki = y_katamuki/komasuu
        x_katamuki = y_katamuki = 0
        shin_x = shin_y = 0
        sind = 0
    if sss == 1:
        katamuki = katamuki + 1
        plt.gca().clear()
        x_katamuki = x_katamuki + delx
        x__katamuki = x__kkatamuki * katamuki + seppenx
        sindo_x = delta_x - x__katamuki
        shindou_x = sindo_x*sindo_x
        y_katamuki = y_katamuki + dely
        y__katamuki = y__kkatamuki * katamuki + seppeny
        sindo_y = delta_y - y__katamuki
        shindou_y = sindo_y*sindo_y
        kinji_x = kinji_x + [sindo_x]
        kinji_y = kinji_y + [sindo_y]
        if n > komasuu:
            k_data = range(1,len(kinji_x)+1)
            ax.plot(k_data, kinji_x, color='blue')
            ax.plot(k_data, kinji_y, color='red')
        shindoo = shindou_x+shindou_y
        shindoo = math.sqrt(shindoo)
        sind = sind + shindoo
        sindd = sind/katamuki
        print('振動',str(sindd))
        plt.draw()
        if n < 51:
            ax.set_xlim([2,50])
        else:
            ax.set_ylim((10, -10))
            ax.set_xlim([n-50,n])
    k = cv2.waitKey(1)
    ret ,img = capture.read()
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    l = 0
    if menu == 1:
        cv2.rectangle(img, (0, 0), (30, 180), (255, 255, 255),thickness = -1)
    if xmax < 1890 and ymax < 1050:
        for i in range(xmin,xmax):
            for j in range(ymin,ymax):
                hh = int(h[j][i])
                hs = int(s[j][i])
                hv = int(v[j][i])
                if hh > Hmin and hh < Hmax and hs < Smax and hs > Smin and hv < Vmax and hv > Vmin:
                    img[j,i] = [255,0,0]
                    l = l + 1
                    p = p + i
                    q = q + j
    if l > 0:
        x = int(p / l)
        y = int(q / l)
        p = 0
        q = 0
        l = 0
        xmin = x - rect
        ymin = y - rect
        xmax = x + rect
        ymax = y + rect
    if r_switch < 5:
        cv2.rectangle(img, (0, 60), (30, 90), (255, 0, 0),thickness = -1)
    if kisekisw == 1:
        if menu == 1:
            cv2.rectangle(img, (0, 150), (30, 180), (0, 255, 0),thickness = -1)
        if kiseki_line > 3:
            for kiseki in range(kiseki_line):
                kisekii = kiseki + 1
                if kisekii < kiseki_line:
                    kinji_i = -1 - int(kiseki)
                    kinji_ii = -2 - int(kiseki)
                    kisx,kisy = kiseki_xy[kinji_i]
                    kisx_end,kisy_end = kiseki_xy[kinji_ii]
                    kisx = int(kisx)
                    kisy = int(kisy)
                    kisx_end = int(kisx_end)
                    kisy_end = int(kisy_end)
                    cv2.line(img, (kisx, kisy), (kisx_end, kisy_end), (0, 255, 0), thickness=1, lineType=cv2.LINE_8)
    if ranzatsu == 0:
        cv2.rectangle(img, (0, 150), (30, 180), (0, 255, 0),thickness = -1)
    if n > komasuu:
        xcos = int(sindo_x)
        ysin = int(sindo_y)
        if xcos == 0:
            print("角度はないよ")
        else:
            mtan = ysin/xcos
            kakudo = math.degrees(math.atan(mtan))
            print("角度",kakudo)
            kakudo_d += [int(kakudo)]
            np.var(kakudo_d)
        cv2.line(img, (80, 0), (80, 100), (0, 0, 0), thickness=1, lineType=cv2.LINE_8)
        cv2.line(img, (30, 50), (130, 50), (0, 0, 0), thickness=1, lineType=cv2.LINE_8)
        if ranzatsu == 0:
            ranzatwu = ranzatwu + [int(sindo_x)]
            ranzatwuy = ranzatwuy + [int(sindo_y)]
            ranzatu += 1
            abcd = ranzatu-1
            for i in range(abcd):
                kinji_i = -1 - int(i)
                fx = ranzatwu[kinji_i]
                fy = ranzatwuy[kinji_i]
                fx = 80+int(fx)*sindo_bairitu
                fy = 50+int(fy)*sindo_bairitu
                cv2.line(img, (80, 50), (fx, fy), (255, 0, 0), thickness=1, lineType=cv2.LINE_8)
    cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (0, 255, 0))
    font = ImageFont.truetype("./fonts/meiryo.ttc", 10)
    fill = -1
    img_pil = Image.fromarray(img)
    if menu == 1:
        ImageDraw.Draw(img_pil).text((5, 95), "切替", font = font , fill = (0, 0, 0, 0))
        ImageDraw.Draw(img_pil).text((10, 40), "X", font = font , fill = (0, 0, 0, 0))
        ImageDraw.Draw(img_pil).text((10, 70), "R", font = font , fill = (0, 0, 0, 0))
        ImageDraw.Draw(img_pil).text((10, 12), "^", font = font , fill = (0, 0, 0, 0))
        ImageDraw.Draw(img_pil).text((5, 125), "軌跡", font = font , fill = (0, 0, 0, 0))
        ImageDraw.Draw(img_pil).text((5, 155), "振動", font = font , fill = (0, 0, 0, 0))
    else:
        ImageDraw.Draw(img_pil).text((10, 10), "v", font = font , fill = (0, 0, 0, 0))
    img = np.array(img_pil)
    cv2.imshow("img",img)
    delta_y = 960 - y
    delta_x = 540 - x
    delx = delta_x - x_old
    dely = delta_y - y_old
    x_old = delta_x
    y_old = delta_y
    cv2.setMouseCallback('img', onMouse)
    end = time.time()
    times = end - start
    if times <= fps:
        slp = fps - times
        slp = slp * 1000
        slp = int(slp)
        slp = slp/1000
        time.sleep(slp)
    else:
        slp = times/fps
        slpp = int(slp)
        slp = slp - slpp
        slp = slp * 1000
        slp = int(slp)
        slp = slp/1000
        komaochi +=1
    ruikei +=1
    kakuritu = (komaochi/ruikei)*100
    kakuritu = int(kakuritu)
    kakuritu = "コマ落ち:" + str(kakuritu) + "%"
    print(kakuritu)
    print("フレームレート:",fpss)
    if reset == 300:
        break
cv2.destroyAllWindows()
