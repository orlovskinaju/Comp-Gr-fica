import customtkinter as ctk
import cv2
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import threading
import processamento as proc

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Trabalho 1 - Processamento de Imagens")
        self.geometry("1000x700")

        self.imagem_atual = None
        self.cap = None
        self.camera_aberta = False

        titulo = ctk.CTkLabel(self, text="Trabalho 1 - Processamento de Imagens",
                              font=("Helvetica", 22, "bold"))
        titulo.pack(pady=15)

        frame_principal = ctk.CTkFrame(self)
        frame_principal.pack(padx=15, pady=15, fill="both", expand=True)

        self.label_imagem = ctk.CTkLabel(frame_principal, text="", corner_radius=10)
        self.label_imagem.pack(side="left", expand=True, fill="both", padx=10, pady=10)

        painel = ctk.CTkFrame(frame_principal, width=240)
        painel.pack(side="right", fill="y", padx=10, pady=10)

        ctk.CTkLabel(painel, text="Controles", font=("Helvetica", 18, "bold")).pack(pady=10)

        ctk.CTkButton(painel, text="Carregar Imagem", command=self.carregar_imagem).pack(pady=5)
        ctk.CTkButton(painel, text="Abrir Câmera", command=self.abrir_camera).pack(pady=5)
        ctk.CTkButton(painel, text="❌ Fechar Câmera", fg_color="red", hover_color="#b00000",
                      command=self.fechar_camera).pack(pady=5)
        ctk.CTkButton(painel, text="Rastrear Objeto", command=self.rastrear_objeto).pack(pady=5)
        ctk.CTkButton(painel, text="Vídeo Ed Sheeran", command=self.detectar_ed_sheeran).pack(pady=5)

        self.filtros = {
            "Cinza": proc.converter_cinza,
            "Negativo": proc.converter_negativo,
            "Binário (Otsu)": proc.converter_binario_otsu,
            "Filtro de Média": proc.filtro_media,
            "Filtro de Mediana": proc.filtro_mediana,
            "Bordas (Canny)": proc.bordas_canny,
            "Erosão": lambda img: proc.aplicar_morfologia(img, "erosao"),
            "Dilatação": lambda img: proc.aplicar_morfologia(img, "dilatacao"),
            "Abertura": lambda img: proc.aplicar_morfologia(img, "abertura"),
            "Fechamento": lambda img: proc.aplicar_morfologia(img, "fechamento"),
        }

        ctk.CTkLabel(painel, text="Selecione um filtro:", font=("Helvetica", 14)).pack(pady=10)
        self.combo_filtro = ctk.CTkComboBox(painel, values=list(self.filtros.keys()))
        self.combo_filtro.pack(pady=5)

        ctk.CTkButton(painel, text="✨ Aplicar Filtro", command=self.aplicar_filtro).pack(pady=10)
        ctk.CTkButton(painel, text="📊 Histograma", command=self.mostrar_histograma).pack(pady=5)
        ctk.CTkButton(painel, text="📐 Área/Perímetro", command=self.medidas_objetos).pack(pady=5)
        ctk.CTkButton(painel, text="🔢 Contar Objetos", command=self.contar_objetos).pack(pady=5)

        ctk.CTkButton(painel, text="🔁 Resetar", fg_color="gray", command=self.resetar).pack(pady=15)

        self.status = ctk.CTkLabel(self, text="Pronto.", anchor="w", font=("Consolas", 12))
        self.status.pack(fill="x", pady=5, padx=10)

    def atualizar_status(self, texto):
        self.status.configure(text=texto)

    def carregar_imagem(self):
        caminho = filedialog.askopenfilename(filetypes=[("Imagens", "*.jpg *.png *.jpeg *.bmp")])
        if not caminho:
            return
        img = cv2.imread(caminho)
        if img is None:
            messagebox.showerror("Erro", "Não foi possível abrir a imagem.")
            return
        self.imagem_atual = img
        self.exibir_imagem(img)
        self.atualizar_status(f"Imagem carregada: {os.path.basename(caminho)}")

    def abrir_camera(self):
        if self.camera_aberta:
            messagebox.showinfo("Câmera", "A câmera já está aberta.")
            return
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Erro", "Não foi possível abrir a câmera.")
            return
        self.camera_aberta = True
        self.atualizar_status("Câmera aberta.")
        threading.Thread(target=self.atualizar_camera, daemon=True).start()

    def fechar_camera(self):
        if self.camera_aberta:
            self.camera_aberta = False
            if self.cap and self.cap.isOpened():
                self.cap.release()
            self.atualizar_status("Câmera encerrada.")
        else:
            messagebox.showinfo("Câmera", "Nenhuma câmera está ativa.")

    def atualizar_camera(self):
        while self.camera_aberta:
            ret, frame = self.cap.read()
            if not ret:
                break
            filtro = self.combo_filtro.get()
            if filtro in self.filtros:
                frame = self.filtros[filtro](frame)
            self.exibir_imagem(frame)
        if self.cap and self.cap.isOpened():
            self.cap.release()

    def exibir_imagem(self, img):
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_pil.thumbnail((700, 600))
        img_tk = ImageTk.PhotoImage(img_pil)
        self.label_imagem.configure(image=img_tk)
        self.label_imagem.image = img_tk

    def aplicar_filtro(self):
        if self.imagem_atual is None:
            messagebox.showwarning("Aviso", "Nenhuma imagem carregada.")
            return
        filtro = self.combo_filtro.get()
        if filtro not in self.filtros:
            messagebox.showwarning("Aviso", "Selecione um filtro válido.")
            return
        try:
            img_f = self.filtros[filtro](self.imagem_atual.copy())
            self.exibir_imagem(img_f)
            self.imagem_atual = img_f
            self.atualizar_status(f"Filtro aplicado: {filtro}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao aplicar filtro: {e}")

    def mostrar_histograma(self):
        if self.imagem_atual is None:
            messagebox.showwarning("Aviso", "Nenhuma imagem carregada.")
            return
        proc.mostrar_histograma(self.imagem_atual)
        self.atualizar_status("Histograma exibido.")

    def contar_objetos(self):
        if self.imagem_atual is None:
            messagebox.showwarning("Aviso", "Nenhuma imagem carregada.")
            return
        bin_img = proc.converter_binario_otsu(self.imagem_atual)
        n = proc.contar_objetos(bin_img)
        messagebox.showinfo("Contagem de Objetos", f"Total de objetos detectados: {n}")
        self.atualizar_status(f"{n} objetos detectados.")

    def medidas_objetos(self):
        if self.imagem_atual is None:
            messagebox.showwarning("Aviso", "Nenhuma imagem carregada.")
            return
        bin_img = proc.converter_binario_otsu(self.imagem_atual)
        img_medidas = proc.calcular_area_perimetro_diametro(bin_img)
        self.exibir_imagem(img_medidas)
        self.atualizar_status("Medições aplicadas.")

    def rastrear_objeto(self):
        messagebox.showinfo(
            "Instruções de Rastreamento",
            "Selecione o objeto com o mouse e pressione ENTER para confirmar.\n"
            "Pressione Q para encerrar o rastreamento."
        )
        threading.Thread(target=proc.rastrear_objeto, daemon=True).start()
        self.atualizar_status("Rastreamento iniciado...")

    def detectar_ed_sheeran(self):
        threading.Thread(target=proc.detectar_ed_sheeran, daemon=True).start()
        self.atualizar_status("Detectando Ed Sheeran no vídeo...")

    def resetar(self):
        self.imagem_atual = None
        self.label_imagem.configure(image="", text="")
        self.atualizar_status("Interface resetada.")


if __name__ == "__main__":
    App().mainloop()
