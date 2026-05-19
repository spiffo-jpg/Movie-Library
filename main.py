"""
Movie Library (Личная кинотека)
GUI-приложение для хранения информации о фильмах с фильтрацией
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# Переменная с ссылкой на GitHub (укажите свой репозиторий)
git_hub = "https://github.com/spiffo-jpg/movie-library"

# Файл для хранения данных
DATA_FILE = "movies.json"

# Список жанров для выпадающего списка
GENRES = ["Боевик", "Комедия", "Драма", "Фантастика", "Ужасы", "Романтика", "Триллер", "Детектив"]


class MovieLibrary:
    """Основной класс приложения для управления фильмотекой"""

    def __init__(self, root):
        self.root = root
        self.root.title(" Movie Library - Личная кинотека")
        self.root.geometry("800x600")
        self.root.configure(bg="#1a1a2e")

        # Загрузка данных
        self.movies = self.load_movies()

        # Текущие фильтры
        self.filter_genre = "Все"
        self.filter_year = ""

        # Создание интерфейса
        self.create_widgets()
        self.update_movie_table()

    # Работа с файлами 
    def load_movies(self):
        """Загрузка списка фильмов из JSON файла"""
        if not os.path.exists(DATA_FILE):
            return []
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                movies = json.load(f)
                return movies if isinstance(movies, list) else []
        except (json.JSONDecodeError, IOError):
            return []

    def save_movies(self):
        """Сохранение списка фильмов в JSON файл"""
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.movies, f, ensure_ascii=False, indent=4)
        except IOError:
            messagebox.showerror("Ошибка", "Не удалось сохранить данные")

    # Проверка корректности ввода
    def validate_input(self):
        """Проверка корректности введённых данных"""
        title = self.title_entry.get().strip()
        genre = self.genre_var.get()
        year = self.year_entry.get().strip()
        rating = self.rating_entry.get().strip()

        # Проверка названия
        if not title:
            messagebox.showwarning("Ошибка", "Введите название фильма")
            return None

        # Проверка жанра
        if not genre or genre == "Выберите жанр":
            messagebox.showwarning("Ошибка", "Выберите жанр фильма")
            return None

        # Проверка года
        if not year:
            messagebox.showwarning("Ошибка", "Введите год выпуска")
            return None
        try:
            year = int(year)
            if year < 1888 or year > 2026:
                messagebox.showwarning("Ошибка", "Год должен быть от 1888 до 2026")
                return None
        except ValueError:
            messagebox.showwarning("Ошибка", "Год должен быть числом")
            return None

        # Проверка рейтинга
        if not rating:
            messagebox.showwarning("Ошибка", "Введите рейтинг")
            return None
        try:
            rating = float(rating)
            if rating < 0 or rating > 10:
                messagebox.showwarning("Ошибка", "Рейтинг должен быть от 0 до 10")
                return None
        except ValueError:
            messagebox.showwarning("Ошибка", "Рейтинг должен быть числом")
            return None

        return {"title": title, "genre": genre, "year": year, "rating": rating}

    # Добавление фильма 
    def add_movie(self):
        """Добавление нового фильма в библиотеку"""
        movie = self.validate_input()
        if movie:
            self.movies.append(movie)
            self.save_movies()
            self.update_movie_table()
            self.clear_input_fields()
            messagebox.showinfo("Успех", f"Фильм '{movie['title']}' добавлен!")

    def clear_input_fields(self):
        """Очистка полей ввода"""
        self.title_entry.delete(0, tk.END)
        self.genre_var.set("Выберите жанр")
        self.year_entry.delete(0, tk.END)
        self.rating_entry.delete(0, tk.END)

    # Удаление фильма
    def delete_movie(self):
        """Удаление выбранного фильма"""
        selected = self.movie_table.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите фильм для удаления")
            return

        if messagebox.askyesno("Подтверждение", "Удалить выбранный фильм?"):
            # Получаем индекс выбранной строки
            item = selected[0]
            values = self.movie_table.item(item, "values")
            
            # Находим фильм в списке и удаляем
            for i, movie in enumerate(self.movies):
                if (movie["title"] == values[0] and 
                    movie["genre"] == values[1] and 
                    str(movie["year"]) == values[2] and 
                    str(movie["rating"]) == values[3]):
                    self.movies.pop(i)
                    break
            
            self.save_movies()
            self.update_movie_table()

    # Отображение таблицы 
    def update_movie_table(self):
        """Обновление таблицы с фильмами (с учётом фильтров)"""
        # Очищаем таблицу
        for item in self.movie_table.get_children():
            self.movie_table.delete(item)

        # Фильтруем фильмы
        filtered_movies = self.apply_filters()

        # Добавляем отфильтрованные фильмы
        for movie in filtered_movies:
            self.movie_table.insert("", tk.END, values=(
                movie["title"],
                movie["genre"],
                movie["year"],
                f"{movie['rating']:.1f}" if isinstance(movie['rating'], float) else str(movie['rating'])
            ))

        # Обновляем счётчик
        self.count_label.config(text=f"Всего фильмов: {len(self.movies)} | Показано: {len(filtered_movies)}")

    def apply_filters(self):
        """Применение фильтров к списку фильмов"""
        filtered = self.movies.copy()

        # Фильтр по жанру
        if self.filter_genre != "Все":
            filtered = [m for m in filtered if m["genre"] == self.filter_genre]

        # Фильтр по году
        if self.filter_year:
            try:
                year_filter = int(self.filter_year)
                filtered = [m for m in filtered if m["year"] == year_filter]
            except ValueError:
                pass

        return filtered

    # Фильтрация 
    def apply_genre_filter(self, event=None):
        """Применение фильтра по жанру"""
        self.filter_genre = self.genre_filter_var.get()
        self.update_movie_table()

    def apply_year_filter(self):
        """Применение фильтра по году"""
        year = self.year_filter_entry.get().strip()
        if year:
            try:
                year_int = int(year)
                if year_int < 1888 or year_int > 2026:
                    messagebox.showwarning("Ошибка", "Введите корректный год (1888-2026)")
                    self.year_filter_entry.delete(0, tk.END)
                    return
                self.filter_year = year
            except ValueError:
                messagebox.showwarning("Ошибка", "Год должен быть числом")
                self.year_filter_entry.delete(0, tk.END)
                return
        else:
            self.filter_year = ""
        self.update_movie_table()

    def clear_filters(self):
        """Очистка всех фильтров"""
        self.genre_filter_var.set("Все")
        self.year_filter_entry.delete(0, tk.END)
        self.filter_genre = "Все"
        self.filter_year = ""
        self.update_movie_table()

    # Создание интерфейса
    def create_widgets(self):
        # Заголовок
        title_label = tk.Label(
            self.root, 
            text=" Movie Library - Личная кинотека ",
            font=("Arial", 18, "bold"),
            bg="#1a1a2e",
            fg="#e94560"
        )
        title_label.pack(pady=15)

        # Форма добавления фильма 
        form_frame = tk.LabelFrame(
            self.root, 
            text=" Добавить новый фильм",
            font=("Arial", 12, "bold"),
            bg="#16213e",
            fg="#e2e2e2"
        )
        form_frame.pack(pady=10, padx=20, fill="x")

        # Поле Название
        tk.Label(form_frame, text="Название:", bg="#16213e", fg="#e2e2e2", font=("Arial", 10)).grid(
            row=0, column=0, padx=10, pady=5, sticky="e"
        )
        self.title_entry = tk.Entry(form_frame, width=30, font=("Arial", 10))
        self.title_entry.grid(row=0, column=1, padx=10, pady=5)

        # Поле Жанр
        tk.Label(form_frame, text="Жанр:", bg="#16213e", fg="#e2e2e2", font=("Arial", 10)).grid(
            row=0, column=2, padx=10, pady=5, sticky="e"
        )
        self.genre_var = tk.StringVar(value="Выберите жанр")
        self.genre_combo = ttk.Combobox(
            form_frame, 
            textvariable=self.genre_var, 
            values=GENRES, 
            state="readonly", 
            width=15
        )
        self.genre_combo.grid(row=0, column=3, padx=10, pady=5)

        # Поле Год
        tk.Label(form_frame, text="Год:", bg="#16213e", fg="#e2e2e2", font=("Arial", 10)).grid(
            row=1, column=0, padx=10, pady=5, sticky="e"
        )
        self.year_entry = tk.Entry(form_frame, width=10, font=("Arial", 10))
        self.year_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Поле Рейтинг
        tk.Label(form_frame, text="Рейтинг (0-10):", bg="#16213e", fg="#e2e2e2", font=("Arial", 10)).grid(
            row=1, column=2, padx=10, pady=5, sticky="e"
        )
        self.rating_entry = tk.Entry(form_frame, width=10, font=("Arial", 10))
        self.rating_entry.grid(row=1, column=3, padx=10, pady=5, sticky="w")

        # Кнопка добавления
        add_btn = tk.Button(
            form_frame, 
            text=" Добавить фильм",
            command=self.add_movie,
            bg="#0f3460",
            fg="#e94560",
            font=("Arial", 10, "bold"),
            cursor="hand2"
        )
        add_btn.grid(row=2, column=0, columnspan=4, pady=10)

        #  Панель фильтрации 
        filter_frame = tk.LabelFrame(
            self.root, 
            text=" Фильтрация",
            font=("Arial", 12, "bold"),
            bg="#16213e",
            fg="#e2e2e2"
        )
        filter_frame.pack(pady=10, padx=20, fill="x")

        # Фильтр по жанру
        tk.Label(filter_frame, text="По жанру:", bg="#16213e", fg="#e2e2e2").grid(
            row=0, column=0, padx=10, pady=5
        )
        self.genre_filter_var = tk.StringVar(value="Все")
        genre_filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.genre_filter_var,
            values=["Все"] + GENRES,
            state="readonly",
            width=15
        )
        genre_filter_combo.grid(row=0, column=1, padx=10, pady=5)
        genre_filter_combo.bind("<<ComboboxSelected>>", self.apply_genre_filter)

        # Фильтр по году
        tk.Label(filter_frame, text="По году:", bg="#16213e", fg="#e2e2e2").grid(
            row=0, column=2, padx=10, pady=5
        )
        self.year_filter_entry = tk.Entry(filter_frame, width=10, font=("Arial", 10))
        self.year_filter_entry.grid(row=0, column=3, padx=10, pady=5)

        apply_year_btn = tk.Button(
            filter_frame,
            text="Применить",
            command=self.apply_year_filter,
            bg="#2980b9",
            fg="white",
            font=("Arial", 9),
            cursor="hand2"
        )
        apply_year_btn.grid(row=0, column=4, padx=5, pady=5)

        # Кнопка очистки фильтров
        clear_filter_btn = tk.Button(
            filter_frame,
            text="Сбросить фильтры",
            command=self.clear_filters,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 9),
            cursor="hand2"
        )
        clear_filter_btn.grid(row=0, column=5, padx=10, pady=5)

        # Таблица с фильмами 
        table_frame = tk.LabelFrame(
            self.root, 
            text=" Список фильмов",
            font=("Arial", 12, "bold"),
            bg="#16213e",
            fg="#e2e2e2"
        )
        table_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Создание таблицы Treeview
        columns = ("Название", "Жанр", "Год", "Рейтинг")
        self.movie_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        # Настройка заголовков
        for col in columns:
            self.movie_table.heading(col, text=col)
            self.movie_table.column(col, width=150, anchor="center")

        # Добавление скроллбара
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.movie_table.yview)
        self.movie_table.configure(yscrollcommand=scrollbar.set)

        self.movie_table.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        # Кнопка удаления и счётчик 
        bottom_frame = tk.Frame(self.root, bg="#1a1a2e")
        bottom_frame.pack(pady=10, fill="x")

        delete_btn = tk.Button(
            bottom_frame,
            text=" Удалить выбранный фильм",
            command=self.delete_movie,
            bg="#c0392b",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2"
        )
        delete_btn.pack(side=tk.LEFT, padx=20)

        self.count_label = tk.Label(
            bottom_frame, 
            text="Всего фильмов: 0", 
            bg="#1a1a2e", 
            fg="#e2e2e2",
            font=("Arial", 10)
        )
        self.count_label.pack(side=tk.RIGHT, padx=20)

        # GitHub ссылка
        github_label = tk.Label(
            self.root, 
            text=f" GitHub: {git_hub}", 
            font=("Arial", 8), 
            bg="#1a1a2e", 
            fg="#7f8c8d"
        )
        github_label.pack(side=tk.BOTTOM, pady=5)


def main():
    root = tk.Tk()
    app = MovieLibrary(root)
    root.mainloop()


if __name__ == "__main__":
    main()