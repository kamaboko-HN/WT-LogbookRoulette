import random
import tkinter as tk
import pyperclip
import json

class LogbookRoulette():
    def __init__(self):
        self.battle_mode = ["AB", "RB"]
        self.junban_list = ["大きい順", "小さい順"]
        self.fanctors = ["勝利数", "バトル数", "勝率", "スポーン数", "デス数", "撃墜数(空中目標)", "撃破数(陸上目標)", "獲得SL"]
        
        self.root = tk.Tk()
        self.root.title("WT Logbook Roulette")
        # self.root.geometry("500x200")
        self.root.minsize(500, 200)
        
        self.result_label_var = tk.StringVar()
        self.indention_bool_var = tk.BooleanVar()
        self.onlyuse_members_bool_var = tk.BooleanVar()
        self.A_team_list = []
        self.members_list = []
        self.B_team_list = []
        
        # Load settings if available
        try:
            with open("WT-LogbookRoulette-Settings.json", "r", encoding="utf-8") as f:
                settings = json.load(f)
                self.indention_bool_var.set(settings.get("indention_bool", False))
                self.onlyuse_members_bool_var.set(settings.get("onlyuse_members_bool", False))
                self.members_list = settings.get("members_list", [])
        except FileNotFoundError:
            pass

        self.result_label = tk.Label(self.root, textvariable=self.result_label_var, font=("Meiryo", 12), wraplength=500)
        self.result_label.config(width=60, height=4)
        self.result_label.pack(pady=20)
        
        self.listbox_frame = tk.Frame(self.root)
        self.A_team_frame = tk.Frame(self.listbox_frame)
        self.members_frame = tk.Frame(self.listbox_frame)
        self.members_listbox_frame = tk.Frame(self.members_frame)
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
        
        self.members_label = tk.Label(self.members_frame, text="メンバー", font=("Meiryo", 10))
        self.members_label.pack()
        self.members_listbox = tk.Listbox(self.members_listbox_frame, height=6, listvariable=tk.StringVar(value=self.members_list))
        self.members_listbox.pack(side="left", fill="y")
        self.members_listbox_scrollbar = tk.Scrollbar(self.members_listbox_frame, orient="vertical", command=self.members_listbox.yview)
        self.members_listbox.config(yscrollcommand=self.members_listbox_scrollbar.set)
        self.members_listbox_scrollbar.pack(side="right", fill="y")
        self.members_listbox_frame.pack()
        
        self.members_add_entry = tk.Entry(self.list_edit_frame, font=("Meiryo", 8))
        self.members_add_entry.pack(pady=5)
        self.members_add_button = tk.Button(self.list_edit_frame, text="追加", font=("Meiryo", 8), command=self.add_new_member)
        self.members_add_button.pack(pady=5, side="left")
        self.members_remove_button = tk.Button(self.list_edit_frame, text="削除", font=("Meiryo", 8), command=self.remove_member)
        self.members_remove_button.pack(pady=5, side="right")
        self.list_edit_frame.pack()
        
        self.B_team_label = tk.Label(self.B_team_frame, text="Bチーム", font=("Meiryo", 10, "bold"), fg="red")
        self.B_team_label.pack()
        self.B_team_listbox = tk.Listbox(self.B_team_frame, listvariable=tk.StringVar(value=self.B_team_list))
        self.B_team_listbox.pack(fill="y")
        
        self.checkbox_frame = tk.Frame(self.root)
        self.checkbox_frame.pack(pady=5)
        self.indention_check_box = tk.Checkbutton(self.checkbox_frame, text="改行付きでクリップボードにコピー", font=("Meiryo", 10), variable=self.indention_bool_var, command=self.log_now_settings)
        self.indention_check_box.pack(side="left")
        self.onlyuse_members_check_box = tk.Checkbutton(self.checkbox_frame, text="チーム分けのみ使用", font=("Meiryo", 10), variable=self.onlyuse_members_bool_var, command=self.log_now_settings)
        self.onlyuse_members_check_box.pack(side="right")

        self.generate_button = tk.Button(self.root, text="次のバトル", command=self.next_battle, font=("Meiryo", 12))
        self.generate_button.config(width=50, height=2)
        self.generate_button.pack(pady=10)

        self.option_label = tk.Label(self.root, text="※クリップボードにコピーされます", font=("Meiryo", 7), wraplength=500, foreground="red")
        self.option_label.pack(pady=5)

        self.root.mainloop()
        
    def add_new_member(self):
        new_member = self.members_add_entry.get()
        if new_member and new_member not in self.members_list:
            self.members_list.append(new_member)
            self.members_listbox.config(listvariable=tk.StringVar(value=self.members_list))
            self.members_add_entry.delete(0, tk.END)
            self.log_now_settings()
            
    def remove_member(self):
        selected_indices = self.members_listbox.curselection()
        for index in reversed(selected_indices):
            del self.members_list[index]
        self.members_listbox.config(listvariable=tk.StringVar(value=self.members_list))
        self.log_now_settings()
        
    def shuffle_members(self):
        shuffled_members = self.members_list[:]
        random.shuffle(shuffled_members)
        mid = len(shuffled_members) // 2
        self.A_team_list = shuffled_members[:mid]
        self.B_team_list = shuffled_members[mid:]
        self.A_team_listbox.config(listvariable=tk.StringVar(value=self.A_team_list))
        self.B_team_listbox.config(listvariable=tk.StringVar(value=self.B_team_list))

    def show_random_choice(self):
        battle = random.choice(self.battle_mode)
        up_down = random.choice(self.junban_list)
        sort_factor = random.choice(self.fanctors)
        rank = random.randint(1, 2000)
        result = f"バトルモード：{battle}\nソート基準：{sort_factor}　|　順番：{up_down}\n順位：{rank}, {rank//2}, {rank//2//2}, {rank//2//2//2}, {rank//2//2//2//2}"
        #self.result_label.config(text=result)
        self.result_label_var.set(result)
        
        if self.indention_bool_var.get():
            clipboard_text = f"バトルモード：{battle}\nソート基準：{sort_factor}\n順番：{up_down}\n順位：{rank}, {rank//2}, {rank//2//2}, {rank//2//2//2}, {rank//2//2//2//2}"
        else:
            clipboard_text = f"バトルモード：{battle}　|　ソート基準：{sort_factor}　|　順番：{up_down}　|　順位：{rank}, {rank//2}, {rank//2//2}, {rank//2//2//2}, {rank//2//2//2//2}"
        
        return clipboard_text
        
    def next_battle(self):
        if self.onlyuse_members_bool_var.get():
            self.shuffle_members()
            if self.A_team_list and self.B_team_list:
                clipboard_text = f"\n\nAチーム: " + ", ".join(self.A_team_list)
                clipboard_text += f"\n\nBチーム: " + ", ".join(self.B_team_list)
        else:
            clipboard_text = self.show_random_choice()
            self.shuffle_members()
            if self.A_team_list and self.B_team_list:
                clipboard_text += f"\n\nAチーム: " + ", ".join(self.A_team_list)
                clipboard_text += f"\n\nBチーム: " + ", ".join(self.B_team_list)
        
        pyperclip.copy(clipboard_text)
        
    def log_now_settings(self):
        settings = {"indention_bool": self.indention_bool_var.get(),
                    "onlyuse_members_bool": self.onlyuse_members_bool_var.get(),
                    "members_list": self.members_list}
        with open("WT-LogbookRoulette-Settings.json", "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
            
            
            

LogbookRoulette()