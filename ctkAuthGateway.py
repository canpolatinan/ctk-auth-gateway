
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time
from pathlib import Path
from tkinter import font as tkfont

import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

VERI_DOSYASI = Path(__file__).with_name("kullanicilar.json")


C = {
    "arka": "#0b0f14",
    "panel": "#121821",
    "kart": "#171e29",
    "girdi": "#0d1219",
    "kenar": "#263040",
    "canvas": "#0d1117",
    "nokta": "#18202b",
    "metin": "#e6edf3",
    "soluk": "#8795a8",
    "mavi": "#3b82f6", "mavi_h": "#2563eb",
    "yesil_btn": "#0d9488", "yesil_btn_h": "#0f766e",
    "kirmizi_btn": "#dc2626", "kirmizi_btn_h": "#b91c1c",
    "mor": "#7c3aed", "mor_h": "#6d28d9",
    "gri": "#263040", "gri_h": "#334155",
    "dugum": "#243b55", "dugum_kenar": "#5b7ea6",
    "yol": "#f59e0b",
    "basari": "#22c55e",
    "uyari": "#eab308",
    "hata": "#ef4444",
}
DURUM_RENK = {"bilgi": C["mavi"], "basari": C["basari"], "uyari": C["uyari"], "hata": C["hata"]}

FONT = "Arial"


def yazi_tipi_sec() -> None:
    """Sistemde bulunan en güzel yazı tipini seçer."""
    global FONT
    mevcut = set(tkfont.families())
    for ad in ("Segoe UI", "Inter", "SF Pro Text", "Helvetica Neue", "Ubuntu", "DejaVu Sans", "Arial"):
        if ad in mevcut:
            FONT = ad
            return


def f(boyut: int, kalin: bool = False):
    return (FONT, boyut, "bold") if kalin else (FONT, boyut)


def karistir(c1: str, c2: str, t: float) -> str:
    """İki hex rengi t oranında karıştırır (parlama efektleri için)."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def egri_noktalari(x0: float, y0: float, x1: float, y1: float, n: int = 18) -> list[float]:
    """Üstten alta yumuşak S eğrisi (kübik Bezier) için nokta listesi."""
    ym = (y0 + y1) / 2
    nokta: list[float] = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        nokta.append(u ** 3 * x0 + 3 * u * u * t * x0 + 3 * u * t * t * x1 + t ** 3 * x1)
        nokta.append(u ** 3 * y0 + 3 * u * u * t * ym + 3 * u * t * t * ym + t ** 3 * y1)
    return nokta


def kucult(metin: str) -> str:
    """Türkçe'ye duyarlı küçük harf (I -> ı, İ -> i)."""
    return metin.replace("I", "ı").replace("İ", "i").lower()



MIN_SIFRE_UZUNLUGU = 8


def sifre_kontrolleri(sifre: str) -> list[tuple[bool, str]]:
    return [
        (len(sifre) >= MIN_SIFRE_UZUNLUGU, f"En az {MIN_SIFRE_UZUNLUGU} karakter"),
        (any(c.isupper() for c in sifre), "Büyük harf"),
        (any(c.islower() for c in sifre), "Küçük harf"),
        (any(c.isdigit() for c in sifre), "Rakam"),
        (any(not c.isalnum() for c in sifre), "Özel karakter"),
    ]


