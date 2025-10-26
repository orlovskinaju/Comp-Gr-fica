import cv2
import numpy as np
import matplotlib.pyplot as plt
import pygame
import os

def carregar_imagem():
    caminho = input("Digite o caminho da imagem (ex: C:/Users/.../imagem.jpg): ")
    img = cv2.imread(caminho)
    if img is None:
        print("Erro ao carregar a imagem. Verifique o caminho ou se o arquivo existe.")
    return img

def abrir_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Não foi possível abrir a câmera.")
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
    # Inverte se o fundo estiver branco
    if np.mean(bin_img) > 127:
        bin_img = cv2.bitwise_not(bin_img)
    return bin_img

def filtro_media(img):
    return cv2.blur(img, (5,5))

def filtro_mediana(img):
    return cv2.medianBlur(img, 5)

def bordas_canny(img):
    gray = converter_cinza(img)
    return cv2.Canny(gray, 100, 200)

def aplicar_morfologia(img, operacao):
    kernel = np.ones((5,5), np.uint8)
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
    hist = cv2.calcHist([gray],[0],None,[256],[0,256])
    plt.plot(hist, color='purple')
    plt.title("Histograma de Intensidade")
    plt.xlabel("Intensidade")
    plt.ylabel("Frequência")
    plt.grid(True)
    plt.show()


