import flet as ft
import yt_dlp

class TodoApp(ft.Column):

    def __init__(self):
        super().__init__()
        self.new_task = ft.TextField(hint_text="Adicione o link desejado para iniciar", expand=True)
        self.tasks_view = ft.Column()
        self.video_info_view = ft.Column()
        self.progress_bar = ft.ProgressBar(value=0)  # Inicializa a barra de progresso
        self.progress_bar.max = 100  # Define o valor máximo da barra de progresso
        self.progress_text = ft.Text("0%")  # Texto para mostrar a porcentagem
        self.speed_text = ft.Text("")  # Texto para mostrar a taxa de download
        self.eta_text = ft.Text("")  # Texto para mostrar o tempo estimado
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
            self.video_info_view,
            ft.Row(
                controls=[
                    self.progress_bar,  # Barra de progresso
                    self.progress_text,  # Texto de porcentagem
                    self.speed_text,  # Texto de taxa de download
                    self.eta_text,  # Texto de tempo estimado
                ],
            ),
            self.tasks_view,
        ]
    def progress_hook(self, d):
        if d.get('downloaded_bytes') is not None and d.get('total_bytes') is not None:
            downloaded = d['downloaded_bytes']
            total = d['total_bytes']
            if total > 0:
                percentage = downloaded / total * 100
                self.progress_bar.value = percentage  # Atualiza a barra de progresso
                self.progress_text.value = f"{int(percentage)}%"  # Atualiza o texto da porcentagem
                
                # Atualiza a taxa de download e o tempo estimado
                if 'speed' in d and d['speed'] is not None:
                    self.speed_text.value = f"Velocidade: {d['speed'] / (1024 * 1024):.2f} MiB/s"  # Velocidade em MiB/s
                if 'eta' in d and d['eta'] is not None:
                    self.eta_text.value = f"ETA: {d['eta']}s"  # Tempo estimado em segundos
                
                self.update()  # Atualiza a interface
    def add_clicked(self, e):
        link = self.new_task.value
        if not link:
            print("Por favor, insira um link válido.")
            return

        # Reseta a barra de progresso antes do download
        self.progress_bar.value = 0
        self.progress_text.value = "0%"  
        self.speed_text.value = ""  # Limpa a taxa de download
        self.eta_text.value = ""  # Limpa o tempo estimado
        self.update()  # Atualiza a interface para mostrar a barra de progresso zerada

        ydl_opts = {
            'format': 'best',
            'outtmpl': '%(title)s.%(ext)s',
            'progress_hooks': [self.progress_hook],  # Adiciona o hook de progresso
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info_dict = ydl.extract_info(link, download=False)
                self.video_info_view.controls = [
                    ft.Text(f"Título: {info_dict['title']}"),
                    ft.Text(f"Visualizações: {info_dict.get('view_count', 'Não disponível')}"),
                    ft.Text(f"Descrição: {info_dict.get('description', 'Descrição não disponível.')[:200]}..."),
                    ft.Text(f"Avaliações: {info_dict.get('average_rating', 'Avaliações não disponíveis.')}")
                ]
                ydl.download([link])
                print("Download concluído com sucesso!")
                self.video_info_view.controls.append(ft.Text("Download concluído com sucesso!"))
                self.progress_bar.value = 100  # Finaliza a barra de progresso
                self.progress_text.value = "100%"  # Atualiza a porcentagem para 100%
                self.speed_text.value = ""  # Limpa a taxa de download
                self.eta_text.value = ""  # Limpa o tempo estimado
            except Exception as ex:
                print(f"Erro durante o download: {ex}")
                self.video_info_view.controls.append(ft.Text(f"Erro durante o download: {ex}", color="red"))

        self.update()

def main(page: ft.Page):
    page.title = "YouTubeDownloader - for Telma Rodrigues"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.update()

    todo = TodoApp()
    page.add(todo)

ft.app(target=main)
