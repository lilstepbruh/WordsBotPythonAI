import flet as ft
from flet import Page, Column, Row, Text, ElevatedButton, alignment
import sqlite3
from threading import Timer
import random

def get_db_connection():
    conn = sqlite3.connect(r'/\words.db')
    return conn

learned_words = []
learning_words = []
current_index = 0
words = {}

def main(page: Page):
    global current_index, words

    def load_words():
        global words
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT word, translation FROM words")
        words = {word: translation for word, translation in cursor.fetchall()}
        conn.close()

    load_words()
    words_list = list(words.items())

    word_text = Text(value="(Слово на русском)", size=20, weight="bold", text_align="center")
    header = Text(value="WORDS", size=24, weight="bold", italic=True, text_align="center")
    question_text = Text(value="Знаете ли вы слово ...", size=20, text_align="center")

    Content = Column((header, question_text, word_text), alignment="center",
                     horizontal_alignment="center", spacing=50)

    def get_button_colors():
        if page.theme_mode == "dark":
            return "#4A4A4A", "#D3D3D3"
        else:
            return "#e0e0e0", "#000000"

    def load_next_word():
        global current_index
        if current_index < len(words_list):
            word, translation = words_list[current_index]
            word_text.value = word
            options = [translation]
            while len(options) < 4 and len(options) < len(words_list):
                _, random_translation = random.choice(words_list)
                if random_translation not in options:
                    options.append(random_translation)
            random.shuffle(options)

            button_bgcolor, button_textcolor = get_button_colors()

            for i, option in enumerate(options):
                buttons.controls[i].text = option
                buttons.controls[i].bgcolor = button_bgcolor
                buttons.controls[i].color = button_textcolor
                buttons.controls[i].width = 350
            page.update()
        else:
            word_text.value = "Все слова просмотрены!"
            for button in buttons.controls:
                button.visible = False
            page.update()

    def handle_answer(option, button):
        global current_index
        word, correct_translation = words_list[current_index]
        if option == correct_translation:
            button.bgcolor = "green"
        else:
            button.bgcolor = "red"
        for btn in buttons.controls:
            if btn.text == correct_translation:
                btn.bgcolor = "green"
            btn.update()

        page.update()
        current_index += 1
        Timer(1.5, load_next_word).start()

    buttons = Column(
        [
            ElevatedButton(text="Вариант 1",
                           on_click=lambda e: handle_answer(e.control.text, e.control)),
            ElevatedButton(text="Вариант 2",
                           on_click=lambda e: handle_answer(e.control.text, e.control)),
            ElevatedButton(text="Вариант 3",
                           on_click=lambda e: handle_answer(e.control.text, e.control)),
            ElevatedButton(text="Вариант 4",
                           on_click=lambda e: handle_answer(e.control.text, e.control)),
        ],
        alignment="center",
        horizontal_alignment="center",
        spacing=10,
        width=400,
    )

    page.add(
        Column(
            [
                Content,
                buttons
            ],
            horizontal_alignment="center",
            expand=True,
            spacing=70
        )
    )

    load_next_word()

ft.app(target=main, view=None, port=8000)
