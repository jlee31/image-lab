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

def button_click_event():
    dialog = ctk.CTkInputDialog(text="Type in a number:", title="Test")
    print("Number:", dialog.get_input())


def ctk_questionbox(title, message):
    popup = ctk.CTkToplevel()
    popup.title(title)
    popup.geometry("400x250")
    popup.grab_set()  # make it modal

    label = ctk.CTkLabel(popup, text=message, wraplength=280)
    label.pack(pady=20, padx=10)

    dialog = ctk.CTkInputDialog(text="Type in a number:", title="Test")
    print("Number:", dialog.get_input())

    def close():
        popup.destroy()

    ok_button = ctk.CTkButton(popup, text="OK", command=close)
    ok_button.pack(pady=(0, 20))

    popup.mainloop()

def ctk_get_value(input, minvalue, maxvalue, type):
    dialog = ctk.CTkInputDialog(text=input, title="Input")
    value = dialog.get_input()
    if not value:
        return
    value = type(value)
    if value < minvalue or value > maxvalue:
        ctk_messagebox("Error", "Please enter a valid value")
        return None
    else:
        return value