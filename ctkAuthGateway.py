import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.attributes("-alpha", 0.90)
app.title("Giriş Paneli")

app.rowconfigure(0, weight=1)
app.columnconfigure(0, weight=1)

ekranFrame = ctk.CTkFrame(app, fg_color="#2b2b2b", corner_radius=15, border_width=2, border_color="#3a3a3a")
ekranFrame.grid(row=0, column=0, padx=20, pady=20)

def ekranıOrtala():
    pencereGenisligi = 450
    pencereYuksekligi = 380

    ekranGenisligi = app.winfo_screenwidth()
    ekranYuksekligi = app.winfo_screenheight()

    x = int(ekranGenisligi / 2 - pencereGenisligi / 2)
    y = int(ekranYuksekligi / 2 - pencereYuksekligi / 2)

    app.geometry(f"{pencereGenisligi}x{pencereYuksekligi}+{x}+{y}")

ekranıOrtala()

def ekranıTemizle():
    isimEntry.delete(0, "end")
    sifreEntry.delete(0, "end")
    sifreyiGosterCheck.deselect()
    sifreEntry.configure(show="*")
    durumLabel.configure(text="")

def SifreyiGosterGizle():
    if sifreyiGosterCheck.get() == 1:
        sifreEntry.configure(show="")
    else:
        sifreEntry.configure(show="*")

def SifreKontrol():
    ad = isimEntry.get()
    sifre = sifreEntry.get()

    if ad == "" or sifre == "":
        durumLabel.configure(text="Kullanıcı adı veya şifre boş olamaz", text_color="#f1c40f")
        return

    uzunlukUygun = len(sifre) > 6
    buyukHarfVar = any(c.isupper() for c in sifre)
    kucukHarfVar = any(c.islower() for c in sifre)
    rakamVeyaOzelVar = any(not c.isalnum() for c in sifre)

    eksikler = []
    if not uzunlukUygun:
        eksikler.append("en az 6 karakter olmalı")
    if not buyukHarfVar:
        eksikler.append("büyük harf eksik")
    if not kucukHarfVar:
        eksikler.append("küçük harf eksik")
    if not rakamVeyaOzelVar:
        eksikler.append("özel karakter veya rakam eksik")

    if eksikler:
        uyariMetni = "Şifre zayıf: " + ", ".join(eksikler)
        durumLabel.configure(text=uyariMetni, text_color="#e74c3c")
    else:
        durumLabel.configure(text="Tebrikler! Şifre kurallara uygun, giriş başarılı.", text_color="#2ecc71")

baslikLabel = ctk.CTkLabel(ekranFrame, text="Kullanıcı Girişi", font=("Arial", 20, "bold"), text_color="#1f6aa5")
baslikLabel.grid(row=0, column=0, columnspan=3, pady=(20, 15))

isimLabel = ctk.CTkLabel(ekranFrame, text="Kullanıcı Adı :", text_color="#dce4ee", font=("Arial", 13, "bold"))
isimLabel.grid(row=1, column=0, padx=15, pady=10, sticky="e")

isimEntry = ctk.CTkEntry(ekranFrame, placeholder_text="Kullanıcı adınızı girin...", width=220, corner_radius=8)
isimEntry.grid(row=1, column=1, columnspan=2, padx=15, pady=10, sticky="ew")

sifreLabel = ctk.CTkLabel(ekranFrame, text="Şifre :", text_color="#dce4ee", font=("Arial", 13, "bold"))
sifreLabel.grid(row=2, column=0, padx=15, pady=10, sticky="e")

sifreEntry = ctk.CTkEntry(ekranFrame, placeholder_text="Şifrenizi giriniz...", show="*", width=220, corner_radius=8)
sifreEntry.grid(row=2, column=1, columnspan=2, padx=15, pady=10, sticky="ew")

sifreyiGosterCheck = ctk.CTkCheckBox(ekranFrame, text="Şifreyi Göster", font=("Arial", 11), command=SifreyiGosterGizle)
sifreyiGosterCheck.grid(row=3, column=1, columnspan=2, padx=15, pady=5, sticky="w")

girisButton = ctk.CTkButton(ekranFrame, text="Giriş Yap", font=("Arial", 13, "bold"), fg_color="#1f6aa5", hover_color="#144870", corner_radius=8, command=SifreKontrol)
girisButton.grid(row=4, column=1, padx=5, pady=20, sticky="ew")

temizleButton = ctk.CTkButton(ekranFrame, text="Temizle", font=("Arial", 13, "bold"), fg_color="#3a3a3a", hover_color="#505050", text_color="#ffffff", corner_radius=8, command=ekranıTemizle)
temizleButton.grid(row=4, column=2, padx=5, pady=20, sticky="ew")

durumLabel = ctk.CTkLabel(ekranFrame, text="", font=("Arial", 11, "bold"))
durumLabel.grid(row=5, column=0, columnspan=3, pady=(0, 15), padx=10)

app.mainloop()