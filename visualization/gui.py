import tkinter as tk
from tkinter import ttk

def show_highlighted_text(text1, text2, added, removed, lev_dist, cos_dist):
    """Отображает тексты с выделенными изменениями в графическом интерфейсе"""
    root = tk.Tk()
    root.title("Сравнение текстов")

    window_width = 925
    window_height = 550
    root.geometry(f"{window_width}x{window_height}")
    root.resizable(False, False)

    # Центрирование окна
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)

    # Текст 1
    ttk.Label(frame, text="Текст 1:", font='Arial 15').grid(row=0, column=0, sticky=tk.W)
    text_widget1 = tk.Text(frame, wrap=tk.WORD, height=20, width=40, font='Arial 14')
    text_widget1.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=5)
    text_widget1.insert(tk.END, text1)

    # Текст 2
    ttk.Label(frame, text="Текст 2:", font='Arial 15').grid(row=0, column=1, sticky=tk.W)
    text_widget2 = tk.Text(frame, wrap=tk.WORD, height=20, width=40, font='Arial 14')
    text_widget2.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
    text_widget2.insert(tk.END, text2)

    text_widget1.tag_configure("removed_tag", foreground="red")
    text_widget2.tag_configure("added_tag", foreground="green")

    def highlight_word(text_widget, word, start_index, tag):
        """Выделяет слово в текстовом виджете с учётом переносов строк."""
        lines = text_widget.get("1.0", tk.END).split("\n")
        current_index = 0

        for line_num, line in enumerate(lines, start=1):
            if current_index + len(line) >= start_index:
                # Находим позицию слова в текущей строке
                column = start_index - current_index
                start_pos = f"{line_num}.{column}"
                end_pos = f"{line_num}.{column + len(word)}"
                text_widget.tag_add(tag, start_pos, end_pos)
                break
            current_index += len(line) + 1  # +1 для учёта символа переноса строки

    for word, start_index in removed:
        highlight_word(text_widget1, word, start_index, "removed_tag")

    for word, start_index in added:
        highlight_word(text_widget2, word, start_index, "added_tag")

    metrics_frame = ttk.Frame(frame, padding="10")
    metrics_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))

    ttk.Label(metrics_frame, text="Метрика Левенштейна:", font='Arial 12').grid(row=0, column=0, sticky=tk.W)
    levenshtein_label = ttk.Label(metrics_frame, text=str(lev_dist), font='Arial 12')
    levenshtein_label.grid(row=0, column=1, sticky=tk.W)

    ttk.Label(metrics_frame, text="Косинусное расстояние:", font='Arial 12').grid(row=1, column=0, sticky=tk.W)
    cosine_label = ttk.Label(metrics_frame, text=str(cos_dist), font='Arial 12')
    cosine_label.grid(row=1, column=1, sticky=tk.W)

    root.mainloop()