import flet as ft
import yt_dlp
import time

class TodoApp(ft.Column):

    def __init__(self):
        super().__init__()
        self.new_task = ft.TextField(hint_text="Adicione o link desejado para iniciar", expand=True)
        self.video_info_view = ft.Column()
        self.thumbnail_image = ft.Image(visible=False)
        self.loading_animation = ft.ProgressRing(visible=False)  # Animação de carregamento
        self.tasks_view = ft.Column(scroll=ft.ScrollMode.AUTO)  # Histórico de downloads com scroll
        self.width = 600
        self.controls = [
            ft.Row(
                controls=[
                    self.new_task,
                    ft.FloatingActionButton(
                        icon=ft.icons.ADD, on_click=self.add_clicked
                    ),
                ],
            ),
            ft.Row(
                controls=[
                    ft.ElevatedButton("MP4", on_click=self.download_mp4, width=150, height=50),
                    ft.ElevatedButton("MP3", on_click=self.download_mp3, width=150, height=50),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20
            ),
            self.video_info_view,
            self.loading_animation,  # Animação de carregamento
            ft.Container(
                self.tasks_view,
                height=300,  # Define a altura do container que vai segurar o histórico
            ),
        ]

    def extract_video_info(self, link):
        with yt_dlp.YoutubeDL() as ydl:
            try:
                info_dict = ydl.extract_info(link, download=False)
                
                # Exibe as informações do vídeo
                self.video_info_view.controls = [
                    ft.Text(f"Título: {info_dict['title']}"),
                    ft.Text(f"Visualizações: {info_dict.get('view_count', 'Não disponível')}"),
                    ft.Text(f"Descrição: {info_dict.get('description', 'Descrição não disponível.')[:200]}..."),
                    ft.Text(f"Avaliações: {info_dict.get('average_rating', 'Avaliações não disponíveis.')}")
                ]
                
                # Carrega a imagem da miniatura
                thumbnail_url = info_dict['thumbnail']
                self.thumbnail_image.src = thumbnail_url
                self.thumbnail_image.visible = True

                self.update()
                return info_dict  # Retorna as informações do vídeo para uso posterior
            except Exception as ex:
                self.video_info_view.controls.append(ft.Text(f"Erro durante o processamento do link: {ex}", color="red"))
                self.update()
                return None

    def add_clicked(self, e):
        link = self.new_task.value
        if not link:
            self.video_info_view.controls.append(ft.Text("Por favor, insira um link válido.", color="red"))
            self.update()
            return

        self.extract_video_info(link)

    def download_mp4(self, e):
        self.download_video('mp4')

    def download_mp3(self, e):
        self.download_video('mp3')

    def download_video(self, format):
        link = self.new_task.value
        if not link:
            self.video_info_view.controls.append(ft.Text("Por favor, insira um link válido.", color="red"))
            self.update()
            return

        # Extraia as informações do vídeo antes de iniciar o download
        info_dict = self.extract_video_info(link)
        if not info_dict:
            return

        # Mostra a animação de carregamento
        self.loading_animation.visible = True
        self.update()

        ydl_opts = {
            'format': 'bestaudio/best' if format == 'mp3' else 'best',
            'outtmpl': '%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }] if format == 'mp3' else [],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([link])
                completion_text = ft.Text(f"DOWNLOAD CONCLUÍDO EM FORMATO {format.upper()}!", color="yellow", weight="bold")

                # Adiciona ao histórico com a miniatura
                self.tasks_view.controls.insert(0, ft.Column(controls=[
                    ft.Text(f"Título: {info_dict['title']}"),
                    ft.Image(src=info_dict['thumbnail'], width=200, height=150),
                    ft.Text(f"Formato: {format.upper()}"),
                    ft.Text(f"Link: {link}"),
                    completion_text
                ]))
                self.update()

            except Exception as ex:
                self.video_info_view.controls.append(ft.Text(f"Erro durante o download: {ex}", color="red"))

        # Esconde a animação de carregamento após o download
        self.loading_animation.visible = False
        self.update()

def main(page: ft.Page):
    page.title = "YouTubeDownloader - for Telma Rodrigues"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_maximized = True  # Inicia o aplicativo maximizado, com botões de controle visíveis
    page.icon = "you.ico"
    page.window_minimizable = True
    page.window_resizable = True
    page.window_maximizable = True
    page.update()

    todo = TodoApp()
    page.add(todo)

ft.app(target=main)

