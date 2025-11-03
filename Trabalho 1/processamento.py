import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import pygame
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

def imread_unicode(p, flags=cv2.IMREAD_COLOR):
    p = str(Path(p))
    data = np.fromfile(p, dtype=np.uint8)
    if data.size == 0:
        return None
    return cv2.imdecode(data, flags)

def abrir_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return None
    return cap

def converter_cinza(img):
    if len(img.shape) == 2:
        return img.copy()
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def converter_negativo(img):
    return cv2.bitwise_not(img)

def converter_binario_otsu(img):
    gray = converter_cinza(img)
    _, bin_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    if np.mean(bin_img) > 127:
        bin_img = cv2.bitwise_not(bin_img)
    return bin_img

def filtro_media(img):
    return cv2.blur(img, (5, 5))

def filtro_mediana(img):
    return cv2.medianBlur(img, 5)

def bordas_canny(img):
    gray = converter_cinza(img)
    return cv2.Canny(gray, 100, 200)

def aplicar_morfologia(img, operacao):
    kernel = np.ones((5, 5), np.uint8)
    if operacao == "erosao":
        return cv2.erode(img, kernel, iterations=1)
    elif operacao == "dilatacao":
        return cv2.dilate(img, kernel, iterations=1)
    elif operacao == "abertura":
        return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    elif operacao == "fechamento":
        return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    return img

def mostrar_histograma(img):
    gray = converter_cinza(img)
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    plt.plot(hist)
    plt.title("Histograma de Intensidade")
    plt.xlabel("Intensidade")
    plt.ylabel("Frequência")
    plt.grid(True)
    plt.show()

