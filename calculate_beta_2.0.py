import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Клас Товару 
class ProductItem:
    def __init__(self, name, price, var_cost, quantity):
        self.name = name
        self.p = float(price)
        self.v = float(var_cost)
        self.q = float(quantity)

    @property
    def revenue(self): return self.p * self.q
    @property
    def var_cost_total(self): return self.v * self.q
    @property
    def contribution(self): return (self.p - self.v) * self.q
    
    def to_dict(self):
        return {
            "Назва": self.name,
            "Ціна (p)": self.p,
            "Собівартість (v)": self.v,
            "Продажі план (q)": self.q,
            "Дохід (Revenue)": self.revenue,
            "Маржа (Margin)": self.contribution
        }

# Головний Клас Програми 
class BusinessCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Бізнес-Калькулятор PRO: Гнучкі витрати + Smart Аналітика")
        self.root.geometry("1200x850")

        style = ttk.Style()
        style.theme_use('clam')

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text=' 1. Фінанси та Витрати ')
        
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text=' 2. Оптимізація ціни (Графік) ')

        self.products = []
        self.expenses = [] # Список для збереження витрат
        
        self.setup_finance_tab()
        self.setup_optimizer_tab()

    def setup_finance_tab(self):
        # ЛІВА ПАНЕЛЬ (Введення даних)
        frame_left = ttk.Frame(self.tab1)
        frame_left.pack(side="left", fill="y", padx=10, pady=5)

        # 1. Блок ПОСТІЙНІ ВИТРАТИ 
        frame_fixed = ttk.LabelFrame(frame_left, text="Крок 1. Постійні витрати (Fixed Costs)", padding=10)
        frame_fixed.pack(fill="x", pady=5)

        ttk.Label(frame_fixed, text="Назва витрати (напр. Оренда):").grid(row=0, column=0, sticky="w")
        self.ent_exp_name = ttk.Entry(frame_fixed, width=20)
        self.ent_exp_name.grid(row=1, column=0, pady=2, sticky="ew")

        ttk.Label(frame_fixed, text="Сума (грн):").grid(row=0, column=1, sticky="w")
        self.ent_exp_amount = ttk.Entry(frame_fixed, width=10)
        self.ent_exp_amount.grid(row=1, column=1, pady=2, padx=5, sticky="ew")

        btn_add_exp = ttk.Button(frame_fixed, text="Додати витрату (+)", command=self.add_expense)
        btn_add_exp.grid(row=1, column=2, padx=2)

        # Таблиця витрат
        columns_exp = ("name", "amount")
        self.tree_exp = ttk.Treeview(frame_fixed, columns=columns_exp, show="headings", height=6)
        self.tree_exp.heading("name", text="Категорія")
        self.tree_exp.heading("amount", text="Сума")
        self.tree_exp.column("name", width=120)
        self.tree_exp.column("amount", width=80)
        self.tree_exp.grid(row=2, column=0, columnspan=3, pady=5)

        btn_del_exp = ttk.Button(frame_fixed, text="Видалити витрату (-)", command=self.delete_expense)
        btn_del_exp.grid(row=3, column=0, columnspan=3, sticky="ew")

        self.lbl_fixed_total = ttk.Label(frame_fixed, text="Всього постійних витрат: 0 грн", font=("Arial", 10, "bold"), foreground="#d9534f")
        self.lbl_fixed_total.grid(row=4, column=0, columnspan=3, pady=5)

        # 2. Блок ДОДАВАННЯ ТОВАРУ
        frame_add = ttk.LabelFrame(frame_left, text="Крок 2. Товари та Послуги", padding=10)
        frame_add.pack(fill="x", pady=5)

        ttk.Label(frame_add, text="Назва товару:").grid(row=0, column=0, sticky="w")
        self.ent_name = ttk.Entry(frame_add, width=25)
        self.ent_name.grid(row=0, column=1, pady=2)

        ttk.Label(frame_add, text="Ціна продажу (p):").grid(row=1, column=0, sticky="w")
        self.ent_price = ttk.Entry(frame_add, width=25)
        self.ent_price.grid(row=1, column=1, pady=2)

        ttk.Label(frame_add, text="Собівартість (v):").grid(row=2, column=0, sticky="w")
        self.ent_vcost = ttk.Entry(frame_add, width=25)
        self.ent_vcost.grid(row=2, column=1, pady=2)

        ttk.Label(frame_add, text="План продажів (шт):").grid(row=3, column=0, sticky="w")
        self.ent_qty = ttk.Entry(frame_add, width=25)
        self.ent_qty.grid(row=3, column=1, pady=2)

        ttk.Button(frame_add, text="Додати товар у список", command=self.add_product).grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")

        # ПРАВА ПАНЕЛЬ (Таблиця та Результати) 
        frame_right = ttk.Frame(self.tab1)
        frame_right.pack(side="right", fill="both", expand=True, padx=10, pady=5)

        # 3. Таблиця Товарів
        columns = ("name", "p", "v", "q", "revenue", "cm")
        self.tree = ttk.Treeview(frame_right, columns=columns, show="headings", height=10)
        
        headers = ["Товар", "Ціна", "Собівартість", "К-сть", "Дохід", "Маржа (Прибуток з товару)"]
        widths = [120, 80, 80, 60, 100, 120]
        
        for col, h, w in zip(columns, headers, widths):
            self.tree.heading(col, text=h)
            self.tree.column(col, width=w, anchor="center")
        
        self.tree.pack(fill="both", expand=True)

        # Кнопки керування
        frame_btns = ttk.Frame(frame_right)
        frame_btns.pack(fill="x", pady=5)
        ttk.Button(frame_btns, text="Видалити вибраний товар", command=self.delete_selected_product).pack(side="right", padx=5)
        ttk.Button(frame_btns, text="Очистити все", command=self.clear_all).pack(side="right")
        ttk.Button(frame_btns, text="💾 Експорт звіту в Excel", command=self.export_to_excel).pack(side="left")

        # 4. Підсумки та Аналітика
        frame_res = ttk.LabelFrame(frame_right, text="Фінансова Аналітика", padding=15)
        frame_res.pack(fill="x", pady=10)

        # Колонка цифр
        f_nums = ttk.Frame(frame_res)
        f_nums.pack(side="left", fill="y", padx=10)

        self.lbl_total_rev = ttk.Label(f_nums, text="Загальний дохід (Оборот): 0.00 грн", font=("Arial", 11))
        self.lbl_total_rev.pack(anchor="w", pady=2)

        self.lbl_total_margin = ttk.Label(f_nums, text="Загальна маржа: 0.00 грн", font=("Arial", 11))
        self.lbl_total_margin.pack(anchor="w", pady=2)

        self.lbl_profit = ttk.Label(f_nums, text="ЧИСТИЙ ПРИБУТОК: 0.00 грн", font=("Arial", 14, "bold"))
        self.lbl_profit.pack(anchor="w", pady=10)

        ttk.Separator(frame_res, orient='vertical').pack(side="left", fill="y", padx=20)

        # Колонка ТБ 
        f_be = ttk.Frame(frame_res)
        f_be.pack(side="left", fill="y")

        self.lbl_be_money = ttk.Label(f_be, text="Поріг окупності (Точка беззбитковості): -", font=("Arial", 10, "bold"))
        self.lbl_be_money.pack(anchor="w", pady=5)

        self.lbl_safety = ttk.Label(f_be, text="Запас міцності: -", font=("Arial", 10))
        self.lbl_safety.pack(anchor="w", pady=2)
        
        self.lbl_be_status = ttk.Label(f_be, text="", font=("Arial", 9, "italic"), foreground="grey")
        self.lbl_be_status.pack(anchor="w", pady=2)


    # Логіка Витрат
    def add_expense(self):
        name = self.ent_exp_name.get()
        amount_str = self.ent_exp_amount.get()

        if not name or not amount_str:
            messagebox.showwarning("Увага", "Введіть назву та суму витрати")
            return
        
        try:
            amount = float(amount_str)
            self.expenses.append({"name": name, "amount": amount})
            self.tree_exp.insert("", "end", values=(name, f"{amount:.2f}"))
            
            # Очистка
            self.ent_exp_name.delete(0, 'end')
            self.ent_exp_amount.delete(0, 'end')
            
            self.recalculate_finance()
        except ValueError:
            messagebox.showerror("Помилка", "Сума має бути числом")

    def delete_expense(self):
        selected = self.tree_exp.selection()
        if not selected: return
        
        for item in selected:
            idx = self.tree_exp.index(item)
            del self.expenses[idx]
            self.tree_exp.delete(item)
        
        self.recalculate_finance()

    def get_fixed_costs_total(self):
        return sum(item["amount"] for item in self.expenses)


    # Логіка Товарів 
    def add_product(self):
        try:
            name = self.ent_name.get()
            p = float(self.ent_price.get())
            v = float(self.ent_vcost.get())
            q = float(self.ent_qty.get())
            if not name: raise ValueError
            
            item = ProductItem(name, p, v, q)
            self.products.append(item)
            self.tree.insert("", "end", values=(name, p, v, q, f"{item.revenue:.2f}", f"{item.contribution:.2f}"))

            self.update_optimizer_combobox()
            self.recalculate_finance()
            
            # Очищення полів
            self.ent_name.delete(0, 'end')
            self.ent_price.delete(0, 'end')
            self.ent_vcost.delete(0, 'end')
            self.ent_qty.delete(0, 'end')
            
        except ValueError:
            messagebox.showerror("Помилка", "Перевірте введені дані. Ціни мають бути числами.")

    def delete_selected_product(self):
        for item in self.tree.selection():
            idx = self.tree.index(item)
            del self.products[idx]
            self.tree.delete(item)
        self.update_optimizer_combobox()
        self.recalculate_finance()

    def clear_all(self):
        self.products = []
        self.tree.delete(*self.tree.get_children())
        self.update_optimizer_combobox()
        self.recalculate_finance()


    # ГОЛОВНИЙ ПЕРЕРАХУНОК 
    def recalculate_finance(self):
        fixed_total = self.get_fixed_costs_total()
        self.lbl_fixed_total.config(text=f"Всього постійних витрат: {fixed_total:,.2f} грн")

        total_rev = sum(x.revenue for x in self.products)
        total_cm = sum(x.contribution for x in self.products)
        profit = total_cm - fixed_total
        
        self.lbl_total_rev.config(text=f"Загальний дохід (Оборот): {total_rev:,.2f} грн")
        self.lbl_total_margin.config(text=f"Загальна маржа: {total_cm:,.2f} грн")
        
        color = "green" if profit > 0 else "red"
        self.lbl_profit.config(text=f"ЧИСТИЙ ПРИБУТОК: {profit:,.2f} грн", foreground=color)
        
        # Аналітика Точки Беззбитковості
        if total_cm > 0 and total_rev > 0:
            margin_ratio = total_cm / total_rev # Коефіцієнт маржинального доходу
            be_revenue = fixed_total / margin_ratio # Формула ТБ в грошах
            
            self.lbl_be_money.config(text=f"Поріг окупності (Точка беззбитковості): {be_revenue:,.2f} грн")

            if total_rev > be_revenue:
                # Ми в плюсі
                safety_margin = total_rev - be_revenue
                safety_percent = (safety_margin / total_rev) * 100
                self.lbl_safety.config(text=f"Запас міцності: {safety_percent:.1f}%", foreground="green")
                self.lbl_be_status.config(text=f"(На стільки можуть впасти продажі, перш ніж ви отримаєте збиток)")
            else:
                # Ми в мінусі або нулі
                needed = be_revenue - total_rev
                self.lbl_safety.config(text="Зона збитків", foreground="red")
                self.lbl_be_status.config(text=f"(Треба продати ще на {needed:,.2f} грн, щоб вийти в нуль)")
        
        elif total_cm <= 0:
             self.lbl_be_money.config(text="Неможливо розрахувати (Маржа від'ємна)")
             self.lbl_safety.config(text="-")
             self.lbl_be_status.config(text="Ви продаєте в мінус на кожній одиниці")
        else:
            self.lbl_be_money.config(text="-")
            self.lbl_safety.config(text="-")
            self.lbl_be_status.config(text="")

    def export_to_excel(self):
        if not self.products:
            messagebox.showinfo("Інфо", "Спочатку додайте товари.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not file_path: return

        try:
            # 1. Товари
            data_prod = [p.to_dict() for p in self.products]
            df_prod = pd.DataFrame(data_prod)
            
            # Підсумки
            fixed_total = self.get_fixed_costs_total()
            total_rev = df_prod["Дохід (Revenue)"].sum()
            total_cm = df_prod["Маржа (Margin)"].sum()
            profit = total_cm - fixed_total

            # 2. Витрати
            df_fixed = pd.DataFrame(self.expenses)
            if not df_fixed.empty:
                df_fixed.columns = ["Категорія витрат", "Сума"]
                # Додаємо рядок суми
                df_fixed.loc[len(df_fixed)] = ["ВСЬОГО ВИТРАТ", fixed_total]

            # 3. Звіт
            summary_data = [
                {"Показник": "Загальний Дохід", "Значення": total_rev},
                {"Показник": "Загальні Постійні Витрати", "Значення": fixed_total},
                {"Показник": "Валовий прибуток (Маржа)", "Значення": total_cm},
                {"Показник": "ЧИСТИЙ ПРИБУТОК", "Значення": profit}
            ]
            df_summary = pd.DataFrame(summary_data)

            with pd.ExcelWriter(file_path) as writer:
                df_prod.to_excel(writer, sheet_name="Товари", index=False)
                if not df_fixed.empty:
                    df_fixed.to_excel(writer, sheet_name="Витрати", index=False)
                df_summary.to_excel(writer, sheet_name="Загальний Звіт", index=False)

            messagebox.showinfo("Успіх", f"Звіт збережено!")

        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося зберегти: {e}")


    # Вкладка Оптимізації 
    def setup_optimizer_tab(self):
        frame_top = ttk.Frame(self.tab2)
        frame_top.pack(side="top", fill="x", padx=10, pady=10)

        # Інструкція
        lbl_instr = ttk.Label(frame_top, text="Тут ви можете визначити ідеальну ціну. Введіть два реальні сценарії (наприклад, поточний та експериментальний).\nМатематична модель покаже, де знаходиться пік прибутку.", 
                              background="#e1e1e1", padding=5, justify="center")
        lbl_instr.pack(fill="x", pady=5)

        # Вибір товару
        ttk.Label(frame_top, text="Оберіть товар для аналізу:").pack(anchor="w")
        self.combo_products = ttk.Combobox(frame_top, state="readonly", width=40)
        self.combo_products.pack(anchor="w", pady=5)
        self.combo_products.bind("<<ComboboxSelected>>", self.on_product_select)

        # Контейнер для вводу даних
        frame_input = ttk.LabelFrame(self.tab2, text="Введення даних для моделювання", padding=10)
        frame_input.pack(side="left", fill="y", padx=10, anchor="n")

        ttk.Label(frame_input, text="Собівартість (v):").grid(row=0, column=0, pady=5, sticky="e")
        self.opt_v = ttk.Entry(frame_input, width=12)
        self.opt_v.grid(row=0, column=1)

        ttk.Separator(frame_input, orient='horizontal').grid(row=1, column=0, columnspan=2, sticky='ew', pady=10)

        # Сценарій 1
        ttk.Label(frame_input, text="Сценарій 1 (Поточний)", font=("Arial", 9, "bold")).grid(row=2, column=0, columnspan=2, sticky="w")
        
        ttk.Label(frame_input, text="Ціна (p1):").grid(row=3, column=0, sticky="e")
        self.opt_p1 = ttk.Entry(frame_input, width=12)
        self.opt_p1.grid(row=3, column=1, pady=2)
        
        ttk.Label(frame_input, text="Продажі (q1):").grid(row=4, column=0, sticky="e")
        self.opt_q1 = ttk.Entry(frame_input, width=12)
        self.opt_q1.grid(row=4, column=1, pady=2)

        ttk.Separator(frame_input, orient='horizontal').grid(row=5, column=0, columnspan=2, sticky='ew', pady=10)

        # Сценарій 2
        ttk.Label(frame_input, text="Сценарій 2 (Змінений)", font=("Arial", 9, "bold")).grid(row=6, column=0, columnspan=2, sticky="w")
        ttk.Label(frame_input, text="Якщо ціна буде...").grid(row=7, column=0, columnspan=2, sticky="w", padx=5)

        ttk.Label(frame_input, text="Ціна (p2):").grid(row=8, column=0, sticky="e")
        self.opt_p2 = ttk.Entry(frame_input, width=12)
        self.opt_p2.grid(row=8, column=1, pady=2)
        
        ttk.Label(frame_input, text="Тоді продажі будуть (q2):").grid(row=9, column=0, sticky="e")
        self.opt_q2 = ttk.Entry(frame_input, width=12)
        self.opt_q2.grid(row=9, column=1, pady=2)

        ttk.Button(frame_input, text="Розрахувати Оптимум 🚀", command=self.calculate_optimum).grid(row=10, column=0, columnspan=2, pady=15, sticky="ew")

        # Лейбл для результатів 
        self.lbl_opt_res = ttk.Label(frame_input, text="", justify="left", font=("Arial", 10), wraplength=220)
        self.lbl_opt_res.grid(row=11, column=0, columnspan=2)

        # Графік
        self.frame_plot = ttk.Frame(self.tab2, relief="sunken")
        self.frame_plot.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    def update_optimizer_combobox(self):
        names = [p.name for p in self.products]
        self.combo_products['values'] = names

    def on_product_select(self, event):
        idx = self.combo_products.current()
        if idx >= 0:
            item = self.products[idx]
            self.opt_v.delete(0, 'end')
            self.opt_v.insert(0, str(item.v))
            # Автозаповнення першого сценарію
            self.opt_p1.delete(0, 'end')
            self.opt_p1.insert(0, str(item.p))
            self.opt_q1.delete(0, 'end')
            self.opt_q1.insert(0, str(item.q))
            # Другий залишаємо пустим або чистимо
            self.opt_p2.delete(0, 'end')
            self.opt_q2.delete(0, 'end')
            self.lbl_opt_res.config(text="")

    def calculate_optimum(self):
        try:
            p1_str, q1_str = self.opt_p1.get(), self.opt_q1.get()
            p2_str, q2_str = self.opt_p2.get(), self.opt_q2.get()
            v_str = self.opt_v.get()

            if not all([p1_str, q1_str, p2_str, q2_str, v_str]):
                messagebox.showerror("Помилка", "Будь ласка, заповніть усі поля для обох сценаріїв.")
                return

            p1, q1 = float(p1_str), float(q1_str)
            p2, q2 = float(p2_str), float(q2_str)
            v = float(v_str)

            if p1 == p2:
                messagebox.showerror("Помилка логіки", "Ціна в сценарії 1 та 2 має відрізнятись, щоб ми побачили залежність.")
                return

            # Розрахунок нахилу кривої попиту
            slope = (q2 - q1) / (p2 - p1)
            
            if slope >= 0:
                reason = "Ви вказали, що при вищій ціні продажі ростуть (або не змінюються)."
                advice = "Закон попиту: коли ціна росте, продажі мають падати. Перевірте дані."
                messagebox.showerror("Помилка економічної моделі", f"{reason}\n\n{advice}")
                self.lbl_opt_res.config(text="Помилка: Невірні дані попиту", foreground="red")
                return

            B = -slope
            A = q1 + B * p1
            
            # Оптимальна ціна
            p_opt = (A + B * v) / (2 * B)
            q_opt = A - B * p_opt 
            profit_opt = (p_opt - v) * q_opt

            res_text = (
                f"✅ Оптимальна ціна:\n   {p_opt:.2f} грн\n\n"
                f"📦 Прогноз продажів:\n   {q_opt:.1f} шт.\n\n"
                f"💰 Макс. прибуток:\n   {profit_opt:.2f} грн"
            )
            self.lbl_opt_res.config(text=res_text, foreground="black")
            
            self.plot_graph(A, B, v, p_opt, profit_opt, q_opt)

        except ValueError:
            messagebox.showerror("Помилка формату", "Перевірте, чи всюди введені числа (використовуйте крапку для дробових).")

    def plot_graph(self, A, B, v, p_opt, max_profit, q_opt):
        for widget in self.frame_plot.winfo_children():
            widget.destroy()

        # Діапазон цін для графіка
        p_max_demand = A / B
        prices = np.linspace(v * 0.8, p_max_demand * 0.9, 100)
        demand = A - B * prices
        profits = (prices - v) * demand

        fig, ax1 = plt.subplots(figsize=(5, 4), dpi=100)
        
        # Вісь прибутку
        color_profit = 'tab:green'
        ax1.set_xlabel('Ціна (грн)')
        ax1.set_ylabel('Прибуток (грн)', color=color_profit, fontweight='bold')
        ax1.plot(prices, profits, color=color_profit, linewidth=2, label="Прибуток")
        ax1.tick_params(axis='y', labelcolor=color_profit)
        ax1.fill_between(prices, profits, 0, color=color_profit, alpha=0.1) # Заливка
        
        # Лінія оптимуму
        ax1.axvline(x=p_opt, color='black', linestyle='--', alpha=0.7)
        ax1.text(p_opt, max(profits)*0.95, f" Оптимум: {p_opt:.0f} грн", color='black', fontsize=9, fontweight='bold')

        # Вісь попиту
        ax2 = ax1.twinx()
        color_demand = 'tab:blue'
        ax2.set_ylabel('Кількість продажів (шт)', color=color_demand)
        ax2.plot(prices, demand, color=color_demand, linestyle=':', label="Попит")
        ax2.tick_params(axis='y', labelcolor=color_demand)
        
        fig.tight_layout()
        plt.title("Пошук максимального прибутку")
        ax1.grid(True, alpha=0.3)

        canvas = FigureCanvasTkAgg(fig, master=self.frame_plot)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

import sqlite3
import urllib.request
import json
import sys
import ctypes

try:
    import sv_ttk 
    HAS_SV_TTK = True
except ImportError:
    HAS_SV_TTK = False

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.widget.bind("<Enter>", self.showtip)
        self.widget.bind("<Leave>", self.hidetip)

    def showtip(self, event=None):
        if self.tipwindow or not self.text: return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 30
        y = y + cy + self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#2B2D42", foreground="#FFFFFF", relief=tk.SOLID, borderwidth=0,
                         font=("Segoe UI Variable", 9), padx=8, pady=6)
        label.pack()

    def hidetip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw: tw.destroy()

