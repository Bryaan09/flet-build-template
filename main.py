import flet as ft
import yt_dlp
import os
import threading
import time

# --- CORES ---
COR_FUNDO = "#121212"
COR_CARD = "#1e1e1e"
COR_TEXTO = "#ffffff"
COR_ACCENT = "#00e054"  # Verde Neon
COR_ERRO = "#ff4757"


def main(page: ft.Page):
    # --- CONFIGURAÇÕES INICIAIS ---
    page.title = "BRY DOWNLOADS"
    page.bgcolor = COR_FUNDO
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0  # Padding zero pois usaremos SafeArea

    # Variáveis de Estado
    download_path = ""
    is_android = False

    # --- DETECTAR SISTEMA ---
    try:
        from jnius import autoclass
        is_android = True
        download_path = "/storage/emulated/0/Download"
    except ImportError:
        is_android = False
        download_path = os.path.join(os.path.expanduser("~"), "Downloads")
        # Simulação de tamanho APENAS no PC
        page.window.width = 390
        page.window.height = 844

    # --- FUNÇÕES ---

    def colar_link(e):
        try:
            # Tenta pegar o clipboard
            clip = page.get_clipboard()

            if clip:
                txt_url.value = clip
                txt_url.error_text = None
                txt_url.update()
            else:
                # Feedback se estiver vazio
                txt_url.hint_text = "Nada na área de transferência!"
                txt_url.update()
                time.sleep(2)
                txt_url.hint_text = "Cole o link aqui..."
                txt_url.update()
        except Exception as ex:
            txt_url.error_text = "Erro ao colar"
            txt_url.update()
            print(f"Erro clipboard: {ex}")

    def hook(d):
        if d['status'] == 'downloading':
            try:
                p = d.get('_percent_str', '0%').replace('%', '')
                val = float(p) / 100
                pb_progresso.value = val
                lbl_status.value = "Baixando..."
                lbl_porcentagem.value = f"{d.get('_percent_str', '0%')}"
                page.update()
            except:
                pass
        elif d['status'] == 'finished':
            lbl_status.value = "Processando..."
            pb_progresso.value = 1
            page.update()

    def run_download(url, formato, qualidade):
        ydl_opts = {
            'outtmpl': f'{download_path}/%(title)s.%(ext)s',
            'progress_hooks': [hook],
            'ignoreerrors': True,
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
        }

        if formato == "mp3":
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            ydl_opts['format'] = 'bestvideo+bestaudio/best'

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            lbl_status.value = "Concluído!"
            lbl_status.color = COR_ACCENT
            page.update()

            time.sleep(3)
            container_progresso.visible = False
            btn_download.disabled = False
            btn_download.content = ft.Text(
                "INICIAR DOWNLOAD", color="black", weight=ft.FontWeight.BOLD)
            page.update()

        except Exception as e:
            lbl_status.value = f"Erro: {str(e)}"
            lbl_status.color = COR_ERRO
            btn_download.disabled = False
            page.update()

    def iniciar_clique(e):
        url = txt_url.value
        if not url:
            txt_url.error_text = "Cole um link primeiro!"
            txt_url.update()
            return

        txt_url.error_text = None
        btn_download.disabled = True
        btn_download.content = ft.Text(
            "BAIXANDO...", color="black", weight=ft.FontWeight.BOLD)

        container_progresso.visible = True
        lbl_status.color = "#888888"
        page.update()

        threading.Thread(target=run_download, args=(
            url, radio_formato.value, dd_qualidade.value), daemon=True).start()

    # --- ELEMENTOS VISUAIS ---

    titulo = ft.Column([
        ft.Row(
            [
                ft.Text("BRY", size=30, weight=ft.FontWeight.BOLD,
                        color=COR_ACCENT, font_family="Impact"),
                ft.Text(" DOWNLOADS", size=30, weight=ft.FontWeight.BOLD,
                        color=COR_TEXTO, font_family="Impact"),
            ],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        ft.Text("YouTube Downloader", size=12, color="#888888")
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # Input e Botão Colar
    txt_url = ft.TextField(
        label="Link do Vídeo",
        hint_text="Cole o link aqui...",
        border_color=COR_ACCENT,
        bgcolor=COR_CARD,
        color=COR_TEXTO,
        text_size=16,
        expand=True,  # Ocupa todo espaço disponível na linha
        border_radius=10
    )

    btn_colar = ft.IconButton(
        icon=ft.Icons.PASTE,
        icon_color=COR_ACCENT,
        tooltip="Colar Link",
        on_click=colar_link,
        style=ft.ButtonStyle(
            bgcolor=COR_CARD, shape=ft.RoundedRectangleBorder(radius=10))
    )

    # Linha de input responsiva
    input_row = ft.Row([txt_url, btn_colar],
                       alignment=ft.MainAxisAlignment.CENTER)

    # Configurações
    radio_formato = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="mp3", label="MP3 (Áudio)",
                     active_color=COR_ACCENT),
            ft.Radio(value="mp4", label="MP4 (Vídeo)",
                     active_color=COR_ACCENT),
        ], alignment=ft.MainAxisAlignment.CENTER),
        value="mp3"
    )

    dd_qualidade = ft.Dropdown(
        options=[
            ft.dropdown.Option("Melhor"),
            ft.dropdown.Option("Média"),
            ft.dropdown.Option("Baixa"),
        ],
        value="Melhor",
        bgcolor=COR_CARD,
        border_color=COR_ACCENT,
        border_radius=10,
        expand=True  # Expande para ocupar largura
    )

    lbl_pasta = ft.Text(f"Salvando em: {download_path}", size=12,
                        color="#555555", italic=True, text_align=ft.TextAlign.CENTER)

    # Botão Principal (Largo)
    btn_download = ft.ElevatedButton(
        content=ft.Text("INICIAR DOWNLOAD", color="black",
                        weight=ft.FontWeight.BOLD),
        bgcolor=COR_ACCENT,
        width=float("inf"),  # Ocupa largura total disponível
        height=50,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
        on_click=iniciar_clique
    )

    # Progresso (Sem largura fixa)
    pb_progresso = ft.ProgressBar(color=COR_ACCENT, bgcolor="#333333", value=0)
    lbl_status = ft.Text("Aguardando...", color="#888888", size=14)
    lbl_porcentagem = ft.Text("0%", color=COR_ACCENT,
                              weight=ft.FontWeight.BOLD)

    container_progresso = ft.Container(
        content=ft.Column([
            pb_progresso,
            ft.Row([lbl_status, lbl_porcentagem],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ]),
        visible=False,
        bgcolor=COR_CARD,
        padding=15,
        border_radius=10
    )

    # --- MONTAGEM DO LAYOUT (SAFE AREA) ---
    # SafeArea garante que não fique embaixo da câmera no Android
    layout_principal = ft.Column(
        [
            ft.Container(height=10),
            titulo,
            ft.Container(height=20),
            input_row,
            ft.Container(height=5),
            lbl_pasta,
            ft.Container(height=20),
            ft.Divider(color="#333333"),
            ft.Text("Formato e Qualidade:", color="#888888"),
            radio_formato,
            # Row ajuda a controlar a largura do dropdown
            ft.Row([dd_qualidade]),
            ft.Container(height=30),
            btn_download,
            ft.Container(height=20),
            container_progresso
        ],
        scroll=ft.ScrollMode.HIDDEN,  # Scroll automático se a tela for pequena
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    page.add(
        ft.SafeArea(
            ft.Container(
                content=layout_principal,
                padding=20
            )
        )
    )


if __name__ == "__main__":
    ft.app(main)
