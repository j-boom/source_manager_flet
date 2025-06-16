import flet as ft
from controllers import AppController

def main(page: ft.Page):
    controller = AppController(page)
    controller.run()

ft.app(target=main)