def contar_objetos(img_bin):
    # aplica morfologia para reduzir ruído
    kernel = np.ones((3,3), np.uint8)
    img_bin = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernel, iterations=2)
    img_bin = cv2.morphologyEx(img_bin, cv2.MORPH_CLOSE, kernel, iterations=2)

    # encontra contornos
    contours, _ = cv2.findContours(img_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    objetos = 0
    for c in contours:
        area = cv2.contourArea(c)
        if area > 100:  # ignora ruído
            objetos += 1
    print(f"🔹 Total de objetos detectados: {objetos}")
    return objetos

def calcular_area_perimetro_diametro(img_bin):
    # Garante que seja binária
    gray = converter_cinza(img_bin)
    _, bin_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(bin_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    area_minima = 200  
    objeto_idx = 0
    for c in contours:
        area = cv2.contourArea(c)
        if area < area_minima:
            continue  
        perimetro = cv2.arcLength(c, True)
        (x, y), diametro = cv2.minEnclosingCircle(c)

        objeto_idx += 1
        print(f"Objeto {objeto_idx}: Área={area:.2f}, Perímetro={perimetro:.2f}, Diâmetro={diametro:.2f}")

    if objeto_idx == 0:
        print("Nenhum objeto significativo detectado.")

def rastrear_objeto():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erro ao acessar a câmera.")
        return

    print("Selecione a região e aperte enter!")
    print("Cancele apertando c")

    ret, frame = cap.read()
    if not ret:
        print("Não foi possível capturar o frame inicial.")
        return

    # Selecionar a ROI (região do objeto a rastrear)
    roi = cv2.selectROI("Selecione o objeto", frame, False)
    cv2.destroyWindow("Selecione o objeto")

    if roi == (0, 0, 0, 0):
        print("Nenhum objeto selecionado.")
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
                print("Tracker CSRT indisponível. Usando KCF como alternativa.")
                try:
                    tracker = cv2.TrackerKCF_create()
                except Exception:
                    print("Nenhum tracker disponível nesta versão do OpenCV.")
                    cap.release()
                    return

    tracker.init(frame, roi)
    print("Rastreamento iniciado! Pressione 'q' para sair.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        success, box = tracker.update(frame)
        if success:
            (x, y, w, h) = [int(v) for v in box]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "Rastreando objeto", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Objeto perdido", (20, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        cv2.imshow("Rastreamento", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Rastreamento encerrado.")

def processar_imagem(imagem_original):
    img = imagem_original.copy()
    while True:
        print("\n📸 Menu de Operações:")
        print("1-Cinza 2-Negativo 3-Binário 4-Média 5-Mediana 6-Bordas Canny")
        print("7-Erosão 8-Dilatação 9-Abertura 10-Fechamento")
        print("11-Histograma 12-Medir Área/Perímetro/Diâmetro")
        print("13-Contagem de Objetos 14-Reset 15-Sair")
        op = input("Escolha uma opção: ")

        if op == "1":
            img = converter_cinza(imagem_original.copy())
        elif op == "2":
            img = converter_negativo(imagem_original.copy())
        elif op == "3":
            img = converter_binario_otsu(imagem_original.copy())
        elif op == "4":
            img = filtro_media(imagem_original.copy())
        elif op == "5":
            img = filtro_mediana(imagem_original.copy())
        elif op == "6":
            img = bordas_canny(imagem_original.copy())
        elif op == "7":
            img = aplicar_morfologia(imagem_original.copy(), "erosao")
        elif op == "8":
            img = aplicar_morfologia(imagem_original.copy(), "dilatacao")
        elif op == "9":
            img = aplicar_morfologia(imagem_original.copy(), "abertura")
        elif op == "10":
            img = aplicar_morfologia(imagem_original.copy(), "fechamento")
        elif op == "11":
            mostrar_histograma(imagem_original.copy())
        elif op == "12":
            bin_img = converter_binario_otsu(imagem_original.copy())
            calcular_area_perimetro_diametro(bin_img)
        elif op == "13":
            bin_img = converter_binario_otsu(imagem_original.copy())
            n_obj = contar_objetos(bin_img)
            print(f"Total de objetos detectados: {n_obj}")
        elif op == "14":
            img = imagem_original.copy()
            print("Imagem resetada.")
        elif op == "15":
            break
        else:
            print("Opção inválida.")
            continue

        cv2.imshow("Resultado", img)
        cv2.waitKey(0)
    cv2.destroyAllWindows()

def processar_camera(cap):
    print("Teclas:")
    print("g=cinza, n=negativo, b=binário, m=média, v=mediana, c=Canny")
    print("e=erosão, d=dilatação, a=abertura, f=fechamento")
    print("r=reset, t=rastrear objeto, q=sair")
    efeito = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        display = frame.copy()

        key = cv2.waitKey(1) & 0xFF

        if key == ord('g'): efeito = 'cinza'
        elif key == ord('n'): efeito = 'negativo'
        elif key == ord('b'): efeito = 'otsu'
        elif key == ord('m'): efeito = 'media'
        elif key == ord('v'): efeito = 'mediana'
        elif key == ord('c'): efeito = 'canny'
        elif key == ord('e'): efeito = 'erosao'
        elif key == ord('d'): efeito = 'dilatacao'
        elif key == ord('a'): efeito = 'abertura'
        elif key == ord('f'): efeito = 'fechamento'
        elif key == ord('r'): efeito = None
        elif key == ord('t'):
            cap.release()
            cv2.destroyAllWindows()
            rastrear_objeto()
            cap = abrir_camera()
            continue
        elif key == ord('q'):
            break

        if efeito == 'cinza':
            display = converter_cinza(frame)
        elif efeito == 'negativo':
            display = converter_negativo(frame)
        elif efeito == 'otsu':
            display = converter_binario_otsu(frame)
        elif efeito == 'media':
            display = filtro_media(frame)
        elif efeito == 'mediana':
            display = filtro_mediana(frame)
        elif efeito == 'canny':
            display = bordas_canny(frame)
        elif efeito == 'erosao':
            display = aplicar_morfologia(frame, "erosao")
        elif efeito == 'dilatacao':
            display = aplicar_morfologia(frame, "dilatacao")
        elif efeito == 'abertura':
            display = aplicar_morfologia(frame, "abertura")
        elif efeito == 'fechamento':
            display = aplicar_morfologia(frame, "fechamento")

        cv2.imshow("Camera", display)

    cap.release()
    cv2.destroyAllWindows()

def detectar_ed_sheeran():
    MIN_GOOD_MATCHES = 15
    HIST_CORREL_THRESH = 0.75
    NO_DETECT_RESET_FRAMES = 15

    print("Iniciando detecção ESPECÍFICA do Ed Sheeran (método ORB + Haar)...")
    try:
        pygame.mixer.init()
        sound_path = "vine-boom-392646 (1).mp3"
        if os.path.exists(sound_path):
            pygame.mixer.music.load(sound_path)
            sound_available = True
        else:
            print("Arquivo de som não encontrado, continuando sem áudio...")
            sound_available = False
    except Exception as e:
        print("pygame não inicializado:", e)
        sound_available = False

    # Carrega a referência do Ed
    ref_path = "ed.jpg"
    if not os.path.exists(ref_path):
        print("Arquivo 'ed.jpg' não encontrado na pasta. Coloque a foto de referência e tente novamente.")
        return
    ref_img_color = cv2.imread(ref_path)
    if ref_img_color is None:
        print("Erro ao ler 'ed.jpg'. Verifique o arquivo.")
        return
    ref_gray = cv2.cvtColor(ref_img_color, cv2.COLOR_BGR2GRAY)

    # Detector de face Haar 
    haar_path = "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(haar_path)
    if face_cascade.empty():
        print("Não foi possível carregar o cascade de faces.")
        return

    # Detecta face o mais parecida com a refeência
    faces_ref = face_cascade.detectMultiScale(ref_gray, scaleFactor=1.1, minNeighbors=5, minSize=(30,30))
    if len(faces_ref) == 0:
        # se não encontrar, usa a imagem inteira (menos ideal)
        ref_face_gray = ref_gray
        print("Nenhuma face detectada em ed.jpg; usando a imagem inteira como referência.")
    else:
        x,y,w,h = faces_ref[0]
        ref_face_gray = ref_gray[y:y+h, x:x+w]

    # Cria descritor ORB e extrai keypoints/descritores da referência
    orb = cv2.ORB_create(1000)
    kp_ref, des_ref = orb.detectAndCompute(ref_face_gray, None)
    if des_ref is None or len(kp_ref) < 5:
        print("Não foi possível extrair descritores da referência. Escolha outra foto (frontal e nítida).")
        return

    # BFMatcher para ORB
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

    # Abre o vídeo
    video_path = "Ed's Heinz Ad.mp4"
    if not os.path.exists(video_path):
        print(f"Vídeo '{video_path}' não encontrado. Coloque na pasta e rode novamente.")
        return
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Não foi possível abrir o vídeo.")
        return


    tocando = False
    no_detect_counter = 0
    frame_count = 0
    ed_detected_count = 0

    print("Sistema pronto. Pressione 'q' na janela para sair.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1
        scale = 0.7
        small = cv2.resize(frame, (0,0), fx=scale, fy=scale)
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)

        # Detecta faces no frame redimensionado
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30,30))

        ed_in_frame = False

        for (x,y,w,h) in faces:
            x_o = int(x / scale)
            y_o = int(y / scale)
            w_o = int(w / scale)
            h_o = int(h / scale)
            roi_color = frame[y_o:y_o+h_o, x_o:x_o+w_o]
            roi_gray = cv2.cvtColor(roi_color, cv2.COLOR_BGR2GRAY)
            kp_roi, des_roi = orb.detectAndCompute(roi_gray, None)
            good_matches = 0
            if des_roi is not None and len(kp_roi) >= 2:
                matches = bf.knnMatch(des_ref, des_roi, k=2)
                good = []
                for m_n in matches:
                    if len(m_n) != 2:
                        continue
                    m, n = m_n
                    if m.distance < 0.75 * n.distance:
                        good.append(m)
                good_matches = len(good)

            hist_score = 0.0
            try:
                ref_hsv = cv2.cvtColor(ref_face_gray, cv2.COLOR_GRAY2BGR) if len(ref_face_gray.shape)==2 else ref_face_gray
                ref_color = ref_img_color if 'ref_img_color' in locals() else None
                if ref_color is not None:
                    if len(faces_ref) > 0:
                        rx,ry,rw,rh = faces_ref[0]
                        ref_face_color = ref_img_color[ry:ry+rh, rx:rx+rw]
                    else:
                        ref_face_color = ref_img_color
                    hsv_ref = cv2.cvtColor(ref_face_color, cv2.COLOR_BGR2HSV)
                    hsv_roi = cv2.cvtColor(roi_color, cv2.COLOR_BGR2HSV)
                    h_ref = cv2.calcHist([hsv_ref], [0,1], None, [30,32], [0,180,0,256])
                    h_roi = cv2.calcHist([hsv_roi], [0,1], None, [30,32], [0,180,0,256])
                    cv2.normalize(h_ref, h_ref)
                    cv2.normalize(h_roi, h_roi)
                    hist_score = cv2.compareHist(h_ref, h_roi, cv2.HISTCMP_CORREL)
                else:
                    hist_score = 0.0
            except Exception:
                hist_score = 0.0
            is_ed = (good_matches >= MIN_GOOD_MATCHES and hist_score >= HIST_CORREL_THRESH)
            if is_ed:
                ed_in_frame = True
                ed_detected_count += 1
                color = (0,255,0)
                label = "ED SHEERAN"
            else:
                color = (255,0,255)
                label = "Rosto"

            cv2.rectangle(frame, (x_o, y_o), (x_o + w_o, y_o + h_o), color, 2)
            cv2.putText(frame, label, (x_o, max(0, y_o-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            cv2.putText(frame, f"matches:{good_matches}", (x_o, y_o + h_o + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)

            # Gatilho de som
            if is_ed and not tocando and sound_available:
                try:
                    pygame.mixer.music.play()
                except:
                    pass
                tocando = True
                no_detect_counter = 0

        if not ed_in_frame:
            no_detect_counter += 1
            if no_detect_counter > NO_DETECT_RESET_FRAMES:
                tocando = False
                no_detect_counter = 0

        # Mostra info
        info = f"Frame:{frame_count} Faces:{len(faces)} EdHits:{ed_detected_count}"
        cv2.putText(frame, info, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

        cv2.imshow("Achar Ed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Análise finalizada. Frames processados:", frame_count)


if __name__ == "__main__":
    while True:
        print("\nMenu Principal:")
        print("1-Carregar imagem")
        print("2-Abrir câmera")
        print("3-Sair")
        print("4-Detectar Ed Sheeran no vídeo")
        escolha = input("Escolha uma opção: ")

        if escolha == "1":
            imagem = carregar_imagem()
            if imagem is not None:
                processar_imagem(imagem)
        elif escolha == "2":
            cam = abrir_camera()
            if cam is not None:
                processar_camera(cam)
        elif escolha == "3":
            print("Saindo...")
            break
        elif escolha == "4":
            detectar_ed_sheeran()
        else:
            print("Opção inválida.")