class KullaniciDeposu:
    ITERASYON = 200_000

    def __init__(self, yol: Path):
        self.yol = yol
        self.veri: dict[str, dict] = self._yukle()

    def _yukle(self) -> dict:
        try:
            return json.loads(self.yol.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _kaydet(self) -> None:
        gecici = self.yol.with_suffix(".tmp")
        gecici.write_text(json.dumps(self.veri, indent=2), encoding="utf-8")
        os.replace(gecici, self.yol)

    @staticmethod
    def _ozet(sifre: str, tuz: bytes, iterasyon: int) -> bytes:
        return hashlib.pbkdf2_hmac("sha256", sifre.encode("utf-8"), tuz, iterasyon)

    def kayit_ol(self, ad: str, sifre: str) -> tuple[bool, str]:
        anahtar = ad.lower()
        if anahtar in self.veri:
            return False, "Bu kullanıcı adı zaten alınmış."
        tuz = secrets.token_bytes(16)
        self.veri[anahtar] = {
            "tuz": tuz.hex(),
            "iter": self.ITERASYON,
            "hash": self._ozet(sifre, tuz, self.ITERASYON).hex(),
        }
        try:
            self._kaydet()
        except OSError as hata:
            del self.veri[anahtar]
            return False, f"Kayıt dosyasına yazılamadı: {hata}"
        return True, "Kayıt başarılı! Şimdi giriş yapabilirsiniz."

    def dogrula(self, ad: str, sifre: str) -> bool:
        kayit = self.veri.get(ad.lower())
        if kayit is None:
            self._ozet(sifre, b"\x00" * 16, self.ITERASYON)
            return False
        beklenen = bytes.fromhex(kayit["hash"])
        hesaplanan = self._ozet(sifre, bytes.fromhex(kayit["tuz"]), kayit["iter"])
        return hmac.compare_digest(hesaplanan, beklenen)


class TrieDugumu:
    __slots__ = ("cocuklar", "kelime_sonu")

    def __init__(self):
        self.cocuklar: dict[str, TrieDugumu] = {}
        self.kelime_sonu = False


class Trie:
    def __init__(self):
        self.kok = TrieDugumu()
        self.kelime_sayisi = 0

    def temizle(self) -> None:
        self.kok = TrieDugumu()
        self.kelime_sayisi = 0

    def ekle(self, kelime: str) -> bool:
        dugum = self.kok
        for harf in kelime:
            dugum = dugum.cocuklar.setdefault(harf, TrieDugumu())
        if dugum.kelime_sonu:
            return False
        dugum.kelime_sonu = True
        self.kelime_sayisi += 1
        return True

    def _bul(self, onek: str) -> TrieDugumu | None:
        dugum = self.kok
        for harf in onek:
            dugum = dugum.cocuklar.get(harf)
            if dugum is None:
                return None
        return dugum

    def ara(self, kelime: str) -> bool:
        dugum = self._bul(kelime)
        return dugum is not None and dugum.kelime_sonu

    def eslesen_uzunluk(self, kelime: str) -> int:
        dugum, n = self.kok, 0
        for harf in kelime:
            dugum = dugum.cocuklar.get(harf)
            if dugum is None:
                break
            n += 1
        return n

    def sil(self, kelime: str) -> bool:
        yol = [self.kok]
        for harf in kelime:
            sonraki = yol[-1].cocuklar.get(harf)
            if sonraki is None:
                return False
            yol.append(sonraki)
        if not yol[-1].kelime_sonu:
            return False
        yol[-1].kelime_sonu = False
        self.kelime_sayisi -= 1
        for i in range(len(kelime), 0, -1):
            if yol[i].kelime_sonu or yol[i].cocuklar:
                break
            del yol[i - 1].cocuklar[kelime[i - 1]]
        return True

    def onek_ile_kelimeler(self, onek: str) -> list[str]:
        baslangic = self._bul(onek)
        if baslangic is None:
            return []
        sonuc: list[str] = []

        def gez(dugum: TrieDugumu, simdiki: str) -> None:
            if dugum.kelime_sonu:
                sonuc.append(simdiki)
            for harf in sorted(dugum.cocuklar):
                gez(dugum.cocuklar[harf], simdiki + harf)

        gez(baslangic, onek)
        return sonuc

    def tum_kelimeler(self) -> list[str]:
        return self.onek_ile_kelimeler("")

    def dugum_sayisi(self) -> int:
        sayac, yigin = 0, [self.kok]
        while yigin:
            d = yigin.pop()
            sayac += len(d.cocuklar)
            yigin.extend(d.cocuklar.values())
        return sayac


class GirisEkrani(ctk.CTkFrame):
    MAX_DENEME = 5
    KILIT_SN = 30

    def __init__(self, master: "Uygulama", depo: KullaniciDeposu, basarili_cb):
        super().__init__(master, fg_color=C["kart"], corner_radius=18,
                         border_width=1, border_color=C["kenar"])
        self.depo = depo
        self.basarili_cb = basarili_cb
        self.mod = "giris"
        self.basarisiz = 0
        self.kilit_bitis = 0.0
        self._job: str | None = None
        px = 36

        self._kalkan_ciz().pack(pady=(26, 6))
        ctk.CTkLabel(self, text="AuthShield", font=f(26, True), text_color=C["metin"]).pack()
        ctk.CTkLabel(self, text="Güvenli kullanıcı girişi", font=f(12),
                     text_color=C["soluk"]).pack(pady=(0, 16))

        self.mod_secici = ctk.CTkSegmentedButton(
            self, values=["Giriş Yap", "Kayıt Ol"], command=self._mod_degistir, height=34,
            fg_color=C["girdi"], selected_color=C["mavi"], selected_hover_color=C["mavi_h"],
            unselected_color=C["girdi"], unselected_hover_color=C["gri"], font=f(12, True))
        self.mod_secici.set("Giriş Yap")
        self.mod_secici.pack(fill="x", padx=px, pady=(0, 16))

        ctk.CTkLabel(self, text="Kullanıcı Adı", font=f(11, True),
                     text_color=C["soluk"]).pack(anchor="w", padx=px)
        self.isim_entry = self._girdi("Kullanıcı adınız")
        self.isim_entry.pack(fill="x", padx=px, pady=(4, 10))

        ctk.CTkLabel(self, text="Şifre", font=f(11, True),
                     text_color=C["soluk"]).pack(anchor="w", padx=px)
        self.sifre_entry = self._girdi("Şifreniz", show="*")
        self.sifre_entry.pack(fill="x", padx=px, pady=(4, 6))
        self.sifre_entry.bind("<KeyRelease>", self._guc_guncelle)

        self.guc_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.guc_bar = ctk.CTkProgressBar(self.guc_frame, height=6, fg_color=C["girdi"])
        self.guc_bar.set(0)
        self.guc_bar.pack(fill="x")
        self.guc_label = ctk.CTkLabel(self.guc_frame, text="", font=f(11), text_color=C["soluk"],
                                      wraplength=330, justify="left")
        self.guc_label.pack(anchor="w", pady=(4, 0))

        self.goster_check = ctk.CTkCheckBox(self, text="Şifreyi göster", font=f(12),
                                            command=self._sifre_goster_gizle, checkbox_width=18,
                                            checkbox_height=18, corner_radius=5)
        self.goster_check.pack(anchor="w", padx=px, pady=(8, 4))

        satir = ctk.CTkFrame(self, fg_color="transparent")
        satir.pack(fill="x", padx=px - 4, pady=(12, 0))
        satir.columnconfigure(0, weight=3)
        satir.columnconfigure(1, weight=2)
        self.ana_buton = ctk.CTkButton(
            satir, text="Giriş Yap", font=f(14, True), height=40, corner_radius=10,
            fg_color=C["mavi"], hover_color=C["mavi_h"], command=self._gonder)
        self.ana_buton.grid(row=0, column=0, padx=4, sticky="ew")
        ctk.CTkButton(
            satir, text="Temizle", font=f(13, True), height=40, corner_radius=10,
            fg_color=C["gri"], hover_color=C["gri_h"], command=self._temizle
        ).grid(row=0, column=1, padx=4, sticky="ew")

        self.durum = ctk.CTkLabel(self, text="", font=f(12, True), wraplength=330)
        self.durum.pack(pady=(14, 4), padx=10)
        ctk.CTkLabel(self, text="Şifreler PBKDF2-SHA256 ile tuzlanıp saklanır.",
                     font=f(10), text_color=C["soluk"]).pack(side="bottom", pady=(0, 14))

        for w in (self.isim_entry, self.sifre_entry):
            w.bind("<Return>", self._gonder)
        self.isim_entry.focus_set()


    def _girdi(self, placeholder: str, show: str = "") -> ctk.CTkEntry:
        return ctk.CTkEntry(self, placeholder_text=placeholder, show=show, height=40,
                            corner_radius=10, fg_color=C["girdi"], border_color=C["kenar"],
                            border_width=1, font=f(13))

    def _kalkan_ciz(self) -> ctk.CTkCanvas:
        c = ctk.CTkCanvas(self, width=64, height=72, bg=C["kart"], highlightthickness=0)
        dis = [32, 3, 59, 14, 59, 37, 32, 68, 5, 37, 5, 14]
        ic = [32, 10, 53, 18, 53, 36, 32, 61, 11, 36, 11, 18]
        c.create_polygon(dis, fill=C["mavi_h"], outline="")
        c.create_polygon(ic, fill=C["mavi"], outline="")
        c.create_line(21, 36, 29, 44, 44, 26, fill="white", width=5, capstyle="round", joinstyle="round")
        return c

    def _durum(self, metin: str, tur: str = "bilgi") -> None:
        renk = {"bilgi": C["metin"], "basari": C["basari"], "uyari": C["uyari"], "hata": C["hata"]}[tur]
        self.durum.configure(text=metin, text_color=renk)

    def _sifre_goster_gizle(self) -> None:
        self.sifre_entry.configure(show="" if self.goster_check.get() else "*")

    def _temizle(self) -> None:
        self.isim_entry.delete(0, "end")
        self.sifre_entry.delete(0, "end")
        self.goster_check.deselect()
        self.sifre_entry.configure(show="*")
        self.durum.configure(text="")
        self._guc_guncelle()

    def _mod_degistir(self, secim: str) -> None:
        kayit = secim == "Kayıt Ol"
        self.mod = "kayit" if kayit else "giris"
        self.ana_buton.configure(text="Kayıt Ol" if kayit else "Giriş Yap")
        self.durum.configure(text="")
        if kayit:
            self.guc_frame.pack(fill="x", padx=36, pady=(2, 0), after=self.sifre_entry)
            self._guc_guncelle()
        else:
            self.guc_frame.pack_forget()
        self.master.ortala(470, 680 if kayit else 610)

    def _guc_guncelle(self, _event=None) -> None:
        if self.mod != "kayit":
            return
        kontroller = sifre_kontrolleri(self.sifre_entry.get())
        saglanan = sum(ok for ok, _ in kontroller)
        self.guc_bar.set(saglanan / len(kontroller))
        renk = (C["hata"], C["hata"], C["uyari"], C["uyari"], C["basari"], C["basari"])[saglanan]
        self.guc_bar.configure(progress_color=renk)
        eksik = [m for ok, m in kontroller if not ok]
        self.guc_label.configure(
            text="Güçlü şifre" if not eksik else "Eksik: " + ", ".join(eksik),
            text_color=C["basari"] if not eksik else C["soluk"])


    def _gonder(self, _event=None) -> None:
        if time.monotonic() < self.kilit_bitis:
            return
        ad = self.isim_entry.get().strip()
        sifre = self.sifre_entry.get()
        if not ad or not sifre:
            self._durum("Kullanıcı adı veya şifre boş olamaz", "uyari")
            return
        (self._kayit if self.mod == "kayit" else self._giris)(ad, sifre)

    def _giris(self, ad: str, sifre: str) -> None:
        if self.depo.dogrula(ad, sifre):
            self.basarisiz = 0
            self.ana_buton.configure(state="disabled")
            self._durum("Giriş başarılı! Yönlendiriliyorsunuz...", "basari")
            self._job = self.after(700, lambda: self.basarili_cb(ad))
            return
        self.basarisiz += 1
        kalan = self.MAX_DENEME - self.basarisiz
        if kalan <= 0:
            self.kilit_bitis = time.monotonic() + self.KILIT_SN
            self.ana_buton.configure(state="disabled")
            self._kilit_sayaci()
        else:
            self._durum(f"Kullanıcı adı veya şifre hatalı. Kalan deneme: {kalan}", "hata")

    def _kayit(self, ad: str, sifre: str) -> None:
        if not (3 <= len(ad) <= 20 and ad.replace("_", "").isalnum()):
            self._durum("Kullanıcı adı 3-20 karakter olmalı (harf, rakam, _)", "uyari")
            return
        eksik = [m for ok, m in sifre_kontrolleri(sifre) if not ok]
        if eksik:
            self._durum("Şifre zayıf. Eksik: " + ", ".join(eksik), "hata")
            return
        ok, mesaj = self.depo.kayit_ol(ad, sifre)
        if not ok:
            self._durum(mesaj, "hata")
            return
        self.mod_secici.set("Giriş Yap")
        self._mod_degistir("Giriş Yap")
        self.sifre_entry.delete(0, "end")
        self._durum(mesaj, "basari")

    def _kilit_sayaci(self) -> None:
        kalan = int(self.kilit_bitis - time.monotonic()) + 1
        if kalan > 0:
            self._durum(f"Çok fazla hatalı deneme. {kalan} sn sonra tekrar deneyin.", "hata")
            self._job = self.after(500, self._kilit_sayaci)
        else:
            self.basarisiz = 0
            self.ana_buton.configure(state="normal")
            self._durum("Tekrar deneyebilirsiniz.", "bilgi")

    def destroy(self) -> None:
        if self._job:
            self.after_cancel(self._job)
            self._job = None
        super().destroy()



class TrieEkrani(ctk.CTkFrame):
    R0, X0, Y0, K0 = 22, 62, 88, 50
    MIN_OLCEK, MAX_OLCEK = 0.4, 2.2
    MAX_KELIME = 20
    ORNEK = ["kedi", "kedilere", "kelebek", "kalem", "kale", "kitap", "kit", "ağaç", "ağ"]

    def __init__(self, master: "Uygulama", kullanici: str, cikis_cb):
        super().__init__(master, fg_color=C["arka"], corner_radius=0)
        self.trie = Trie()
        self.vurgu: set[str] = set()
        self.gizli: set[str] = set()
        self.olcek = 1.0
        self._job: str | None = None
        self._tween_job: str | None = None
        self._bekleyen = None
        self._gosterilen: dict[str, tuple[float, float]] = {}
        self._hedef: dict[str, tuple[float, float]] = {}
        self._dugumler: dict[str, TrieDugumu] = {}
        self._icerik_boyut = (1.0, 1.0)
        self._ipucu_dolu = False
        self.oto = True

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self._sol_menu(kullanici, cikis_cb)
        self._icerik()
        self._durum("Bir kelime yazıp Enter'a basarak başla.", "bilgi")
        self._liste_guncelle()


    def _buton(self, ust, metin, komut, renk, hover, **kw):
        return ctk.CTkButton(ust, text=metin, command=komut, height=36, corner_radius=10,
                             fg_color=renk, hover_color=hover, font=f(13, True), **kw)

    def _bolum(self, ust, metin):
        ctk.CTkLabel(ust, text=metin, font=f(10, True), text_color=C["soluk"]
                     ).pack(anchor="w", padx=22, pady=(14, 4))

    def _logo(self, ust) -> ctk.CTkCanvas:
        c = ctk.CTkCanvas(ust, width=38, height=38, bg=C["panel"], highlightthickness=0)
        for (a, b) in (((19, 7), (9, 28)), ((19, 7), (29, 28))):
            c.create_line(*a, *b, fill=C["dugum_kenar"], width=2)
        c.create_oval(12, 2, 26, 16, fill=C["mavi"], outline="")
        c.create_oval(3, 22, 15, 34, fill=C["dugum"], outline=C["dugum_kenar"], width=2)
        c.create_oval(23, 22, 35, 34, fill=C["basari"], outline="")
        return c

    def _sol_menu(self, kullanici: str, cikis_cb) -> None:
        yan = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color=C["panel"])
        yan.grid(row=0, column=0, sticky="nsew")
        yan.pack_propagate(False)

        self._buton(yan, "Oturumu Kapat", cikis_cb, C["gri"], C["gri_h"]
                    ).pack(side="bottom", fill="x", padx=22, pady=(8, 20))

        ust = ctk.CTkFrame(yan, fg_color="transparent")
        ust.pack(fill="x", padx=22, pady=(22, 0))
        self._logo(ust).pack(side="left")
        yazi = ctk.CTkFrame(ust, fg_color="transparent")
        yazi.pack(side="left", padx=10)
        ctk.CTkLabel(yazi, text="Trie Visualizer", font=f(17, True), text_color=C["metin"]).pack(anchor="w")
        ctk.CTkLabel(yazi, text=f"Oturum: {kullanici}", font=f(11), text_color=C["soluk"]).pack(anchor="w")

        self._bolum(yan, "KELİME / ÖNEK")
        self.giris = ctk.CTkEntry(yan, placeholder_text="Örn: kitap", height=40, corner_radius=10,
                                  fg_color=C["girdi"], border_color=C["kenar"], border_width=1, font=f(13))
        self.giris.pack(fill="x", padx=22)
        self.giris.bind("<Return>", lambda _e: self.ekle())

        self._buton(yan, "Kelime Ekle", self.ekle, C["mavi"], C["mavi_h"]).pack(fill="x", padx=22, pady=(10, 6))
        satir = ctk.CTkFrame(yan, fg_color="transparent")
        satir.pack(fill="x", padx=22)
        satir.columnconfigure((0, 1), weight=1)
        self._buton(satir, "Ara", self.ara, C["yesil_btn"], C["yesil_btn_h"]
                    ).grid(row=0, column=0, padx=(0, 4), sticky="ew")
        self._buton(satir, "Sil", self.sil, C["kirmizi_btn"], C["kirmizi_btn_h"]
                    ).grid(row=0, column=1, padx=(4, 0), sticky="ew")
        self._buton(yan, "Önek ile Ara", self.onek_ara, C["mor"], C["mor_h"]).pack(fill="x", padx=22, pady=6)

        self._bolum(yan, "ARAÇLAR")
        satir2 = ctk.CTkFrame(yan, fg_color="transparent")
        satir2.pack(fill="x", padx=22)
        satir2.columnconfigure((0, 1), weight=1)
        self._buton(satir2, "Örnek Veri", self.ornek_yukle, C["gri"], C["gri_h"]
                    ).grid(row=0, column=0, padx=(0, 4), sticky="ew")
        self._buton(satir2, "Temizle", self.agaci_temizle, C["gri"], C["gri_h"]
                    ).grid(row=0, column=1, padx=(4, 0), sticky="ew")

        hiz = ctk.CTkFrame(yan, fg_color="transparent")
        hiz.pack(fill="x", padx=22, pady=(12, 0))
        ctk.CTkLabel(hiz, text="Animasyon hızı", font=f(11), text_color=C["soluk"]).pack(side="left")
        self.hiz = ctk.CTkSlider(hiz, from_=60, to=500, number_of_steps=22, width=130, height=14)
        self.hiz.set(320)
        self.hiz.pack(side="right")

        kartlar = ctk.CTkFrame(yan, fg_color="transparent")
        kartlar.pack(fill="x", padx=22, pady=(16, 0))
        kartlar.columnconfigure((0, 1), weight=1)
        self.sayi_kelime = self._istatistik(kartlar, 0, "Kelime", C["basari"])
        self.sayi_dugum = self._istatistik(kartlar, 1, "Düğüm", C["mavi"])

        self._bolum(yan, "KELİMELER")
        self.liste = ctk.CTkTextbox(yan, height=80, fg_color=C["girdi"], border_color=C["kenar"],
                                    border_width=1, corner_radius=10, font=f(13), state="disabled")
        self.liste.pack(fill="both", expand=True, padx=22, pady=(0, 4))

    def _istatistik(self, ust, kolon, baslik, renk) -> ctk.CTkLabel:
        kart = ctk.CTkFrame(ust, fg_color=C["girdi"], corner_radius=10, border_width=1, border_color=C["kenar"])
        kart.grid(row=0, column=kolon, padx=(0, 4) if kolon == 0 else (4, 0), sticky="ew")
        sayi = ctk.CTkLabel(kart, text="0", font=f(22, True), text_color=renk)
        sayi.pack(pady=(8, 0))
        ctk.CTkLabel(kart, text=baslik, font=f(10), text_color=C["soluk"]).pack(pady=(0, 8))
        return sayi

    def _icerik(self) -> None:
        ic = ctk.CTkFrame(self, fg_color=C["arka"], corner_radius=0)
        ic.grid(row=0, column=1, sticky="nsew")
        ic.rowconfigure(2, weight=1)
        ic.columnconfigure(0, weight=1)

        baslik = ctk.CTkFrame(ic, fg_color="transparent")
        baslik.grid(row=0, column=0, sticky="ew", padx=22, pady=(18, 2))
        ctk.CTkLabel(baslik, text="Trie (Sözlük Ağacı)", font=f(20, True),
                     text_color=C["metin"]).pack(side="left")
        lejant = ctk.CTkFrame(baslik, fg_color="transparent")
        lejant.pack(side="right")
        for renk, ad in ((C["dugum_kenar"], "Düğüm"), (C["basari"], "Kelime sonu"), (C["yol"], "Aktif yol")):
            ctk.CTkLabel(lejant, text="●", text_color=renk, font=f(14)).pack(side="left")
            ctk.CTkLabel(lejant, text=ad, font=f(11), text_color=C["soluk"]).pack(side="left", padx=(3, 12))

        arac = ctk.CTkFrame(ic, fg_color="transparent")
        arac.grid(row=1, column=0, sticky="ew", padx=22, pady=(4, 8))
        for metin, komut, gen in (("−", lambda: self._olcek_carp(1 / 1.15), 34),
                                  ("+", lambda: self._olcek_carp(1.15), 34)):
            ctk.CTkButton(arac, text=metin, width=gen, height=30, corner_radius=8, font=f(15, True),
                          fg_color=C["gri"], hover_color=C["gri_h"], command=komut).pack(side="left", padx=(0, 6))
        self.zoom_etiket = ctk.CTkLabel(arac, text="%100", width=48, font=f(12, True), text_color=C["metin"])
        self.zoom_etiket.pack(side="left", padx=(0, 6))
        ctk.CTkButton(arac, text="Sığdır", width=70, height=30, corner_radius=8, font=f(12, True),
                      fg_color=C["gri"], hover_color=C["gri_h"], command=self.sigdir).pack(side="left")
        ctk.CTkLabel(arac, text="Ctrl + tekerlek: yakınlaştır   •   sürükle: gezin   •   düğüme çift tık: önek seç",
                     font=f(11), text_color=C["soluk"]).pack(side="right")

        kasa = ctk.CTkFrame(ic, fg_color=C["canvas"], corner_radius=14, border_width=1, border_color=C["kenar"])
        kasa.grid(row=2, column=0, sticky="nsew", padx=22)
        kasa.rowconfigure(0, weight=1)
        kasa.columnconfigure(0, weight=1)
        self.canvas = ctk.CTkCanvas(kasa, bg=C["canvas"], highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=3, pady=3)
        sy = ctk.CTkScrollbar(kasa, command=self.canvas.yview, width=12)
        sy.grid(row=0, column=1, sticky="ns", pady=8, padx=(0, 4))
        sx = ctk.CTkScrollbar(kasa, orientation="horizontal", command=self.canvas.xview, height=12)
        sx.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 4))
        self.canvas.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)

        self.canvas.bind("<Configure>", lambda _e: self._yapi_degisti(False))
        self.canvas.bind("<ButtonPress-1>", lambda e: self.canvas.scan_mark(e.x, e.y))
        self.canvas.bind("<B1-Motion>", lambda e: self.canvas.scan_dragto(e.x, e.y, gain=1))
        self.canvas.bind("<Enter>", lambda _e: self.canvas.focus_set())
        for olay in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.canvas.bind(olay, self._tekerlek)

        cubuk = ctk.CTkFrame(ic, fg_color=C["kart"], corner_radius=12, border_width=1, border_color=C["kenar"])
        cubuk.grid(row=3, column=0, sticky="ew", padx=22, pady=(10, 18))
        self.durum_nokta = ctk.CTkLabel(cubuk, text="●", font=f(14), text_color=C["mavi"])
        self.durum_nokta.pack(side="left", padx=(14, 6), pady=10)
        self.durum = ctk.CTkLabel(cubuk, text="", font=f(13, True), anchor="w", justify="left", wraplength=520)
        self.durum.pack(side="left", fill="x", expand=True)
        self.ipucu = ctk.CTkLabel(cubuk, text="", font=f(12), text_color=C["soluk"])
        self.ipucu.pack(side="right", padx=14)
        cubuk.bind("<Configure>", lambda e: self.durum.configure(wraplength=max(220, e.width - 360)))


    def _durum(self, metin: str, tur: str = "bilgi") -> None:
        self.durum.configure(text=metin, text_color=C["metin"])
        self.durum_nokta.configure(text_color=DURUM_RENK[tur])

    def _liste_guncelle(self) -> None:
        self.sayi_kelime.configure(text=str(self.trie.kelime_sayisi))
        self.sayi_dugum.configure(text=str(self.trie.dugum_sayisi()))
        self.liste.configure(state="normal")
        self.liste.delete("1.0", "end")
        self.liste.insert("1.0", "\n".join(self.trie.tum_kelimeler()))
        self.liste.configure(state="disabled")

    def _kelime_al(self) -> str | None:
        self._animasyonu_durdur()
        kelime = kucult(self.giris.get().strip())
        if not kelime:
            self._durum("Lütfen bir kelime girin.", "uyari")
        elif not kelime.isalpha():
            self._durum("Yalnızca harf kullanabilirsiniz (boşluk, rakam ve sembol olmaz).", "uyari")
        elif len(kelime) > self.MAX_KELIME:
            self._durum(f"En fazla {self.MAX_KELIME} harf girebilirsiniz.", "uyari")
        else:
            return kelime
        return None

    def _onek_sec(self, onek: str) -> None:
        self.giris.delete(0, "end")
        self.giris.insert(0, onek)
        self.giris.focus_set()
        self._durum(f"'{onek}' kutuya yazıldı. Önek ile Ara'ya basabilirsin." if onek else "Kök seçildi.", "bilgi")

    def _hover(self, onek: str | None) -> None:
        if onek is None:
            self.canvas.configure(cursor="")
            self.ipucu.configure(text="")
            return
        self.canvas.configure(cursor="hand2")
        self._ipucu_dolu = True
        if not onek:
            self.ipucu.configure(text="Kök düğüm")
            return
        altta = len(self.trie.onek_ile_kelimeler(onek))
        sonu = " • kelime sonu" if self.trie.ara(onek) else ""
        self.ipucu.configure(text=f"'{onek}'  •  seviye {len(onek)}  •  altında {altta} kelime{sonu}")


    def _olcek_yaz(self) -> None:
        self.zoom_etiket.configure(text=f"%{round(self.olcek * 100)}")

    def _olcek_carp(self, katsayi: float) -> None:
        self.oto = False
        self.olcek = max(self.MIN_OLCEK, min(self.MAX_OLCEK, self.olcek * katsayi))
        self._olcek_yaz()
        self._yapi_degisti(False)

    def sigdir(self) -> None:
        self.oto = True
        self._yapi_degisti(False)
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

    def _otomatik_olcek(self) -> None:
        """Ağaç görünür alana sığmıyorsa ölçeği küçültür (en çok %40'a kadar)."""
        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        if not self.oto or cw < 50 or ch < 50:
            return
        _, _, (iw, ih) = self._hedef_hesapla(1.0)
        yeni = max(self.MIN_OLCEK, min(1.0, (cw - 10) / iw, (ch - 10) / ih))
        if abs(yeni - self.olcek) > 1e-3:
            self.olcek = yeni
            self._olcek_yaz()

    def _tekerlek(self, e) -> None:
        yukari = e.num == 4 or e.delta > 0
        if e.state & 0x4:
            self._olcek_carp(1.1 if yukari else 1 / 1.1)
        elif e.state & 0x1:
            self.canvas.xview_scroll(-1 if yukari else 1, "units")
        else:
            self.canvas.yview_scroll(-1 if yukari else 1, "units")


    def _gecikme(self) -> int:
        return int(580 - self.hiz.get())

    def _animasyonu_durdur(self) -> None:
        """Çalışan animasyonu keser; bekleyen işlem (ör. silme) varsa hemen uygular."""
        if self._job:
            self.after_cancel(self._job)
            self._job = None
        gizliydi = bool(self.gizli)
        self.gizli = set()
        bekleyen, self._bekleyen = self._bekleyen, None
        if bekleyen:
            bekleyen()
        elif gizliydi:
            self.ciz()

    def _yol_animasyonu(self, yol: str, bitince=None) -> None:
        self._animasyonu_durdur()
        onekler = [yol[:i] for i in range(len(yol) + 1)]
        yeniler = set(self._yeni_bekleyen)
        self._yeni_bekleyen = set()
        self._bekleyen = bitince

        def adim(i: int) -> None:
            self.vurgu = set(onekler[: i + 1])
            self.gizli = {p for p in yeniler if len(p) > i}
            self.ciz()
            if i + 1 < len(onekler):
                self._job = self.after(self._gecikme(), lambda: adim(i + 1))
            else:
                self._job = None
                son, self._bekleyen = self._bekleyen, None
                if son:
                    son()

        adim(0)

    _yeni_bekleyen: set[str] = set()


    def ekle(self) -> None:
        kelime = self._kelime_al()
        if not kelime:
            return
        n = self.trie.eslesen_uzunluk(kelime)
        yeni = self.trie.ekle(kelime)
        self.giris.delete(0, "end")
        self._liste_guncelle()
        self._yapi_degisti(True)
        self._yeni_bekleyen = {kelime[:i] for i in range(n + 1, len(kelime) + 1)}
        self._yol_animasyonu(kelime)
        if yeni:
            self._durum(f"'{kelime}' eklendi.", "basari")
        else:
            self._durum(f"'{kelime}' zaten ağaçta var.", "uyari")

    def ara(self) -> None:
        kelime = self._kelime_al()
        if not kelime:
            return
        n = self.trie.eslesen_uzunluk(kelime)
        self._yol_animasyonu(kelime[:n])
        if self.trie.ara(kelime):
            self._durum(f"'{kelime}' bulundu.", "basari")
        elif n == len(kelime):
            self._durum(f"'{kelime}' bir kelime değil, yalnızca başka kelimelerin öneki.", "uyari")
        else:
            self._durum(f"'{kelime}' bulunamadı ({n + 1}. harften sonra yol yok).", "hata")

    def sil(self) -> None:
        kelime = self._kelime_al()
        if not kelime:
            return
        if not self.trie.ara(kelime):
            self._yol_animasyonu(kelime[: self.trie.eslesen_uzunluk(kelime)])
            self._durum(f"'{kelime}' ağaçta yok, silinemedi.", "hata")
            return

        def bitir() -> None:
            self.trie.sil(kelime)
            self.vurgu = set()
            self._liste_guncelle()
            self._yapi_degisti(True)
            self._durum(f"'{kelime}' silindi.", "basari")

        self.giris.delete(0, "end")
        self._yol_animasyonu(kelime, bitir)
        self._durum(f"'{kelime}' siliniyor...", "bilgi")

    def onek_ara(self) -> None:
        onek = self._kelime_al()
        if not onek:
            return
        sonuc = self.trie.onek_ile_kelimeler(onek)
        if not sonuc:
            self._yol_animasyonu(onek[: self.trie.eslesen_uzunluk(onek)])
            self._durum(f"'{onek}' ile başlayan kelime yok.", "hata")
            return

        def alt_agaci_goster() -> None:
            for k in sonuc:
                self.vurgu.update(k[:i] for i in range(len(k) + 1))
            self.ciz()

        self._yol_animasyonu(onek, alt_agaci_goster)
        ornek = ", ".join(sonuc[:8]) + (" ..." if len(sonuc) > 8 else "")
        self._durum(f"'{onek}' ile başlayan {len(sonuc)} kelime: {ornek}", "basari")

    def ornek_yukle(self) -> None:
        self._animasyonu_durdur()
        for k in self.ORNEK:
            self.trie.ekle(k)
        self.vurgu = set()
        self._liste_guncelle()
        self._yapi_degisti(True)
        self._durum("Örnek kelimeler yüklendi. Ortak önekler (ke-, ka-, ki-) tek dalı paylaşıyor.", "basari")

    def agaci_temizle(self) -> None:
        self._animasyonu_durdur()
        self.trie.temizle()
        self.vurgu = set()
        self._liste_guncelle()
        self._yapi_degisti(True)
        self._durum("Ağaç temizlendi.", "bilgi")

  
    def _olc(self, dugum: TrieDugumu, onek: str, genislik: dict[str, int]) -> int:
        if not dugum.cocuklar:
            w = 1
        else:
            w = sum(self._olc(c, onek + h, genislik) for h, c in sorted(dugum.cocuklar.items()))
        genislik[onek] = w
        return w

    def _yerles(self, dugum, onek, sol, derinlik, genislik, poz) -> None:
        w = genislik[onek]
        poz[onek] = (sol + w / 2, derinlik, dugum)
        x = sol
        for harf, cocuk in sorted(dugum.cocuklar.items()):
            self._yerles(cocuk, onek + harf, x, derinlik + 1, genislik, poz)
            x += genislik[onek + harf]

    def _hedef_hesapla(self, olcek: float):
        """Her önek için piksel konumu, düğüm nesneleri ve içerik boyutunu hesaplar."""
        xa, ya, k = self.X0 * olcek, self.Y0 * olcek, self.K0 * olcek
        genislik: dict[str, int] = {}
        poz: dict[str, tuple[float, int, TrieDugumu]] = {}
        self._olc(self.trie.kok, "", genislik)
        self._yerles(self.trie.kok, "", 0, 0, genislik, poz)
        iw = genislik[""] * xa + 2 * k
        ih = max(d for _, d, _ in poz.values()) * ya + 2 * k
        cw = max(self.canvas.winfo_width(), 1)
        ofset = max(0, (cw - iw) / 2)
        hedef = {o: (ofset + k + ux * xa, k + d * ya) for o, (ux, d, _) in poz.items()}
        dugumler = {o: n for o, (_, _, n) in poz.items()}
        return hedef, dugumler, (iw, ih)

    def _yapi_degisti(self, animasyonlu: bool) -> None:
        """Ağaç ya da ölçek değişti: yeni konumları hesapla, düğümleri oraya kaydır."""
        if self._tween_job:
            self.after_cancel(self._tween_job)
            self._tween_job = None
        self._otomatik_olcek()
        hedef, self._dugumler, self._icerik_boyut = self._hedef_hesapla(self.olcek)
        onceki = self._gosterilen
        self._hedef = hedef
        if not animasyonlu or not onceki:
            self._gosterilen = dict(hedef)
            self.ciz()
            return

        basla = {}
        for onek, hxy in hedef.items():
            a = onek
            while a and a not in onceki:
                a = a[:-1]
            basla[onek] = onceki.get(a, hxy)

        toplam = 10

        def kare(i: int) -> None:
            t = i / toplam
            e = 1 - (1 - t) ** 3
            self._gosterilen = {
                o: (basla[o][0] + (h[0] - basla[o][0]) * e, basla[o][1] + (h[1] - basla[o][1]) * e)
                for o, h in hedef.items()
            }
            self.ciz()
            self._tween_job = self.after(16, lambda: kare(i + 1)) if i < toplam else None

        kare(1)


    def ciz(self) -> None:
        c = self.canvas
        c.delete("all")
        if self._ipucu_dolu:
            self._ipucu_dolu = False
            self.ipucu.configure(text="")
            c.configure(cursor="")
        if not self._gosterilen:
            self._yapi_degisti(False)
            return
        s = self.olcek
        r = self.R0 * s
        cw, ch = max(c.winfo_width(), 1), max(c.winfo_height(), 1)
        iw, ih = self._icerik_boyut
        sw, sh = max(cw, iw), max(ch, ih)


        adim = 34
        if (sw / adim) * (sh / adim) < 3000:
            for gx in range(adim // 2, int(sw), adim):
                for gy in range(adim // 2, int(sh), adim):
                    c.create_rectangle(gx, gy, gx + 1, gy + 1, fill=C["nokta"], outline="")


        for onek in self.vurgu:
            if onek in self.gizli or onek not in self._gosterilen:
                continue
            x, y = self._gosterilen[onek]
            for gr, t in ((r + 15 * s, 0.10), (r + 10 * s, 0.20), (r + 5 * s, 0.35)):
                c.create_oval(x - gr, y - gr, x + gr, y + gr, fill=karistir(C["canvas"], C["yol"], t), outline="")


        for onek, (x1, y1) in self._gosterilen.items():
            if not onek or onek in self.gizli:
                continue
            x0, y0 = self._gosterilen[onek[:-1]]
            nokta = egri_noktalari(x0, y0, x1, y1)
            if onek in self.vurgu:
                c.create_line(*nokta, fill=karistir(C["canvas"], C["yol"], 0.35), width=8 * s,
                              capstyle="round", joinstyle="round")
                c.create_line(*nokta, fill=C["yol"], width=max(2, 3 * s), capstyle="round", joinstyle="round")
            else:
                c.create_line(*nokta, fill=C["kenar"], width=max(1.5, 2.2 * s),
                              capstyle="round", joinstyle="round")


        yazi = (FONT, max(7, round(13 * s)), "bold")
        kok_yazi = (FONT, max(7, round(10 * s)), "bold")
        for onek, (x, y) in self._gosterilen.items():
            if onek in self.gizli:
                continue
            dugum = self._dugumler[onek]
            aktif = onek in self.vurgu
            etiket = f"n_{onek}"
            etiketler = (etiket, "dugum")

            c.create_oval(x - r + 2, y - r + 5, x + r + 2, y + r + 5, fill="#05080c", outline="")  # gölge
            if dugum.kelime_sonu:
                g = r + 6 * s
                c.create_oval(x - g, y - g, x + g, y + g, outline=C["basari"], width=max(1.5, 2.2 * s), tags=etiketler)

            if not onek:
                dolgu, kenar, metin = (C["yol"] if aktif else C["mavi"]), "#bfdbfe", "white"
            elif aktif:
                dolgu, kenar, metin = C["yol"], "#fef3c7", "#1b1203"
            elif dugum.kelime_sonu:
                dolgu, kenar, metin = "#15803d", "#bbf7d0", "white"
            else:
                dolgu, kenar, metin = C["dugum"], C["dugum_kenar"], "#f1f5f9"
            c.create_oval(x - r, y - r, x + r, y + r, fill=dolgu, outline=kenar,
                          width=max(1.5, 2.2 * s), tags=etiketler)
            c.create_text(x, y, text=onek[-1] if onek else "Kök", fill=metin,
                          font=yazi if onek else kok_yazi, tags=etiketler)

            c.tag_bind(etiket, "<Enter>", lambda _e, o=onek: self._hover(o))
            c.tag_bind(etiket, "<Leave>", lambda _e: self._hover(None))
            c.tag_bind(etiket, "<Double-Button-1>", lambda _e, o=onek: self._onek_sec(o))

        if not self.trie.kelime_sayisi:
            c.create_text(cw / 2, self.K0 * s + 120, fill=C["soluk"], font=f(14, True),
                          text="Ağaç şu an boş")
            c.create_text(cw / 2, self.K0 * s + 148, fill=C["soluk"], font=f(12),
                          text="Soldan bir kelime ekle ya da 'Örnek Veri'ye bas.")

        c.configure(scrollregion=(0, 0, sw, sh))

    def destroy(self) -> None:
        for ad in ("_job", "_tween_job"):
            is_id = getattr(self, ad)
            if is_id:
                self.after_cancel(is_id)
                setattr(self, ad, None)
        self._bekleyen = None
        super().destroy()



class Uygulama(ctk.CTk):
    def __init__(self):
        super().__init__()
        yazi_tipi_sec()
        self.configure(fg_color=C["arka"])
        try:
            self.attributes("-alpha", 0.97)
        except Exception:
            pass
        self.depo = KullaniciDeposu(VERI_DOSYASI)
        self.aktif: ctk.CTkFrame | None = None
        self.giris_goster()

    def ortala(self, genislik: int, yukseklik: int) -> None:
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        genislik, yukseklik = min(genislik, sw - 40), min(yukseklik, sh - 90)
        x, y = int(sw / 2 - genislik / 2), max(0, int(sh / 2 - yukseklik / 2) - 20)
        self.geometry(f"{genislik}x{yukseklik}+{x}+{y}")

    def _goster(self, ekran: ctk.CTkFrame, baslik: str, boyut: tuple[int, int],
                kenar: int = 0, min_boyut: tuple[int, int] = (0, 0)) -> None:
        if self.aktif is not None:
            self.aktif.destroy()
        self.aktif = ekran
        self.title(baslik)
        self.minsize(*min_boyut)
        self.ortala(*boyut)
        ekran.pack(fill="both", expand=True, padx=kenar, pady=kenar)

    def giris_goster(self) -> None:
        self._goster(GirisEkrani(self, self.depo, self.ana_panel_goster),
                     "AuthShield - Giriş", (470, 610), kenar=22)

    def ana_panel_goster(self, kullanici: str) -> None:
        self._goster(TrieEkrani(self, kullanici, self.giris_goster),
                     "Trie Visualizer - Algoritma ve Veri Yapıları Görselleştirme Motoru",
                     (1240, 760), min_boyut=(1020, 640))


if __name__ == "__main__":
    Uygulama().mainloop()