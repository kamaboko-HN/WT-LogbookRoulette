import random
import tkinter as tk
import pyperclip

class LogbookRoulette():
    def __init__(self):
        self.battle_mode = ["AB", "RB"]
        self.junban_list = ["大きい順", "小さい順"]
        self.fanctors = ["勝利数", "バトル数", "勝率", "スポーン数", "デス数", "撃墜数(空中目標)", "撃破数(陸上目標)", "獲得SL"]
        self.result_label = None
        
        self.root = tk.Tk()
        self.root.title("WT Logbook Roulette")
        # self.root.geometry("500x200")
        self.root.minsize(500, 200)

        self.result_label = tk.Label(self.root, text="", font=("Meiryo", 12), wraplength=500)
        self.result_label.config(width=60, height=4)
        self.result_label.pack(pady=20)

        self.generate_button = tk.Button(self.root, text="次のバトル", command=self.show_random_choice, font=("Meiryo", 12))
        self.generate_button.config(width=50, height=2)
        self.generate_button.pack(pady=10)

        self.option_label = tk.Label(self.root, text="※クリップボードにコピーされます", font=("Meiryo", 7), wraplength=500, foreground="red")
        self.option_label.pack(pady=5)

        self.root.mainloop()

    def show_random_choice(self):
        battle = random.choice(self.battle_mode)
        up_down = random.choice(self.junban_list)
        sort_factor = random.choice(self.fanctors)
        rank = random.randint(1, 2000)
        result = f"バトルモード：{battle}\nソート基準：{sort_factor}　|　順番：{up_down}\n順位：{rank}, {rank//2}, {rank//2//2}, {rank//2//2//2}, {rank//2//2//2//2}"
        self.result_label.config(text=result)
        clipboard_text = f"バトルモード：{battle}　|　ソート基準：{sort_factor}　|　順番：{up_down}　|　順位：{rank}, {rank//2}, {rank//2//2}, {rank//2//2//2}, {rank//2//2//2//2}"
        pyperclip.copy(clipboard_text)

LogbookRoulette()