class AdvancedBusinessCalculatorApp(BusinessCalculatorApp):
    def __init__(self, root):
        self.conn = sqlite3.connect("business_data.db")
        self.create_tables()
        self.editing_idx = None
        self.editing_exp_idx = None 
        
        self.apply_modern_window_effects(root)

        super().__init__(root)
        
        self.root.title("Додаток для моделювання бізнес-процесів та автоматизації розрахунків")
        self.notebook.tab(self.tab2, text=' 2. Візуалізація оптимізації ціни ')

        self.setup_monte_carlo_tab()

        if HAS_SV_TTK:
            sv_ttk.set_theme("dark")
            self.root.option_add("*font", ("Segoe UI Variable", 10))
        
        self.current_currency = "UAH"
        self.currency_symbol = "₴"
        self.rates = self.fetch_live_rates()
        self.setup_advanced_ui()
        self.load_from_db()
        
        self.root.after(50, self.update_dynamic_labels)
        self.root.after(50, self.apply_custom_colors)

    def fmt(self, value, dec=2):
        """Внутрішня функція для форматування великих чисел: 100 000 замість 100,000"""
        if dec == 0:
            return f"{value:,.0f}".replace(",", " ")
        elif dec == 1:
            return f"{value:,.1f}".replace(",", " ")
        else:
            return f"{value:,.2f}".replace(",", " ")

    def setup_monte_carlo_tab(self):
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text=' 🎲 3. Аналіз ризиків (Монте-Карло) ')

        frame_top = ttk.Frame(self.tab3)
        frame_top.pack(side="top", fill="x", padx=10, pady=10)

        instr = ("Метод Монте-Карло використовує Нормальний розподіл Гаусса для моделювання випадкових сценаріїв продажів.\n"
                 "Це дозволяє математично оцінити реальний ризик збитків та дізнатись найбільш ймовірний фінансовий результат.")
        ttk.Label(frame_top, text=instr, padding=5, justify="center", font=("Segoe UI Variable", 10, "italic")).pack(fill="x", pady=5)

        frame_controls = ttk.LabelFrame(self.tab3, text="Параметри моделі", padding=10)
        frame_controls.pack(side="left", fill="y", padx=10, anchor="n")

        ttk.Label(frame_controls, text="Кількість ітерацій (N):").pack(anchor="w", pady=(0, 5))
        self.ent_mc_iter = ttk.Entry(frame_controls, width=15)
        self.ent_mc_iter.insert(0, "10000") 
        self.ent_mc_iter.pack(anchor="w", pady=(0, 5))
        
        # Пояснення про 10 000 ітерацій
        explanation = "ℹ Чому 10 000? Це ідеальний баланс між точністю\n(Закон великих чисел) та швидкістю. Ліміти: 100 - 1 000 000."
        ttk.Label(frame_controls, text=explanation, font=("Segoe UI Variable", 8, "italic"), foreground="gray").pack(anchor="w", pady=(0, 15))
        ToolTip(self.ent_mc_iter, "Скільки випадкових сценаріїв згенерує програма.\nБільше число = точніший результат, але довший розрахунок.")

        ttk.Label(frame_controls, text="Можливе відхилення продажів (%):").pack(anchor="w", pady=(0, 5))
        self.ent_mc_dev = ttk.Entry(frame_controls, width=15)
        self.ent_mc_dev.insert(0, "20") 
        self.ent_mc_dev.pack(anchor="w", pady=(0, 15))
        ToolTip(self.ent_mc_dev, "Стандартне відхилення (σ). Наскільки сильно\nпродажі можуть відрізнятися від вашого плану в гіршу або кращу сторону.")

        self.btn_run_mc = ttk.Button(frame_controls, text="Запустити симуляцію", command=self.run_monte_carlo)
        self.btn_run_mc.pack(fill="x", pady=10)

        ttk.Separator(frame_controls, orient='horizontal').pack(fill='x', pady=15)

        # ДОДАНО: Іконки ⓘ від самого початку роботи програми на 3 вкладці
        self.lbl_mc_mean = ttk.Label(frame_controls, text="Очікуваний прибуток: - ⓘ", font=("Segoe UI Variable", 10, "bold"))
        self.lbl_mc_mean.pack(anchor="w", pady=5)
        ToolTip(self.lbl_mc_mean, "Математичне очікування (найбільш ймовірний результат).")

        self.lbl_mc_loss = ttk.Label(frame_controls, text="Ризик збитку: - ⓘ", font=("Segoe UI Variable", 11, "bold"), foreground="#FF5252")
        self.lbl_mc_loss.pack(anchor="w", pady=5)
        ToolTip(self.lbl_mc_loss, "Ймовірність того, що ви не покриєте фіксовані витрати.")

        self.lbl_mc_p95 = ttk.Label(frame_controls, text="Оптимістичний (95%): - ⓘ", foreground="#00E676")
        self.lbl_mc_p95.pack(anchor="w", pady=5)
        ToolTip(self.lbl_mc_p95, "З ймовірністю 95% ваш прибуток не перевищить цю суму (найкращий сценарій).")

        self.lbl_mc_p05 = ttk.Label(frame_controls, text="Песимістичний (5%): - ⓘ")
        self.lbl_mc_p05.pack(anchor="w", pady=5)
        ToolTip(self.lbl_mc_p05, "З ймовірністю 95% ваш прибуток буде більшим за цю суму (найгірший сценарій).")

        self.mc_plot_frame = ttk.Frame(self.tab3, relief="sunken")
        self.mc_plot_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        self.mc_placeholder = ttk.Label(self.mc_plot_frame, text="⬅️ Введіть параметри та натисніть 'Запустити симуляцію',\nщоб побудувати графік та розрахувати математичні ризики.", justify="center", font=("Segoe UI Variable", 12))
        self.mc_placeholder.pack(expand=True)

    def run_monte_carlo(self):
        if not self.products:
            messagebox.showinfo("Інфо", "Для симуляції додайте хоча б один товар.")
            return
        
        try:
            dev_percent = float(self.ent_mc_dev.get()) / 100.0
            n_iter = int(self.ent_mc_iter.get())
            if n_iter < 100 or n_iter > 1000000 or dev_percent < 0: raise ValueError
        except ValueError:
            messagebox.showerror("Помилка", "Перевірте введені дані. Відхилення має бути >= 0, а ітерації від 100 до 1 000 000.")
            return
            
        rate = self.rates[self.current_currency]
        fixed_costs = self.get_fixed_costs_total() / rate
        
        profits_sim = np.full(n_iter, -fixed_costs)
        
        for p in self.products:
            q_mean = p.q
            q_std = q_mean * dev_percent
            q_sim = np.random.normal(q_mean, q_std, n_iter)
            q_sim = np.maximum(q_sim, 0) 
            
            margin = (p.p - p.v) / rate
            profits_sim += q_sim * margin
            
        mean_profit = np.mean(profits_sim)
        prob_loss = np.mean(profits_sim < 0) * 100
        p05 = np.percentile(profits_sim, 5) 
        p95 = np.percentile(profits_sim, 95) 
        
        sym = self.currency_symbol
        self.lbl_mc_mean.config(text=f"Очікуваний прибуток: {self.fmt(mean_profit, 0)} {sym} ⓘ")
        self.lbl_mc_loss.config(text=f"Ризик збитку: {self.fmt(prob_loss, 1)}% ⓘ")
        self.lbl_mc_p05.config(text=f"Песимістичний (5%): {self.fmt(p05, 0)} {sym} ⓘ")
        self.lbl_mc_p95.config(text=f"Оптимістичний (95%): {self.fmt(p95, 0)} {sym} ⓘ")
        
        for widget in self.mc_plot_frame.winfo_children():
            widget.destroy()
            
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        ax.hist(profits_sim, bins=50, color='#818CF8', alpha=0.8, edgecolor='black', linewidth=0.5)
        ax.axvline(0, color='#FF5252', linestyle='dashed', linewidth=2, label='Точка збитку (0)')
        ax.axvline(mean_profit, color='#00E676', linestyle='dashed', linewidth=2, label='Очікуваний прибуток')
        
        ax.set_title(f"Розподіл ймовірностей прибутку ({self.fmt(n_iter, 0)} ітерацій)", fontweight='bold')
        ax.set_xlabel(f"Чистий прибуток ({sym})")
        ax.set_ylabel("Частота сценаріїв")
        ax.legend()
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.mc_plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_dynamic_labels(self):
        sym = self.currency_symbol
        
        new_instr = ("💡 Аналіз та візуалізація ціноутворення.\n"
                     "Введіть поточні показники і спрогнозуйте можливий сценарій їх зміни.\n"
                     "Математична модель побудує графік попиту та знайде ідеальну ціну для максимального прибутку.")
        for widget in self.tab2.winfo_children():
            if isinstance(widget, ttk.Frame):
                for subwidget in widget.winfo_children():
                    if isinstance(subwidget, ttk.Label) and ("ідеальну ціну" in str(subwidget.cget("text")) or "Аналіз та" in str(subwidget.cget("text"))):
                        subwidget.configure(text=new_instr, background="")

        for widget in self.opt_v.master.winfo_children():
            if isinstance(widget, ttk.Label):
                txt = str(widget.cget("text"))
                if "Собівартість" in txt:
                    widget.configure(text=f"Собівартість ({sym}) ⓘ:")
                elif "Ціна (p1)" in txt or "Поточна ціна" in txt: 
                    widget.configure(text=f"Поточна ціна ({sym}) ⓘ:")
                elif "Продажі (q1)" in txt or "Поточні продажі" in txt: 
                    widget.configure(text=f"Поточні продажі (од.) ⓘ:")
                elif "Ціна (p2)" in txt or "Нова ціна" in txt: 
                    widget.configure(text=f"Нова ціна ({sym}) ⓘ:")
                elif "Тоді продажі" in txt or "Очікувані продажі" in txt: 
                    widget.configure(text=f"Очікувані продажі (од.) ⓘ:")
                
        for widget in self.ent_name.master.winfo_children():
            if isinstance(widget, ttk.Label):
                txt = str(widget.cget("text"))
                if "Ціна продажу" in txt: widget.configure(text=f"Ціна продажу ({sym}):")
                elif "Собівартість" in txt: widget.configure(text=f"Собівартість ({sym}):")
                elif "План продажів" in txt: widget.configure(text=f"План продажів (од.):")

        for widget in self.ent_exp_amount.master.winfo_children():
            if isinstance(widget, ttk.Label) and "Сума" in widget.cget("text"):
                widget.configure(text=f"Сума ({sym}):")
                
        self.refresh_tree()
        self.refresh_tree_exp()

    def toggle_theme_safe(self):
        if HAS_SV_TTK:
            sv_ttk.toggle_theme()
            self.root.after(100, self.apply_custom_colors)
            self.root.after(100, self.update_dynamic_labels)

    def apply_custom_colors(self):
        style = ttk.Style()
        
        style.configure("CustomText.TButton", font=("Segoe UI Variable", 9, "bold"))
        style.configure("CustomText.TButton", foreground="#818CF8")
        style.map("CustomText.TButton", 
                  foreground=[
                      ("disabled", "#a3a3a3"),
                      ("pressed", "#4F46E5"), 
                      ("active", "#6366F1"), 
                      ("!disabled", "#818CF8")
                  ])
        
        def make_solid_btn(widget, command, text, pady=4):
            parent = widget.master
            manager = widget.winfo_manager()
            
            new_btn = tk.Button(parent, text=text, command=command,
                                bg="#818CF8", fg="white", 
                                activebackground="#6366F1", activeforeground="white",
                                relief="flat", font=("Segoe UI Variable", 9, "bold"), 
                                cursor="hand2", padx=10, pady=pady)
            
            if manager == "grid":
                info = widget.grid_info()
                new_btn.grid(row=info['row'], column=info['column'], 
                             rowspan=info.get('rowspan', 1), columnspan=info.get('columnspan', 1),
                             padx=info.get('padx', 0), pady=info.get('pady', 0), 
                             sticky=info.get('sticky', ''))
            elif manager == "pack":
                info = widget.pack_info()
                new_btn.pack(side=info.get('side', 'top'), fill=info.get('fill', 'none'),
                             expand=info.get('expand', 0), padx=info.get('padx', 0), 
                             pady=info.get('pady', 0), anchor=info.get('anchor', 'center'))
            
            widget.destroy()
            return new_btn

        def walk_and_style(widget):
            for child in list(widget.winfo_children()):
                if isinstance(child, ttk.Button):
                    text = str(child.cget("text"))
                    
                    if "Додати витрату" in text:
                        self.btn_add_exp_ref = make_solid_btn(child, self.add_expense, text)
                    elif "Додати товар у список" in text:
                        self.btn_add_product = make_solid_btn(child, self.add_product, text, pady=6)
                    elif "Розрахувати Оптимум" in text:
                        make_solid_btn(child, self.calculate_optimum, text, pady=6)
                    elif "Запустити симуляцію" in text:
                        make_solid_btn(child, self.run_monte_carlo, text, pady=6)
                        
                    elif any(word in text for word in ["Видалити витрату", "Очистити все", "Видалити вибраний", "Редагувати вибране", "Експорт звіту", "Редагувати витрату"]):
                        child.configure(style="CustomText.TButton")
                else:
                    walk_and_style(child)
                    
        walk_and_style(self.root)
        
        if not hasattr(self, 'btn_add_product'):
            self.btn_add_product = self.ent_name.master.winfo_children()[-1]

    def add_expense(self):
        name = self.ent_exp_name.get()
        amount_str = self.ent_exp_amount.get()

        if not name or not amount_str:
            messagebox.showwarning("Увага", "Введіть назву та суму витрати")
            return
        try:
            rate = self.rates[self.current_currency]
            amount = float(amount_str) * rate 
            # Захист від від'ємних витрат або нуля
            if amount <= 0: raise ValueError
            
            self.expenses.append({"name": name, "amount": amount})
            self.refresh_tree_exp()
            self.recalculate_finance()
            self.save_all_to_db()
            self.ent_exp_name.delete(0, 'end')
            self.ent_exp_amount.delete(0, 'end')
        except ValueError:
            messagebox.showerror("Помилка", "Сума витрати має бути додатним числом (>0)")

    def add_product(self):
        try:
            name = self.ent_name.get()
            rate = self.rates[self.current_currency]
            p = float(self.ent_price.get()) * rate 
            v = float(self.ent_vcost.get()) * rate
            q = float(self.ent_qty.get())
            
            # ДОДАНО: Захист від від'ємних значень
            if not name or p <= 0 or v < 0 or q <= 0: raise ValueError
            
            item = ProductItem(name, p, v, q)
            self.products.append(item)

            self.update_optimizer_combobox()
            self.refresh_tree()
            self.recalculate_finance()
            self.save_all_to_db()
            
            self.ent_name.delete(0, 'end')
            self.ent_price.delete(0, 'end')
            self.ent_vcost.delete(0, 'end')
            self.ent_qty.delete(0, 'end')
        except ValueError:
            messagebox.showerror("Помилка", "Перевірте дані: Ціна та Кількість мають бути > 0, Собівартість >= 0.")

    def on_product_select(self, event):
        idx = self.combo_products.current()
        if idx >= 0:
            item = self.products[idx]
            rate = self.rates[self.current_currency]
            self.opt_v.delete(0, 'end')
            self.opt_v.insert(0, str(round(item.v / rate, 2)))
            self.opt_p1.delete(0, 'end')
            self.opt_p1.insert(0, str(round(item.p / rate, 2)))
            self.opt_q1.delete(0, 'end')
            self.opt_q1.insert(0, str(item.q))
            self.opt_p2.delete(0, 'end')
            self.opt_q2.delete(0, 'end')
            self.lbl_opt_res.config(text="")

    def calculate_optimum(self):
        try:
            p1_str, q1_str = self.opt_p1.get(), self.opt_q1.get()
            p2_str, q2_str = self.opt_p2.get(), self.opt_q2.get()
            v_str = self.opt_v.get()

            if not all([p1_str, q1_str, p2_str, q2_str, v_str]):
                messagebox.showerror("Помилка", "Будь ласка, заповніть усі поля для обох сценаріїв.")
                return

            p1, q1 = float(p1_str), float(q1_str)
            p2, q2 = float(p2_str), float(q2_str)
            v = float(v_str)

            # ДОДАНО: Логічний захист даних
            if p1 <= 0 or p2 <= 0 or q1 < 0 or q2 < 0 or v < 0:
                messagebox.showerror("Помилка логіки", "Ціна має бути > 0. Кількість і собівартість >= 0.")
                return

            if p1 == p2:
                messagebox.showerror("Помилка логіки", "Ціна в сценарії 1 та 2 має відрізнятись, щоб ми побачили залежність.")
                return

            slope = (q2 - q1) / (p2 - p1)
            
            if slope >= 0:
                messagebox.showerror("Помилка економічної моделі", "Закон попиту: коли ціна росте, продажі мають падати. Перевірте дані.")
                self.lbl_opt_res.config(text="Помилка: Невірні дані попиту", foreground="#FF5252")
                return

            B = -slope
            A = q1 + B * p1
            
            p_opt = (A + B * v) / (2 * B)
            q_opt = A - B * p_opt 
            profit_opt = (p_opt - v) * q_opt
            
            profits_upper_opt = (p_opt - v) * (q_opt * 1.15)
            profits_lower_opt = (p_opt - v) * (q_opt * 0.85)

            sym = self.currency_symbol
            res_text = (
                f"✅ Оптимальна ціна:\n   {self.fmt(p_opt)} {sym}\n\n"
                f"📦 Прогноз продажів:\n   {self.fmt(q_opt, 1)} од.\n\n"
                f"💰 Макс. прибуток:\n   {self.fmt(profit_opt)} {sym}\n\n"
                f"📊 Довірчий інтервал прибутку (±15% попиту):\n   від {self.fmt(profits_lower_opt)} до {self.fmt(profits_upper_opt)} {sym}"
            )
            self.lbl_opt_res.config(text=res_text, foreground="")
            
            self.plot_graph(A, B, v, p_opt, profit_opt, q_opt)

        except ValueError:
            messagebox.showerror("Помилка формату", "Перевірте, чи всюди введені числа (використовуйте крапку для дробових).")

    def plot_graph(self, A, B, v, p_opt, max_profit, q_opt):
        for widget in self.frame_plot.winfo_children():
            widget.destroy()

        p_max_demand = A / B
        prices = np.linspace(v * 0.8, p_max_demand * 0.9, 100)
        demand = A - B * prices
        profits = (prices - v) * demand

        demand_upper = demand * 1.15
        demand_lower = demand * 0.85
        profits_upper = (prices - v) * demand_upper
        profits_lower = (prices - v) * demand_lower

        fig, ax1 = plt.subplots(figsize=(5, 4), dpi=100)
        
        color_profit = 'tab:green'
        sym = self.currency_symbol
        
        ax1.set_xlabel(f'Ціна ({sym})')
        ax1.set_ylabel(f'Прибуток ({sym})', color=color_profit, fontweight='bold')
        
        ax1.fill_between(prices, profits_lower, profits_upper, color='gray', alpha=0.2, label="Довірчий інтервал (±15%)")
        ax1.plot(prices, profits, color=color_profit, linewidth=2, label="Прогнозний Прибуток")
        
        ax1.tick_params(axis='y', labelcolor=color_profit)
        
        ax1.axvline(x=p_opt, color='black', linestyle='--', alpha=0.7)
        ax1.text(p_opt, max(profits)*0.95, f" Оптимум: {self.fmt(p_opt, 0)} {sym}", color='black', fontsize=9, fontweight='bold')

        ax2 = ax1.twinx()
        color_demand = 'tab:blue'
        ax2.set_ylabel('Кількість продажів (одиниці)', color=color_demand)
        ax2.plot(prices, demand, color=color_demand, linestyle=':', label="Попит")
        ax2.tick_params(axis='y', labelcolor=color_demand)
        
        ax1.legend(loc='upper left', fontsize=8)
        fig.tight_layout()
        plt.title("Пошук максимального прибутку з оцінкою ризиків")
        ax1.grid(True, alpha=0.3)

        canvas = FigureCanvasTkAgg(fig, master=self.frame_plot)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def apply_modern_window_effects(self, root):
        if sys.platform == "win32":
            try:
                root.update_idletasks() 
                hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 33, ctypes.byref(ctypes.c_int(2)), 4)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(ctypes.c_int(1)), 4)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 38, ctypes.byref(ctypes.c_int(2)), 4)
            except Exception:
                pass 

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS products 
                          (id INTEGER PRIMARY KEY, name TEXT, p REAL, v REAL, q REAL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS expenses 
                          (id INTEGER PRIMARY KEY, name TEXT, amount REAL)''')
        self.conn.commit()

    def save_all_to_db(self):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM products")
        cursor.execute("DELETE FROM expenses")
        for p in self.products:
            cursor.execute("INSERT INTO products (name, p, v, q) VALUES (?, ?, ?, ?)", (p.name, p.p, p.v, p.q))
        for e in self.expenses:
            cursor.execute("INSERT INTO expenses (name, amount) VALUES (?, ?)", (e["name"], e["amount"]))
        self.conn.commit()

    def load_from_db(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, p, v, q FROM products")
        for row in cursor.fetchall():
            item = ProductItem(row[0], row[1], row[2], row[3])
            self.products.append(item)
            
        cursor.execute("SELECT name, amount FROM expenses")
        for row in cursor.fetchall():
            self.expenses.append({"name": row[0], "amount": row[1]})
            
        self.update_optimizer_combobox()
        self.recalculate_finance()

    def delete_expense(self):
        super().delete_expense()
        self.refresh_tree_exp()
        self.save_all_to_db()

    def delete_selected_product(self):
        super().delete_selected_product()
        self.refresh_tree()
        self.save_all_to_db()

    def clear_all(self):
        super().clear_all()
        self.refresh_tree_exp()
        self.save_all_to_db()

    def refresh_tree_exp(self):
        self.tree_exp.delete(*self.tree_exp.get_children())
        sym = self.currency_symbol
        rate = self.rates[self.current_currency]
        for item in self.expenses:
            self.tree_exp.insert("", "end", values=(item["name"], f"{self.fmt(item['amount'] / rate)} {sym}"))

    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        sym = self.currency_symbol
        rate = self.rates[self.current_currency]
        for item in self.products:
            self.tree.insert("", "end", values=(item.name, f"{self.fmt(item.p / rate)} {sym}", f"{self.fmt(item.v / rate)} {sym}", f"{self.fmt(item.q, 0)} од.", f"{self.fmt(item.revenue / rate)} {sym}", f"{self.fmt(item.contribution / rate)} {sym}"))

    def fetch_live_rates(self):
        rates = {"UAH": 1.0, "USD": 40.0, "EUR": 43.0}
        try:
            req = urllib.request.Request("https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5")
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode('utf-8'))
                for item in data:
                    if item['ccy'] == 'USD': rates['USD'] = float(item['sale'])
                    if item['ccy'] == 'EUR': rates['EUR'] = float(item['sale'])
        except Exception:
            pass
        return rates

    def setup_advanced_ui(self):
        top_bar = ttk.Frame(self.root, padding=10)
        top_bar.pack(side="top", fill="x", before=self.notebook)

        lbl_curr = ttk.Label(top_bar, text="🌎 Валюта для фінансової аналітики:", font=('Segoe UI Variable', 11, 'bold'))
        lbl_curr.pack(side="left", padx=10)

        self.curr_var = tk.StringVar(value="UAH")
        curr_combo = ttk.Combobox(top_bar, textvariable=self.curr_var, values=["UAH", "USD", "EUR"], state="readonly", width=8)
        curr_combo.pack(side="left")
        curr_combo.bind("<<ComboboxSelected>>", self.change_currency)

        if HAS_SV_TTK:
            self.btn_theme = ttk.Button(top_bar, text="🌓 Змінити тему", command=self.toggle_theme_safe)
            self.btn_theme.pack(side="right", padx=10)

        frame_fixed = self.ent_exp_amount.master
        for child in list(frame_fixed.winfo_children()):
            if isinstance(child, ttk.Button) and "Видалити витрату" in str(child.cget("text")):
                child.destroy()
                
        self.frame_exp_btns = ttk.Frame(frame_fixed)
        self.frame_exp_btns.grid(row=3, column=0, columnspan=3, pady=5, sticky="ew")
        
        ttk.Button(self.frame_exp_btns, text="Видалити витрату", command=self.delete_expense).pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(self.frame_exp_btns, text="Редагувати витрату", command=self.prepare_edit_expense).pack(side="right", expand=True, fill="x", padx=2)

        self.btn_save_exp_edit = ttk.Button(frame_fixed, text="✅ Зберегти", command=self.finalize_edit_expense, style="Accent.TButton")

        frame_btns = self.tree.master.winfo_children()[-2]
        ttk.Button(frame_btns, text="✏️ Редагувати вибране", command=self.prepare_edit).pack(side="right", padx=5)
        self.btn_save_edit = ttk.Button(self.ent_qty.master, text="✅ Зберегти зміни", command=self.finalize_edit, style="Accent.TButton")

        f_advanced = ttk.Frame(self.lbl_profit.master.master)
        f_advanced.pack(side="left", fill="y", padx=20)
        ttk.Separator(self.lbl_profit.master.master, orient='vertical').pack(side="left", fill="y", before=f_advanced)

        self.lbl_roi = ttk.Label(f_advanced, text="📈 ROI (Рентабельність): - ⓘ", font=("Segoe UI Variable", 11, "bold"))
        self.lbl_roi.pack(anchor="w", pady=5)
        
        self.lbl_op_lev = ttk.Label(f_advanced, text="⚙️ Операційний важіль: - ⓘ", font=("Segoe UI Variable", 11))
        self.lbl_op_lev.pack(anchor="w", pady=2)
        
        ToolTip(self.lbl_fixed_total, "Сума всіх постійних витрат (напр. оренда, інтернет),\nякі ви повинні сплатити незалежно від кількості продажів.")
        ToolTip(self.lbl_total_rev, "Загальний дохід (Оборот):\nУсі гроші, отримані від продажу товарів або послуг,\nдо вирахування будь-яких витрат.")
        ToolTip(self.lbl_total_margin, "Загальна маржа (Валовий прибуток):\nДохід мінус собівартість товарів. Показує, скільки\nгрошей залишається на покриття постійних витрат.")
        ToolTip(self.lbl_profit, "Чистий прибуток:\nВаш кінцевий фінансовий результат на руки.\nЗагальна маржа мінус усі постійні витрати.")
        ToolTip(self.lbl_be_money, "Поріг окупності (Точка беззбитковості):\nМінімальна сума грошей, на яку треба продати товарів, щоб вийти в нуль\n(повністю покрити всі витрати, але ще не отримати прибуток).")
        ToolTip(self.lbl_safety, "Запас міцності:\nПоказує, на скільки відсотків можуть впасти ваші поточні\nпродажі, перш ніж бізнес почне зазнавати збитків.")
        ToolTip(self.lbl_roi, "ROI (Коефіцієнт рентабельності):\nПоказує ефективність. Скільки відсотків прибутку\nприносить кожна вкладена у фіксовані витрати гривня.")
        ToolTip(self.lbl_op_lev, "Операційний важіль:\nПоказує, на скільки відсотків зміниться ваш прибуток,\nякщо ваша виручка збільшиться рівно на 1%.")
        
        for widget in self.opt_v.master.winfo_children():
            if isinstance(widget, ttk.Label):
                txt = str(widget.cget("text"))
                if "Собівартість" in txt: ToolTip(widget, "Всі витрати на виготовлення або закупівлю 1 одиниці товару.")
                elif "Ціна (p1)" in txt or "Поточна ціна" in txt: ToolTip(widget, "Поточна ціна, за якою ви продаєте товар зараз.")
                elif "Продажі (q1)" in txt or "Поточні продажі" in txt: ToolTip(widget, "Кількість продажів, яку ви робите за поточною ціною.")
                elif "Ціна (p2)" in txt or "Нова ціна" in txt: ToolTip(widget, "Нова, експериментальна ціна для перевірки вашої гіпотези.")
                elif "Тоді продажі" in txt or "Очікувані продажі" in txt: ToolTip(widget, "Ваш прогноз: скільки ви продасте, якщо встановите нову ціну.")

    def prepare_edit_expense(self):
        selected = self.tree_exp.selection()
        if not selected:
            messagebox.showinfo("Інфо", "Оберіть витрату у таблиці для редагування.")
            return
        
        item_id = selected[0]
        self.editing_exp_idx = self.tree_exp.index(item_id)
        expense = self.expenses[self.editing_exp_idx]
        rate = self.rates[self.current_currency]

        self.ent_exp_name.delete(0, 'end')
        self.ent_exp_name.insert(0, expense["name"])
        self.ent_exp_amount.delete(0, 'end')
        self.ent_exp_amount.insert(0, str(round(expense["amount"] / rate, 2))) 

        if hasattr(self, 'btn_add_exp_ref'):
            self.btn_add_exp_ref.grid_remove()
        self.btn_save_exp_edit.grid(row=1, column=2, padx=4)

    def finalize_edit_expense(self):
        try:
            name = self.ent_exp_name.get()
            rate = self.rates[self.current_currency]
            amount = float(self.ent_exp_amount.get()) * rate
            if not name or amount <= 0: raise ValueError

            self.expenses[self.editing_exp_idx] = {"name": name, "amount": amount}
            
            self.refresh_tree_exp()
            self.recalculate_finance()
            self.save_all_to_db()

            self.ent_exp_name.delete(0, 'end')
            self.ent_exp_amount.delete(0, 'end')
            
            self.btn_save_exp_edit.grid_remove()
            if hasattr(self, 'btn_add_exp_ref'):
                self.btn_add_exp_ref.grid()
            
            self.editing_exp_idx = None

        except ValueError:
            messagebox.showerror("Помилка", "Перевірте дані. Назва не може бути пустою, а сума має бути > 0.")

    def prepare_edit(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Інфо", "Оберіть товар у таблиці для редагування.")
            return
        
        item_id = selected[0]
        self.editing_idx = self.tree.index(item_id)
        product = self.products[self.editing_idx]
        rate = self.rates[self.current_currency]

        self.ent_name.delete(0, 'end')
        self.ent_name.insert(0, product.name)
        self.ent_price.delete(0, 'end')
        self.ent_price.insert(0, str(round(product.p / rate, 2)))
        self.ent_vcost.delete(0, 'end')
        self.ent_vcost.insert(0, str(round(product.v / rate, 2)))
        self.ent_qty.delete(0, 'end')
        self.ent_qty.insert(0, str(product.q))

        self.btn_add_product.grid_remove()
        self.btn_save_edit.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")

    def finalize_edit(self):
        try:
            name = self.ent_name.get()
            rate = self.rates[self.current_currency]
            p = float(self.ent_price.get()) * rate
            v = float(self.ent_vcost.get()) * rate
            q = float(self.ent_qty.get())
            if not name or p <= 0 or v < 0 or q <= 0: raise ValueError

            self.products[self.editing_idx] = ProductItem(name, p, v, q)
            
            self.refresh_tree()
            self.recalculate_finance()
            self.save_all_to_db()

            self.ent_name.delete(0, 'end')
            self.ent_price.delete(0, 'end')
            self.ent_vcost.delete(0, 'end')
            self.ent_qty.delete(0, 'end')
            
            self.btn_save_edit.grid_remove()
            self.btn_add_product.grid()
            
            self.editing_idx = None
            self.update_optimizer_combobox()

        except ValueError:
            messagebox.showerror("Помилка", "Перевірте дані: Ціна та Кількість мають бути > 0, Собівартість >= 0.")

    def export_to_excel(self):
        if not self.products:
            messagebox.showinfo("Інфо", "Спочатку додайте товари.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not file_path: return

        try:
            rate = self.rates[self.current_currency]
            sym = self.currency_symbol
            
            data_prod = []
            for p in self.products:
                data_prod.append({
                    "Назва": p.name,
                    f"Ціна ({sym})": round(p.p / rate, 2),
                    f"Собівартість ({sym})": round(p.v / rate, 2),
                    "Продажі план (од.)": p.q,
                    f"Дохід ({sym})": round(p.revenue / rate, 2),
                    f"Маржа ({sym})": round(p.contribution / rate, 2)
                })
            df_prod = pd.DataFrame(data_prod)
            
            fixed_total = self.get_fixed_costs_total() / rate
            total_rev = sum(p.revenue for p in self.products) / rate
            total_cm = sum(p.contribution for p in self.products) / rate
            profit = total_cm - fixed_total

            data_exp = [{"Категорія витрат": e["name"], f"Сума ({sym})": round(e["amount"] / rate, 2)} for e in self.expenses]
            df_fixed = pd.DataFrame(data_exp)
            if not df_fixed.empty:
                df_fixed.loc[len(df_fixed)] = ["ВСЬОГО ВИТРАТ", round(fixed_total, 2)]

            summary_data = [
                {"Показник": "Загальний Дохід", f"Значення ({sym})": round(total_rev, 2)},
                {"Показник": "Загальні Постійні Витрати", f"Значення ({sym})": round(fixed_total, 2)},
                {"Показник": "Валовий прибуток (Маржа)", f"Значення ({sym})": round(total_cm, 2)},
                {"Показник": "ЧИСТИЙ ПРИБУТОК", f"Значення ({sym})": round(profit, 2)}
            ]
            df_summary = pd.DataFrame(summary_data)

            with pd.ExcelWriter(file_path) as writer:
                df_prod.to_excel(writer, sheet_name="Товари", index=False)
                if not df_fixed.empty:
                    df_fixed.to_excel(writer, sheet_name="Витрати", index=False)
                df_summary.to_excel(writer, sheet_name="Загальний Звіт", index=False)

            messagebox.showinfo("Успіх", f"Звіт збережено!")

        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося зберегти: {e}")

    def change_currency(self, event):
        old_rate = self.rates[self.current_currency]
        self.current_currency = self.curr_var.get()
        new_rate = self.rates[self.current_currency]
        symbols = {"UAH": "₴", "USD": "$", "EUR": "€"}
        self.currency_symbol = symbols.get(self.current_currency, "₴")
        
        conversion = old_rate / new_rate
        entries_to_convert = [self.ent_exp_amount, self.ent_price, self.ent_vcost, self.opt_v, self.opt_p1, self.opt_p2]
        
        for ent in entries_to_convert:
            val_str = ent.get()
            if val_str:
                try:
                    val = float(val_str.replace(" ", "").replace(",", ""))
                    ent.delete(0, 'end')
                    # Для полів вводу залишаємо машинний формат щоб не зламати парсинг, але конвертуємо
                    ent.insert(0, str(round(val * conversion, 2))) 
                except: pass

        self.recalculate_finance()
        self.update_dynamic_labels()
        
        for widget in self.mc_plot_frame.winfo_children():
            widget.destroy()
        self.mc_placeholder = ttk.Label(self.mc_plot_frame, text="⬅️ Введіть параметри та натисніть 'Запустити симуляцію',\nщоб побудувати графік та розрахувати математичні ризики.", justify="center", font=("Segoe UI Variable", 12))
        self.mc_placeholder.pack(expand=True)
            
        self.lbl_mc_mean.config(text="Очікуваний прибуток: - ⓘ")
        self.lbl_mc_loss.config(text="Ризик збитку: - ⓘ")
        self.lbl_mc_p05.config(text="Песимістичний (5%): - ⓘ")
        self.lbl_mc_p95.config(text="Оптимістичний (95%): - ⓘ")
        
        self.lbl_opt_res.config(text="")
        for widget in self.frame_plot.winfo_children():
            widget.destroy()

    def recalculate_finance(self):
        fixed_total_uah = self.get_fixed_costs_total()
        total_rev_uah = sum(x.revenue for x in self.products)
        total_cm_uah = sum(x.contribution for x in self.products)
        profit_uah = total_cm_uah - fixed_total_uah

        rate = self.rates[self.current_currency]
        fixed_total = fixed_total_uah / rate
        total_rev = total_rev_uah / rate
        total_cm = total_cm_uah / rate
        profit = profit_uah / rate
        sym = self.currency_symbol

        self.lbl_fixed_total.config(text=f"Всього постійних витрат: {self.fmt(fixed_total)} {sym} ⓘ")
        self.lbl_total_rev.config(text=f"Загальний дохід (Оборот): {self.fmt(total_rev)} {sym} ⓘ")
        self.lbl_total_margin.config(text=f"Загальна маржа: {self.fmt(total_cm)} {sym} ⓘ")
        
        color = "#00E676" if profit > 0 else "#FF5252"
        self.lbl_profit.config(text=f"💰 ЧИСТИЙ ПРИБУТОК: {self.fmt(profit)} {sym} ⓘ", foreground=color)

        if total_cm > 0 and total_rev > 0:
            margin_ratio = total_cm / total_rev 
            be_revenue = fixed_total / margin_ratio 
            self.lbl_be_money.config(text=f"Поріг окупності: {self.fmt(be_revenue)} {sym} ⓘ")

            if total_rev > be_revenue:
                safety_percent = ((total_rev - be_revenue) / total_rev) * 100
                self.lbl_safety.config(text=f"Запас міцності: {self.fmt(safety_percent, 1)}% ⓘ", foreground="#00E676")
                self.lbl_be_status.config(text="(Продажі можуть впасти настільки до збитків)")
            else:
                needed = be_revenue - total_rev
                self.lbl_safety.config(text="Зона збитків ⓘ", foreground="#FF5252")
                self.lbl_be_status.config(text=f"(Ще треба {self.fmt(needed)} {sym} до нуля)")
        elif total_cm <= 0:
             self.lbl_be_money.config(text="Маржа від'ємна ⓘ")
             self.lbl_safety.config(text="- ⓘ")
        
        if fixed_total > 0 and profit > 0:
            roi = (profit / fixed_total) * 100
            self.lbl_roi.config(text=f"📈 ROI (Рентабельність): {self.fmt(roi, 1)}% ⓘ", foreground="#60A5FA")
        else:
            self.lbl_roi.config(text="📈 ROI (Рентабельність): - ⓘ")

        if profit > 0:
            op_leverage = total_cm / profit 
            self.lbl_op_lev.config(text=f"⚙️ Операційний важіль: {self.fmt(op_leverage)} ⓘ")
        else:
            self.lbl_op_lev.config(text="⚙️ Операційний важіль: - ⓘ")


BusinessCalculatorApp = AdvancedBusinessCalculatorApp 

if __name__ == "__main__":
    root = tk.Tk()
    app = BusinessCalculatorApp(root)
    root.mainloop()