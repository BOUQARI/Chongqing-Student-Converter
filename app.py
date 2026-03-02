import tkinter as tk
from tkinter import messagebox
import requests

# --- لوحة الألوان العصرية ---
THEMES = {
    "dark": {
        "bg": "#1c1c1e",       # خلفية داكنة جداً
        "card": "#2c2c2e",     # خلفية الخانات
        "txt": "#ffffff",       # نص أبيض
        "accent": "#0a84ff",    # أزرق iOS
        "btn_txt": "#ffffff"
    },
    "light": {
        "bg": "#f2f2f7",       # خلفية فاتحة
        "card": "#ffffff",     # خلفية الخانات بيضاء
        "txt": "#000000",       # نص أسود
        "accent": "#007aff",    # أزرق كلاسيكي
        "btn_txt": "#ffffff"
    }
}

class ChongqingWalletUltra:
    def __init__(self, root):
        self.root = root
        self.root.title("Chongqing Student Wallet v3.0")
        self.root.geometry("450x650")
        
        # الحالات (States)
        self.is_dark_mode = True
        self.is_chinese = False
        self.is_tnd_to_cny = True

        # قاموس اللغات
        self.lang_dict = {
            "en": {
                "title": "Chongqing Wallet",
                "switch": "⇄ Switch Currency",
                "tnd_label": "Amount in TND (Tunisia):",
                "cny_label": "Amount in CNY (China):",
                "calc": "Calculate",
                "theme_btn": "☀ Light Mode",
                "lang_btn": "中文 (ZH)",
                "tip": "Ready for your journey to China?"
            },
            "zh": {
                "title": "重庆留学钱包",
                "switch": "⇄ 切换货币",
                "tnd_label": "突尼斯第纳尔 (TND):",
                "cny_label": "人民币 (CNY):",
                "calc": "计算",
                "theme_btn": "☀ 明亮模式",
                "lang_btn": "English (EN)",
                "tip": "准备好去中国了吗？"
            }
        }

        # --- بناء الواجهة (UI) ---
        self.main_container = tk.Frame(root, padx=30, pady=20)
        self.main_container.pack(fill="both", expand=True)

        # 1. Header (Buttons)
        self.header = tk.Frame(self.main_container)
        self.header.pack(fill="x")

        self.btn_theme = tk.Button(self.header, command=self.toggle_theme, relief="flat", padx=10, pady=5, cursor="hand2")
        self.btn_theme.pack(side="left")

        self.btn_lang = tk.Button(self.header, command=self.toggle_language, relief="flat", padx=10, pady=5, font=("Helvetica", 9, "bold"), cursor="hand2")
        self.btn_lang.pack(side="right")

        # 2. Body
        self.label_title = tk.Label(self.main_container, font=("Helvetica", 24, "bold"))
        self.label_title.pack(pady=30)

        self.btn_dir = tk.Button(self.main_container, command=self.toggle_direction, relief="flat", font=("Helvetica", 10), cursor="hand2")
        self.btn_dir.pack(pady=5)

        self.label_input = tk.Label(self.main_container, font=("Helvetica", 11))
        self.label_input.pack(pady=20)

        self.entry_amount = tk.Entry(self.main_container, font=("Helvetica", 18), justify='center', borderwidth=0)
        self.entry_amount.pack(pady=10, ipady=12, fill="x")

        self.btn_calc = tk.Button(self.main_container, command=self.convert, font=("Helvetica", 13, "bold"), relief="flat", cursor="hand2")
        self.btn_calc.pack(pady=35, ipady=12, fill="x")

        self.result_label = tk.Label(self.main_container, text="0.00", font=("Helvetica", 36, "bold"))
        self.result_label.pack(pady=10)

        self.info_label = tk.Label(self.main_container, font=("Helvetica", 10, "italic"))
        self.info_label.pack(side="bottom", pady=20)

        self.update_ui_full()

    # --- المنطق (Logic) ---

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.update_ui_full()

    def toggle_language(self):
        self.is_chinese = not self.is_chinese
        self.update_ui_full()

    def toggle_direction(self):
        self.is_tnd_to_cny = not self.is_tnd_to_cny
        self.update_ui_full()
        self.entry_amount.delete(0, tk.END)

    def update_ui_full(self):
        """تحديث شامل للألوان والنصوص بشكل متزامن"""
        theme = THEMES["dark"] if self.is_dark_mode else THEMES["light"]
        lang = "zh" if self.is_chinese else "en"
        
        # تحديث الألوان
        self.root.configure(bg=theme["bg"])
        self.main_container.configure(bg=theme["bg"])
        self.header.configure(bg=theme["bg"])
        
        self.label_title.config(bg=theme["bg"], fg=theme["accent"], text=self.lang_dict[lang]["title"])
        self.label_input.config(bg=theme["bg"], fg=theme["txt"])
        self.result_label.config(bg=theme["bg"], fg=theme["accent"])
        self.info_label.config(bg=theme["bg"], fg="#888888", text=self.lang_dict[lang]["tip"])
        
        # تحديث الأزرار
        self.btn_theme.config(bg=theme["card"], fg=theme["txt"], text=self.lang_dict[lang]["theme_btn"])
        self.btn_lang.config(bg=theme["accent"], fg="white", text=self.lang_dict[lang]["lang_btn"])
        self.btn_dir.config(bg=theme["card"], fg=theme["accent"], text=self.lang_dict[lang]["switch"])
        self.btn_calc.config(bg=theme["accent"], fg="white", text=self.lang_dict[lang]["calc"])
        
        self.entry_amount.config(bg=theme["card"], fg=theme["txt"], insertbackground=theme["txt"])
        
        # تحديث نصوص العملة حسب الاتجاه
        if self.is_tnd_to_cny:
            self.label_input.config(text=self.lang_dict[lang]["tnd_label"])
            self.result_label.config(text=self.result_label.cget("text").split()[0] + " ¥")
        else:
            self.label_input.config(text=self.lang_dict[lang]["cny_label"])
            self.result_label.config(text=self.result_label.cget("text").split()[0] + " TND")

    def convert(self):
        try:
            # استخدام API للحصول على سعر الصرف اللحظي
            url = "https://api.exchangerate-api.com/v4/latest/TND"
            data = requests.get(url).json()
            rate = data['rates']['CNY']
            
            amount = float(self.entry_amount.get())
            if self.is_tnd_to_cny:
                res = amount * rate
                self.result_label.config(text=f"{res:.2f} ¥")
            else:
                res = amount / rate
                self.result_label.config(text=f"{res:.2f} TND")
        except Exception:
            messagebox.showerror("Error", "Check Connection or Entry")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChongqingWalletUltra(root)
    root.mainloop()