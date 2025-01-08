import flet as ft
from flet import Page, Column, TextField, Text, ElevatedButton, Container, alignment, padding, border_radius
import json
import random

def main(page: Page):
    with open("translate.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        sentences = data["sentences"]

    header = Container(
        content=Text(value="WORDS", size=24, weight="bold", italic=True),
        alignment=ft.alignment.center,
        margin=20
    )

    def get_button_colors():
        if page.theme_mode == "dark":
            return "#4A4A4A", "#D3D3D3"
        else:
            return "#e0e0e0", "#000000"

    input_field = TextField(label="Введите предложение", width=400, border_color="#e0e0e0")

    russian_sentence = Text(value="", size=20, weight="bold", text_align="center")
    instruction_text = Text(value="Переведите", size=16, text_align="center")

    button_bgcolor, button_textcolor = get_button_colors()
    answer_button = ElevatedButton(text="Ответить", bgcolor=button_bgcolor, color=button_textcolor, width=200)
    continue_button = ElevatedButton(text="Продолжить", bgcolor=button_bgcolor, color=button_textcolor, width=200, visible=False)

    sentence_container = Container(
        content=Column(
            [
                instruction_text,
                russian_sentence
            ],
            alignment="center",
            horizontal_alignment="center",
        ),
    )

    def load_random_sentence():
        global current_index
        if sentences:
            current_index = random.randint(0, len(sentences) - 1)
            russian_sentence.value = sentences[current_index]["russian"]
            input_field.value = ""
            input_field.border_color = "#e0e0e0"
            answer_button.visible = True
            continue_button.visible = False
            page.update()
        else:
            russian_sentence.value = "Предложения закончились!"
            input_field.visible = False
            answer_button.visible = False
            page.update()

    def check_answer(e):
        user_input = input_field.value.lower().split()
        correct_answer = sentences[current_index]["english"].lower().split()

        if user_input == correct_answer:
            input_field.border_color = "green"
        else:
            input_field.border_color = "red"
            correct_sentence = " ".join(correct_answer)
            russian_sentence.value = f"Правильно: {correct_sentence}"

        answer_button.visible = False
        continue_button.visible = True
        page.update()

    def continue_to_next(e):
        load_random_sentence()

    answer_button.on_click = check_answer
    continue_button.on_click = continue_to_next

    page.add(
        Column(
            [
                header,
                sentence_container,
                input_field,
                answer_button,
                continue_button
            ],
            horizontal_alignment="center",
            expand=True,
            spacing=30
        )
    )

    load_random_sentence()

    def on_theme_change(e):
        button_bgcolor, button_textcolor = get_button_colors()
        answer_button.bgcolor = button_bgcolor
        answer_button.color = button_textcolor
        continue_button.bgcolor = button_bgcolor
        continue_button.color = button_textcolor
        page.update()

    page.on_theme_change = on_theme_change

ft.app(target=main, view=None, port=8000)