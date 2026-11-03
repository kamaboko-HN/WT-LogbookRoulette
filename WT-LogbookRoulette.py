import os
import sys
import random
import tkinter as tk
import pyperclip
import json

# exe化した場合も設定ファイルを実行ファイルと同じ場所に置く
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(BASE_DIR, "WT-LogbookRoulette-Settings.json")
VERSION = "v2.2"

class LogbookRoulette():
    def __init__(self):
        self.battle_mode = ["AB", "RB"]
        self.junban_list = ["大きい順(降順)", "小さい順(昇順)"]
        self.fanctors = ["勝利数", "バトル数", "勝率", "スポーン数", "デス数", "撃墜数(空中目標)", "撃破数(陸上目標)", "獲得SL", "車両ランク"]
        self.ranks = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]
        self.vehicle_types = ["陸上車両", "航空機", "ヘリコプター", "艦艇"]

        self.root = tk.Tk()
        self.root.title(f"WT Logbook Roulette {VERSION}")
        # self.root.geometry("500x200")
        self.root.minsize(500, 200)

        self.menubar = tk.Menu(self.root)
        self.menu_file = tk.Menu(self.menubar, tearoff = False)
        self.menu_file.add_command(label = "終了", command = self.root.destroy)

        self.result_label_var = tk.StringVar()
        self.indention_bool_var = tk.BooleanVar()
        self.onlyuse_members_bool_var = tk.BooleanVar()
        self.discord_bool_var = tk.BooleanVar()
        self.A_team_list = []
        self.members = []  # [{"name": str, "var": BooleanVar}]
        self.B_team_list = []
        self.rank_vars = {rank: tk.BooleanVar(value=True) for rank in self.ranks}
        self.vehicle_type_vars = {vehicle_type: tk.BooleanVar(value=True) for vehicle_type in self.vehicle_types}

        self.load_settings()

        self.result_label = tk.Label(self.root, textvariable=self.result_label_var, font=("Meiryo", 12), wraplength=500)
        self.result_label.config(width=60, height=7)
        self.result_label.pack(pady=20)

        # 使用可能な車両ランク・車種
        self.rank_frame = tk.LabelFrame(self.root, text="使用可能な車両ランク", font=("Meiryo", 10))
        self.rank_frame.pack(padx=10, pady=5)
        for rank in self.ranks:
            tk.Checkbutton(self.rank_frame, text=rank, font=("Meiryo", 10), variable=self.rank_vars[rank], command=self.save_settings).pack(side="left")
        tk.Button(self.rank_frame, text="全て選択", font=("Meiryo", 8), command=lambda: self.set_all_vars(self.rank_vars, True)).pack(side="left", padx=2)
        tk.Button(self.rank_frame, text="全て解除", font=("Meiryo", 8), command=lambda: self.set_all_vars(self.rank_vars, False)).pack(side="left", padx=2)

        self.vehicle_type_frame = tk.LabelFrame(self.root, text="使用可能な車種", font=("Meiryo", 10))
        self.vehicle_type_frame.pack(padx=10, pady=5)
        for vehicle_type in self.vehicle_types:
            tk.Checkbutton(self.vehicle_type_frame, text=vehicle_type, font=("Meiryo", 10), variable=self.vehicle_type_vars[vehicle_type], command=self.save_settings).pack(side="left")

        self.listbox_frame = tk.Frame(self.root)
        self.A_team_frame = tk.Frame(self.listbox_frame)
        self.members_frame = tk.Frame(self.listbox_frame)
        self.members_list_frame = tk.Frame(self.members_frame, relief="sunken", borderwidth=1)
        self.B_team_frame = tk.Frame(self.listbox_frame)
        self.list_edit_frame = tk.Frame(self.members_frame)

        self.listbox_frame.pack()
        self.A_team_frame.pack(side="left", padx=20, anchor="n")
        self.members_frame.pack(side="left", padx=20, anchor="n")
        self.B_team_frame.pack(side="left", padx=20, anchor="n")

        self.A_team_label = tk.Label(self.A_team_frame, text="Aチーム", font=("Meiryo", 10, "bold"), fg="blue")
        self.A_team_label.pack()
        self.A_team_listbox = tk.Listbox(self.A_team_frame, listvariable=tk.StringVar(value=self.A_team_list))
        self.A_team_listbox.pack(fill="y")

        # メンバー一覧（チェックしたメンバーのみチーム分けに参加）
        self.members_label = tk.Label(self.members_frame, text="メンバー（参加者にチェック）", font=("Meiryo", 10))
        self.members_label.pack()
        self.members_canvas = tk.Canvas(self.members_list_frame, width=180, height=120, highlightthickness=0)
        self.members_canvas.pack(side="left", fill="y")
        self.members_list_scrollbar = tk.Scrollbar(self.members_list_frame, orient="vertical", command=self.members_canvas.yview)
        self.members_canvas.config(yscrollcommand=self.members_list_scrollbar.set)
        self.members_list_scrollbar.pack(side="right", fill="y")
        self.members_inner_frame = tk.Frame(self.members_canvas)
        self.members_canvas.create_window((0, 0), window=self.members_inner_frame, anchor="nw")
        self.members_inner_frame.bind("<Configure>", lambda event: self.members_canvas.config(scrollregion=self.members_canvas.bbox("all")))
        self.members_canvas.bind("<Enter>", lambda event: self.members_canvas.bind_all("<MouseWheel>", self.on_members_mousewheel))
        self.members_canvas.bind("<Leave>", lambda event: self.members_canvas.unbind_all("<MouseWheel>"))
        self.members_list_frame.pack()

        self.members_add_entry = tk.Entry(self.list_edit_frame, font=("Meiryo", 8))
        self.members_add_entry.pack(pady=5)
        self.members_add_entry.bind("<Return>", lambda event: self.add_new_member())
        self.members_add_button = tk.Button(self.list_edit_frame, text="追加", font=("Meiryo", 8), command=self.add_new_member)
        self.members_add_button.pack(pady=5, side="left")
        self.members_all_button = tk.Button(self.list_edit_frame, text="全員チェック", font=("Meiryo", 8), command=lambda: self.set_all_members(True))
        self.members_all_button.pack(pady=5, padx=2, side="left")
        self.members_none_button = tk.Button(self.list_edit_frame, text="全員外す", font=("Meiryo", 8), command=lambda: self.set_all_members(False))
        self.members_none_button.pack(pady=5, side="left")
        self.list_edit_frame.pack()

        self.B_team_label = tk.Label(self.B_team_frame, text="Bチーム", font=("Meiryo", 10, "bold"), fg="red")
        self.B_team_label.pack()
        self.B_team_listbox = tk.Listbox(self.B_team_frame, listvariable=tk.StringVar(value=self.B_team_list))
        self.B_team_listbox.pack(fill="y")

        self.checkbox_frame = tk.Frame(self.root)
        self.checkbox_frame.pack(pady=5)
        self.indention_check_box = tk.Checkbutton(self.checkbox_frame, text="改行付きでクリップボードにコピー", font=("Meiryo", 10), variable=self.indention_bool_var, command=self.save_settings)
        self.indention_check_box.pack(side="left")
        self.onlyuse_members_check_box = tk.Checkbutton(self.checkbox_frame, text="チーム分けのみ使用", font=("Meiryo", 10), variable=self.onlyuse_members_bool_var, command=self.save_settings)
        self.onlyuse_members_check_box.pack(side="right")

        self.generate_button = tk.Button(self.root, text="次のバトル", command=self.next_battle, font=("Meiryo", 12))
        self.generate_button.config(width=50, height=2)
        self.generate_button.pack(pady=10)

        self.option_label = tk.Label(self.root, text="※クリップボードにコピーされます", font=("Meiryo", 7), wraplength=500, foreground="red")
        self.option_label.pack(pady=5)

        self.discord_check_box = tk.Checkbutton(self.root, text="Discord用に文字装飾してコピー", font=("Meiryo", 10), variable=self.discord_bool_var, command=self.save_settings)
        self.discord_check_box.pack(pady=5)

        # メニューバーに各メニューを追加
        self.menubar.add_cascade(label="ファイル", menu = self.menu_file)
        self.root.config(menu = self.menubar)

        self.refresh_members_view()
        self.root.mainloop()

    def on_members_mousewheel(self, event):
        self.members_canvas.yview_scroll(int(-event.delta / 120), "units")

    def refresh_members_view(self):
        for child in self.members_inner_frame.winfo_children():
            child.destroy()
        for member in self.members:
            row = tk.Frame(self.members_inner_frame)
            row.pack(fill="x", anchor="w")
            tk.Checkbutton(row, text=member["name"], font=("Meiryo UI", 9), pady=0, bd=0, highlightthickness=0, variable=member["var"], command=self.save_settings).pack(side="left")
            tk.Button(row, text="×", font=("Meiryo UI", 7), relief="flat", pady=0, bd=0, highlightthickness=0, fg="gray", command=lambda name=member["name"]: self.remove_member(name)).pack(side="right")

    def add_new_member(self):
        new_member = self.members_add_entry.get().strip()
        if new_member and new_member not in [member["name"] for member in self.members]:
            self.members.append({"name": new_member, "var": tk.BooleanVar(value=True)})
            self.refresh_members_view()
            self.members_add_entry.delete(0, tk.END)
            self.save_settings()

    def remove_member(self, name):
        self.members = [member for member in self.members if member["name"] != name]
        self.refresh_members_view()
        self.save_settings()

    def set_all_members(self, value):
        for member in self.members:
            member["var"].set(value)
        self.save_settings()

    def shuffle_members(self):
        shuffled_members = [member["name"] for member in self.members if member["var"].get()]
        random.shuffle(shuffled_members)
        mid = len(shuffled_members) // 2
        self.A_team_list = shuffled_members[:mid]
        self.B_team_list = shuffled_members[mid:]
        self.A_team_listbox.config(listvariable=tk.StringVar(value=self.A_team_list))
        self.B_team_listbox.config(listvariable=tk.StringVar(value=self.B_team_list))

    def set_all_vars(self, vars_dict, value):
        for var in vars_dict.values():
            var.set(value)
        self.save_settings()

    def get_enabled(self, vars_dict):
        return [key for key, var in vars_dict.items() if var.get()]

    def format_line(self, emoji, label, value, sep="："):
        # Discord用は絵文字＋太字の見出しにする
        if self.discord_bool_var.get():
            return f"{emoji} **{label}**{sep}{value}"
        return f"{label}{sep}{value}"

    def team_text(self):
        if not (self.A_team_list and self.B_team_list):
            return ""
        return ("\n\n" + self.format_line("🔵", "Aチーム", ", ".join(self.A_team_list), sep=": ")
                + "\n\n" + self.format_line("🔴", "Bチーム", ", ".join(self.B_team_list), sep=": "))

    def show_random_choice(self):
        battle = random.choice(self.battle_mode)
        up_down = random.choice(self.junban_list)
        sort_factor = random.choice(self.fanctors)
        rank = random.randint(1, 2000)
        rank_text = f"{rank}, {rank//2}, {rank//2//2}, {rank//2//2//2}, {rank//2//2//2//2}"

        enabled_ranks_text = ", ".join(self.get_enabled(self.rank_vars))
        enabled_vehicle_types_text = ", ".join(self.get_enabled(self.vehicle_type_vars))

        spacer = "――――――――――"

        # 使用可能ランク・車種を先頭に置き、スペーサーを挟んで抽選結果を並べる
        result = "\n".join([f"使用可能ランク：{enabled_ranks_text}", f"使用可能車種：{enabled_vehicle_types_text}", spacer,
                            f"バトルモード：{battle}", f"ソート基準：{sort_factor}　|　順番：{up_down}", f"順位：{rank_text}"])
        #self.result_label.config(text=result)
        self.result_label_var.set(result)

        limit_lines = [self.format_line("🎖️", "使用可能ランク", enabled_ranks_text),
                       self.format_line("🛩️", "使用可能車種", enabled_vehicle_types_text)]
        clipboard_lines = [self.format_line("🎮", "バトルモード", battle),
                           self.format_line("📊", "ソート基準", sort_factor),
                           self.format_line("🔃", "順番", up_down),
                           self.format_line("🏆", "順位", rank_text)]
        if self.indention_bool_var.get():
            clipboard_text = "\n".join(limit_lines + [spacer] + clipboard_lines)
        else:
            clipboard_text = "\n".join(["　|　".join(limit_lines), spacer, "　|　".join(clipboard_lines)])

        return clipboard_text

    def next_battle(self):
        clipboard_text = ""
        if self.onlyuse_members_bool_var.get():
            self.shuffle_members()
            clipboard_text = self.team_text()
        else:
            if not self.get_enabled(self.rank_vars) or not self.get_enabled(self.vehicle_type_vars):
                self.result_label_var.set("使用可能なランク・車種を1つ以上選択してください")
                return
            clipboard_text = self.show_random_choice()
            self.shuffle_members()
            clipboard_text += self.team_text()

        pyperclip.copy(clipboard_text)

    def load_settings(self):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                settings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return
        self.indention_bool_var.set(settings.get("indention_bool", False))
        self.onlyuse_members_bool_var.set(settings.get("onlyuse_members_bool", False))
        self.discord_bool_var.set(settings.get("discord_bool", False))
        members = settings.get("members")
        if members is None:
            # 旧形式（名前のみのリスト）からの移行
            members = [{"name": name, "enabled": True} for name in settings.get("members_list", [])]
        self.members = [{"name": member["name"], "var": tk.BooleanVar(value=member.get("enabled", True))} for member in members]
        enabled_ranks = settings.get("enabled_ranks", self.ranks)
        for rank, var in self.rank_vars.items():
            var.set(rank in enabled_ranks)
        enabled_vehicle_types = settings.get("enabled_vehicle_types", self.vehicle_types)
        for vehicle_type, var in self.vehicle_type_vars.items():
            var.set(vehicle_type in enabled_vehicle_types)

    def save_settings(self):
        settings = {"indention_bool": self.indention_bool_var.get(),
                    "onlyuse_members_bool": self.onlyuse_members_bool_var.get(),
                    "discord_bool": self.discord_bool_var.get(),
                    "members": [{"name": member["name"], "enabled": member["var"].get()} for member in self.members],
                    "enabled_ranks": self.get_enabled(self.rank_vars),
                    "enabled_vehicle_types": self.get_enabled(self.vehicle_type_vars)}
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)




LogbookRoulette()
