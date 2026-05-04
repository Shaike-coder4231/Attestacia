import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime

class TaskGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator")
        self.root.geometry("600x500")
        self.root.resizable(True, True)

        # Предопределённые задачи
        self.tasks_db = {
            "учеба": [
                "Прочитать статью по Python",
                "Решить 5 задач по математике",
                "Выучить 10 новых слов на английском",
                "Посмотреть лекцию по истории"
            ],
            "спорт": [
                "Сделать зарядку (15 минут)",
                "Пробежка 30 минут",
                "Отжимания и приседания",
                "Поход в спортзал"
            ],
            "работа": [
                "Написать отчёт о проекте",
                "Ответить на рабочие письма",
                "Составить план на неделю",
                "Изучить новый инструмент"
            ]
        }

        self.history_file = "tasks_history.json"
        self.history = []
        self.load_history()

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        title_label = ttk.Label(main_frame, text="🎲 Генератор случайных задач",
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)

        self.generate_btn = ttk.Button(main_frame, text="🎯 Сгенерировать задачу",
                                       command=self.generate_task)
        self.generate_btn.grid(row=1, column=0, columnspan=3, pady=10)

        self.current_task_label = ttk.Label(main_frame, text="Нажмите кнопку для генерации",
                                            font=("Arial", 12), wraplength=500)
        self.current_task_label.grid(row=2, column=0, columnspan=3, pady=10)

        ttk.Separator(main_frame, orient='horizontal').grid(row=3, column=0, columnspan=3, sticky="ew", pady=10)

        filter_frame = ttk.LabelFrame(main_frame, text="Фильтрация истории", padding="5")
        filter_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=5)

        ttk.Label(filter_frame, text="Тип задачи:").grid(row=0, column=0, padx=5)
        self.filter_type = tk.StringVar(value="все")
        self.filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_type,
                                         values=["все", "учеба", "спорт", "работа"], state="readonly")
        self.filter_combo.grid(row=0, column=1, padx=5)
        self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self.update_history_display())

        ttk.Button(filter_frame, text="Применить фильтр",
                   command=self.update_history_display).grid(row=0, column=2, padx=5)

        add_frame = ttk.LabelFrame(main_frame, text="Добавить новую задачу", padding="5")
        add_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=5)

        ttk.Label(add_frame, text="Тип:").grid(row=0, column=0, padx=5)
        self.new_type = ttk.Combobox(add_frame, values=["учеба", "спорт", "работа"], state="readonly", width=10)
        self.new_type.grid(row=0, column=1, padx=5)
        self.new_type.set("учеба")

        ttk.Label(add_frame, text="Задача:").grid(row=0, column=2, padx=5)
        self.new_task_entry = ttk.Entry(add_frame, width=30)
        self.new_task_entry.grid(row=0, column=3, padx=5)

        ttk.Button(add_frame, text="➕ Добавить", command=self.add_new_task).grid(row=0, column=4, padx=5)

        history_frame = ttk.LabelFrame(main_frame, text="История сгенерированных задач", padding="5")
        history_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)

        scrollbar = ttk.Scrollbar(history_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_listbox = tk.Listbox(history_frame, height=12, yscrollcommand=scrollbar.set)
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_listbox.yview)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=7, column=0, columnspan=3, pady=5)

        ttk.Button(btn_frame, text="🗑 Очистить историю", command=self.clear_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💾 Сохранить историю", command=self.save_history).pack(side=tk.LEFT, padx=5)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)

        self.update_history_display()

    def generate_task(self):
        """Генерирует случайную задачу из выбранной категории"""
        all_tasks = []
        task_category = None

        if self.filter_type.get() != "все":
            category = self.filter_type.get()
            if category in self.tasks_db and self.tasks_db[category]:
                all_tasks = [(task, category) for task in self.tasks_db[category]]
        else:
            for category, tasks in self.tasks_db.items():
                for task in tasks:
                    all_tasks.append((task, category))

        if not all_tasks:
            messagebox.showwarning("Нет задач", f"В категории '{self.filter_type.get()}' нет задач!")
            return

        selected_task, category = random.choice(all_tasks)

        self.current_task_label.config(text=f"✨ {selected_task} ✨")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history_entry = {
            "timestamp": timestamp,
            "task": selected_task,
            "category": category
        }
        self.history.append(history_entry)
        self.save_history()
        self.update_history_display()

    def update_history_display(self):
        """Обновляет отображение истории с учётом фильтра"""
        self.history_listbox.delete(0, tk.END)

        filter_value = self.filter_type.get()

        for entry in reversed(self.history):  # Показываем последние вверху
            if filter_value == "все" or entry["category"] == filter_value:
                display_text = f"[{entry['timestamp']}] [{entry['category'].upper()}] {entry['task']}"
                self.history_listbox.insert(tk.END, display_text)

    def add_new_task(self):
        """Добавляет новую задачу в базу"""
        task_text = self.new_task_entry.get().strip()
        task_type = self.new_type.get()

        if not task_text:
            messagebox.showerror("Ошибка", "Задача не может быть пустой строкой!")
            return

        if task_type not in self.tasks_db:
            self.tasks_db[task_type] = []

        self.tasks_db[task_type].append(task_text)
        self.new_task_entry.delete(0, tk.END)
        messagebox.showinfo("Успех", f"Задача '{task_text}' добавлена в категорию '{task_type}'")

    def clear_history(self):
        """Очищает историю задач"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history.clear()
            self.save_history()
            self.update_history_display()
            messagebox.showinfo("Очищено", "История успешно очищена")

    def save_history(self):
        """Сохраняет историю в JSON файл"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")

    def load_history(self):
        """Загружает историю из JSON файла"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except Exception as e:
                self.history = []
                print(f"Ошибка загрузки истории: {e}")
        else:
            self.history = []

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskGenerator(root)
    root.mainloop()
