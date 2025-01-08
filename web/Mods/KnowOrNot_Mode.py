import flet as ft
from flet import Page, Column, Row, Text, ElevatedButton, alignment
import sqlite3
import random
from threading import Timer


def get_db_connection():
    conn = sqlite3.connect(r'/\words.db')
    return conn

words = {}

def main(page: Page):
    global words

    word_text = Text(value="(Слово на русском)", size=20, weight="bold", text_align="center")
    translation_text = Text(value="", size=18, text_align="center")

    def load_words():
        global words
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT word, translation FROM words")
        words = dict(cursor.fetchall())
        conn.close()

    load_words()
    word_list = list(words.keys())

    def fetch_random_word():
        if word_list:
            word = random.choice(word_list)
            return word
        return None

    def display_word():
        word = fetch_random_word()
        if word:
            word_text.value = word
            translation_text.value = ""
            yes_button.disabled = False
            no_button.disabled = False
        else:
            word_text.value = "Все слова просмотрены!"
            translation_text.value = ""
            yes_button.disabled = True
            no_button.disabled = True
        page.update()

    def on_yes_click(e):
        display_word()

    def on_no_click(e):
        word = word_text.value
        if word:
            translation = words.get(word, "")
            translation_text.value = translation
            page.update()

            Timer(1.5, display_word).start()

    def get_button_colors():
        if page.theme_mode == "dark":
            return "#4A4A4A", "#D3D3D3"
        else:
            return "#e0e0e0", "#000000"

    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    header = Text(value="WORDS", size=24, weight="bold", italic=True, text_align="center")
    question_text = Text(value="Знаете ли вы слово ...", size=20, text_align="center")

    button_bgcolor, button_textcolor = get_button_colors()

    yes_button = ElevatedButton(text="Да", on_click=on_yes_click, expand=True, bgcolor=button_bgcolor, color=button_textcolor)
    no_button = ElevatedButton(text="Нет", on_click=on_no_click, expand=True, bgcolor=button_bgcolor, color=button_textcolor)

    Content = Column((header, question_text, word_text, translation_text),
                     alignment=alignment, horizontal_alignment="center", spacing=50)
    buttons = Row((yes_button, no_button), alignment="center", spacing=50)
    page.add(
        Column(
            [Content, buttons],
            horizontal_alignment="center",
            expand=True,
            spacing=70
        )
    )
    display_word()

ft.app(target=main, view=None, port=8000)
