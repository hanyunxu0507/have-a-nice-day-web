import tkinter as tk
from tkinter import ttk


def main():
    root = tk.Tk()
    root.title("Have a nice day!")
    root.geometry("360x160")
    root.resizable(False, False)

    frame = ttk.Frame(root, padding=24)
    frame.pack(expand=True, fill="both")

    label = ttk.Label(
        frame,
        text="Have a nice day!",
        font=("Segoe UI", 18),
        anchor="center",
    )
    label.pack(expand=True, fill="both")

    root.eval("tk::PlaceWindow . center")
    root.mainloop()


if __name__ == "__main__":
    main()
