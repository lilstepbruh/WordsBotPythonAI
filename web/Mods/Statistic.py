import flet as ft
from flet import Page, Column, Container, Text, DataTable, DataColumn, DataCell, DataRow, ScrollMode
import sqlite3
import json

def get_words_from_db():
    conn = sqlite3.connect(r'/\words.db')
    cursor = conn.cursor()
    cursor.execute("SELECT word, translation, status FROM words")
    words = cursor.fetchall()
    conn.close()
    return words

def get_sentences_count():
    try:
        with open('translate.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return len(data.get('sentences', []))
    except FileNotFoundError:
        return 0

def main(page: Page):
    page.title = "WORDS"
    header = Text(value="WORDS", size=24, weight="bold", italic=True, text_align="center")

    words = get_words_from_db()
    num_words = len(words)
    num_sentences = get_sentences_count()

    profile_button = Container(
        content=Column(
            [
                Text(value="Профиль", size=18, weight="bold"),
                Text(value=f"Предложений: {num_sentences}", size=18),
                Text(value=f"Слов: {num_words}", size=18),
            ],

            spacing=5,
            alignment=ft.alignment.center,
        ),
        padding=10,
        border_radius=8,
        ink=True,
        on_click=lambda e: print("Профиль clicked"),
        width=400,
        margin=5
    )

    buttons = Column(
        [profile_button],
        spacing=10,
        alignment=ft.alignment.center,
        width=400
    )

    table = DataTable(
        columns=[
            DataColumn(label=Text("Слово")),
            DataColumn(label=Text("Перевод")),
            DataColumn(label=Text("Статус"))
        ],
        rows=[DataRow(cells=[
            DataCell(Text(word[0])),
            DataCell(Text(word[1])),
            DataCell(Text("Изучил" if word[2] == 'learned' else "Учу"))
        ]) for word in words],

    )

    table_container = Container(
        border_radius=8,
        content=Column([table], scroll=ScrollMode.AUTO),
        width=600,
        height=500,
    )

    page.add(
        Column(
            [header, buttons, table_container],
            alignment=ft.alignment.center,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
            spacing=20
        )
    )


ft.app(target=main, view=None,port=8000)