def contar_objetos(img_bin):
    kernel = np.ones((3, 3), np.uint8)
    img_bin = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernel, iterations=2)
    img_bin = cv2.morphologyEx(img_bin, cv2.MORPH_CLOSE, kernel, iterations=2)
    contours, _ = cv2.findContours(img_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    objetos = 0
    for c in contours:
        area = cv2.contourArea(c)
        if area > 100:
            objetos += 1
    return objetos

def calcular_area_perimetro_diametro(img_bin):
    gray = converter_cinza(img_bin)
    _, bin_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(bin_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    area_minima = 200
    if len(img_bin.shape) == 2:
        img_display = cv2.cvtColor(img_bin, cv2.COLOR_GRAY2BGR)
    else:
        img_display = img_bin.copy()
    for c in contours:
        area = cv2.contourArea(c)
        if area < area_minima:
            continue
        perimetro = cv2.arcLength(c, True)
        (x, y), diametro = cv2.minEnclosingCircle(c)
        (bx, by, w, h) = cv2.boundingRect(c)
        cv2.drawContours(img_display, [c], -1, (0, 255, 0), 2)
        cv2.putText(img_display, f"A:{area:.0f}", (bx, by - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        cv2.putText(img_display, f"P:{perimetro:.0f}", (bx, by + h + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        cv2.putText(img_display, f"D:{diametro:.0f}", (bx + w // 2 - 20, by + h // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    return img_display

def rastrear_objeto():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return
    ret, frame = cap.read()
    if not ret:
        return
    roi = cv2.selectROI("Selecione o objeto", frame, False)
    cv2.destroyWindow("Selecione o objeto")
    if roi == (0, 0, 0, 0):
        cap.release()
        return
    tracker = None
    try:
        tracker = cv2.TrackerCSRT_create()
    except AttributeError:
        try:
            tracker = cv2.legacy.TrackerCSRT_create()
        except AttributeError:
            try:
                tracker = cv2.TrackerCSRT.create()
            except AttributeError:
                try:
                    tracker = cv2.TrackerKCF_create()
                except Exception:
                    cap.release()
                    return
    tracker.init(frame, roi)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        success, box = tracker.update(frame)
        if success:
            (x, y, w, h) = [int(v) for v in box]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "Rastreando objeto", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Objeto perdido", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.imshow("Rastreamento", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def detectar_ed_sheeran():
    MIN_GOOD_MATCHES = 18
    HIST_CORREL_THRESH = 0.70
    NO_DETECT_RESET_FRAMES = 20
    sound_available = False
    try:
        pygame.mixer.init()
        sound_path = os.path.normpath(os.path.join(ASSETS_DIR, "vine-boom-392646 (1).mp3"))
        if os.path.exists(sound_path):
            pygame.mixer.music.load(sound_path)
            sound_available = True
    except Exception:
        sound_available = False
    ref_path = os.path.normpath(os.path.join(ASSETS_DIR, "ed.jpg"))
    if not os.path.exists(ref_path):
        return
    ref_img_color = imread_unicode(ref_path)
    if ref_img_color is None:
        return
    ref_gray = cv2.cvtColor(ref_img_color, cv2.COLOR_BGR2GRAY)
    haar_path = os.path.join(ASSETS_DIR, "haarcascade_frontalface_default.xml")
    face_cascade = cv2.CascadeClassifier(haar_path)
    if face_cascade.empty():
        return
    faces_ref = face_cascade.detectMultiScale(ref_gray, 1.1, 5, minSize=(30, 30))
    if len(faces_ref) == 0:
        ref_face_gray = ref_gray
        ref_face_color = ref_img_color
    else:
        x, y, w, h = faces_ref[0]
        ref_face_gray = ref_gray[y:y + h, x:x + w]
        ref_face_color = ref_img_color[y:y + h, x:x + w]
    orb = cv2.ORB_create(1000)
    kp_ref, des_ref = orb.detectAndCompute(ref_face_gray, None)
    if des_ref is None or len(kp_ref) < 5:
        return
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    video_path = os.path.normpath(os.path.join(ASSETS_DIR, "eds_heinz_ad.mp4"))
    if not os.path.exists(video_path):
        return
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return
    tocando = False
    no_detect_counter = 0
    ed_detected_count = 0
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1
        scale = 0.7
        small = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(40, 40))
        ed_in_frame = False
        for (x, y, w, h) in faces:
            x0, y0, w0, h0 = [int(v / scale) for v in (x, y, w, h)]
            roi_color = frame[y0:y0 + h0, x0:x0 + w0]
            roi_gray = cv2.cvtColor(roi_color, cv2.COLOR_BGR2GRAY)
            kp_roi, des_roi = orb.detectAndCompute(roi_gray, None)
            good_matches = 0
            if des_roi is not None and len(kp_roi) >= 2:
                matches = bf.knnMatch(des_ref, des_roi, k=2)
                good = []
                for pair in matches:
                    if len(pair) != 2:
                        continue
                    m, n = pair
                    if m.distance < 0.75 * n.distance:
                        good.append(m)
                good_matches = len(good)
            hsv_ref = cv2.cvtColor(ref_face_color, cv2.COLOR_BGR2HSV)
            hsv_roi = cv2.cvtColor(roi_color, cv2.COLOR_BGR2HSV)
            h_ref = cv2.calcHist([hsv_ref], [0, 1], None, [30, 32], [0, 180, 0, 256])
            h_roi = cv2.calcHist([hsv_roi], [0, 1], None, [30, 32], [0, 180, 0, 256])
            cv2.normalize(h_ref, h_ref)
            cv2.normalize(h_roi, h_roi)
            hist_score = cv2.compareHist(h_ref, h_roi, cv2.HISTCMP_CORREL)
            is_ed = (good_matches >= MIN_GOOD_MATCHES and hist_score >= HIST_CORREL_THRESH)
            color = (0, 255, 0) if is_ed else (255, 0, 255)
            label = "ED SHEERAN" if is_ed else "Rosto"
            cv2.rectangle(frame, (x0, y0), (x0 + w0, y0 + h0), color, 2)
            cv2.putText(frame, f"{label}  m:{good_matches}  h:{hist_score:.2f}", (x0, max(20, y0 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            if is_ed:
                ed_in_frame = True
                ed_detected_count += 1
                if sound_available and not tocando:
                    try:
                        pygame.mixer.music.play()
                        tocando = True
                        no_detect_counter = 0
                    except Exception:
                        pass
        if not ed_in_frame:
            no_detect_counter += 1
            if no_detect_counter > NO_DETECT_RESET_FRAMES:
                tocando = False
                no_detect_counter = 0
        info = f"Frame:{frame_count} Faces:{len(faces)} EdHits:{ed_detected_count}"
        cv2.putText(frame, info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imshow("Achar Ed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
