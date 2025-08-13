import customtkinter as ctk

def ctk_messagebox(title, message):
    popup = ctk.CTkToplevel()
    popup.title(title)
    popup.geometry("300x150")
    popup.grab_set()  # make it modal

    label = ctk.CTkLabel(popup, text=message, wraplength=280)
    label.pack(pady=20, padx=10)

    def close():
        popup.destroy()

    ok_button = ctk.CTkButton(popup, text="OK", command=close)
    ok_button.pack(pady=(0, 20))

    popup.mainloop()
