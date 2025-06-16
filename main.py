import flet as ft
from controller import AppController

def main(page: ft.Page):
    controller = AppController(page)
    controller.run()

ft.app(target=main)
