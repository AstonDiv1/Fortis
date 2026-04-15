import customtkinter as ctk
from tkinter import messagebox, StringVar
import pyperclip
import threading
import time
import uuid
from fortis.vault import vault_exists, create_vault, load_vault, save_vault
from fortis.generator import generate_password, password_strength

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ─── Color palette ─────────────────────────────────────────────────────────────
BG        = "#0d0d0f"
PANEL     = "#111114"
CARD      = "#18181d"
BORDER    = "#2a2a35"
ACCENT    = "#c8a96e"       # gold
ACCENT2   = "#7c6daf"       # violet
TEXT      = "#e8e6e0"
SUBTEXT   = "#7a7880"
RED       = "#e05c5c"
GREEN     = "#4ec994"
FONT_MAIN = ("Courier New", 13)
FONT_HEAD = ("Courier New", 22, "bold")
FONT_SUB  = ("Courier New", 11)


# ──────────────────────────────────────────────────────────────────────────────
class FortisApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Fortis")
        self.geometry("960x640")
        self.minsize(860, 560)
        self.configure(fg_color=BG)
        self.master_password = None
        self.entries = []
        self.filtered = []
        self._clipboard_timer = None

        if vault_exists():
            self._show_unlock()
        else:
            self._show_setup()

    # ── Setup screen ──────────────────────────────────────────────────────────
    def _show_setup(self):
        self._clear()
        frame = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=16,
                             border_width=1, border_color=BORDER,
                             width=420, height=480)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame, text="⬡ FORTIS", font=("Courier New", 28, "bold"),
                     text_color=ACCENT).pack(pady=(40, 4))
        ctk.CTkLabel(frame, text="Gestionnaire de mots de passe chiffré",
                     font=FONT_SUB, text_color=SUBTEXT).pack(pady=(0, 30))

        ctk.CTkLabel(frame, text="Créer un mot de passe maître",
                     font=FONT_MAIN, text_color=TEXT).pack(anchor="w", padx=40)
        pw1 = ctk.CTkEntry(frame, show="•", height=42, font=FONT_MAIN,
                           fg_color=CARD, border_color=BORDER, text_color=TEXT)
        pw1.pack(padx=40, fill="x", pady=(4, 16))

        ctk.CTkLabel(frame, text="Confirmer le mot de passe",
                     font=FONT_MAIN, text_color=TEXT).pack(anchor="w", padx=40)
        pw2 = ctk.CTkEntry(frame, show="•", height=42, font=FONT_MAIN,
                           fg_color=CARD, border_color=BORDER, text_color=TEXT)
        pw2.pack(padx=40, fill="x", pady=(4, 24))

        err = ctk.CTkLabel(frame, text="", font=FONT_SUB, text_color=RED)
        err.pack()

        def do_create():
            p1, p2 = pw1.get(), pw2.get()
            if len(p1) < 8:
                err.configure(text="⚠ Minimum 8 caractères"); return
            if p1 != p2:
                err.configure(text="⚠ Les mots de passe ne correspondent pas"); return
            create_vault(p1)
            self.master_password = p1
            self.entries = []
            self._show_main()

        ctk.CTkButton(frame, text="Créer le coffre →", height=44, font=FONT_MAIN,
                      fg_color=ACCENT, hover_color="#b8943e", text_color="#0d0d0f",
                      command=do_create).pack(padx=40, fill="x", pady=(8, 0))
        pw1.bind("<Return>", lambda e: pw2.focus())
        pw2.bind("<Return>", lambda e: do_create())

    # ── Unlock screen ─────────────────────────────────────────────────────────
    def _show_unlock(self):
        self._clear()
        frame = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=16,
                             border_width=1, border_color=BORDER,
                             width=400, height=380)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame, text="⬡ FORTIS", font=("Courier New", 28, "bold"),
                     text_color=ACCENT).pack(pady=(44, 4))
        ctk.CTkLabel(frame, text="Coffre verrouillé — entrez votre mot de passe maître",
                     font=FONT_SUB, text_color=SUBTEXT, wraplength=320).pack(pady=(0, 28))

        pw = ctk.CTkEntry(frame, show="•", height=44, font=FONT_MAIN,
                          fg_color=CARD, border_color=BORDER, text_color=TEXT,
                          placeholder_text="Mot de passe maître…")
        pw.pack(padx=40, fill="x")
        pw.focus()

        err = ctk.CTkLabel(frame, text="", font=FONT_SUB, text_color=RED)
        err.pack(pady=8)

        attempts = [0]

        def do_unlock():
            result = load_vault(pw.get())
            if result is None:
                attempts[0] += 1
                err.configure(text=f"⚠ Mot de passe incorrect ({attempts[0]} tentative{'s' if attempts[0]>1 else ''})")
                pw.delete(0, "end")
            else:
                self.master_password = pw.get()
                self.entries = result
                self._show_main()

        ctk.CTkButton(frame, text="Déverrouiller →", height=44, font=FONT_MAIN,
                      fg_color=ACCENT, hover_color="#b8943e", text_color="#0d0d0f",
                      command=do_unlock).pack(padx=40, fill="x", pady=(4, 0))
        pw.bind("<Return>", lambda e: do_unlock())

    # ── Main interface ────────────────────────────────────────────────────────
    def _show_main(self):
        self._clear()

        # ── Sidebar
        sidebar = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=0,
                               border_width=0, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="⬡ FORTIS", font=("Courier New", 18, "bold"),
                     text_color=ACCENT).pack(pady=(28, 2))
        ctk.CTkLabel(sidebar, text="v1.0 · AES-256-GCM",
                     font=("Courier New", 9), text_color=SUBTEXT).pack(pady=(0, 24))

        # Stats
        stats_frame = ctk.CTkFrame(sidebar, fg_color=CARD, corner_radius=10,
                                   border_width=1, border_color=BORDER)
        stats_frame.pack(padx=16, fill="x", pady=(0, 20))
        self._stat_count = ctk.CTkLabel(stats_frame, text=f"{len(self.entries)}",
                                        font=("Courier New", 28, "bold"), text_color=ACCENT)
        self._stat_count.pack(pady=(14, 0))
        ctk.CTkLabel(stats_frame, text="entrées stockées",
                     font=FONT_SUB, text_color=SUBTEXT).pack(pady=(0, 14))

        ctk.CTkButton(sidebar, text="+ Nouvelle entrée", height=40, font=FONT_MAIN,
                      fg_color=ACCENT, hover_color="#b8943e", text_color="#0d0d0f",
                      command=self._open_add_dialog).pack(padx=16, fill="x", pady=(0, 8))
        ctk.CTkButton(sidebar, text="⚙ Générateur", height=38, font=FONT_MAIN,
                      fg_color=CARD, hover_color=BORDER, text_color=TEXT,
                      border_width=1, border_color=BORDER,
                      command=self._open_generator).pack(padx=16, fill="x", pady=(0, 8))
        ctk.CTkButton(sidebar, text="🔒 Verrouiller", height=38, font=FONT_MAIN,
                      fg_color=CARD, hover_color=BORDER, text_color=SUBTEXT,
                      border_width=1, border_color=BORDER,
                      command=self._lock).pack(padx=16, fill="x", side="bottom", pady=20)

        # ── Main panel
        main = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        main.pack(side="left", fill="both", expand=True)

        # Topbar
        topbar = ctk.CTkFrame(main, fg_color=BG, corner_radius=0, height=64)
        topbar.pack(fill="x", padx=24, pady=(20, 0))
        topbar.pack_propagate(False)

        ctk.CTkLabel(topbar, text="Mes identifiants",
                     font=FONT_HEAD, text_color=TEXT).pack(side="left", anchor="w")

        self._search_var = StringVar()
        self._search_var.trace_add("write", lambda *_: self._refresh_list())
        search = ctk.CTkEntry(topbar, textvariable=self._search_var, height=38,
                              width=220, font=FONT_MAIN, fg_color=CARD,
                              border_color=BORDER, text_color=TEXT,
                              placeholder_text="🔍 Rechercher…")
        search.pack(side="right", anchor="e")

        # Separator
        sep = ctk.CTkFrame(main, fg_color=BORDER, height=1)
        sep.pack(fill="x", padx=24, pady=(12, 0))

        # Column headers
        headers = ctk.CTkFrame(main, fg_color=BG)
        headers.pack(fill="x", padx=24, pady=(8, 4))
        for text, w in [("Nom / Site", 200), ("Identifiant", 180), ("", 120)]:
            ctk.CTkLabel(headers, text=text, font=("Courier New", 10),
                         text_color=SUBTEXT, width=w, anchor="w").pack(side="left", padx=4)

        # Scrollable entry list
        self._list_frame = ctk.CTkScrollableFrame(main, fg_color=BG,
                                                   scrollbar_button_color=BORDER,
                                                   scrollbar_button_hover_color=ACCENT)
        self._list_frame.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        # Status bar
        self._status = ctk.CTkLabel(main, text="", font=FONT_SUB, text_color=GREEN)
        self._status.pack(pady=(0, 8))

        self._refresh_list()

    # ── Entry list ────────────────────────────────────────────────────────────
    def _refresh_list(self):
        for w in self._list_frame.winfo_children():
            w.destroy()

        query = self._search_var.get().lower() if hasattr(self, "_search_var") else ""
        self.filtered = [e for e in self.entries
                         if query in e.get("name","").lower()
                         or query in e.get("username","").lower()
                         or query in e.get("url","").lower()]

        if hasattr(self, "_stat_count"):
            self._stat_count.configure(text=str(len(self.entries)))

        if not self.filtered:
            msg = "Aucun résultat." if query else "Aucune entrée — cliquez sur + pour commencer."
            ctk.CTkLabel(self._list_frame, text=msg, font=FONT_MAIN,
                         text_color=SUBTEXT).pack(pady=40)
            return

        for entry in self.filtered:
            self._render_entry_row(entry)

    def _render_entry_row(self, entry):
        row = ctk.CTkFrame(self._list_frame, fg_color=CARD, corner_radius=10,
                           border_width=1, border_color=BORDER, height=56)
        row.pack(fill="x", pady=4)
        row.pack_propagate(False)

        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16, pady=0)

        # Icon + Name
        name_frame = ctk.CTkFrame(inner, fg_color="transparent", width=200)
        name_frame.pack(side="left")
        name_frame.pack_propagate(False)
        icon = self._site_icon(entry.get("url",""))
        ctk.CTkLabel(name_frame, text=f"{icon}  {entry.get('name','?')}",
                     font=FONT_MAIN, text_color=TEXT, anchor="w").pack(anchor="w", pady=16)

        # Username
        user_frame = ctk.CTkFrame(inner, fg_color="transparent", width=180)
        user_frame.pack(side="left")
        user_frame.pack_propagate(False)
        ctk.CTkLabel(user_frame, text=entry.get("username","—"),
                     font=FONT_SUB, text_color=SUBTEXT, anchor="w").pack(anchor="w", pady=18)

        # Buttons
        btn_frame = ctk.CTkFrame(inner, fg_color="transparent")
        btn_frame.pack(side="right")

        ctk.CTkButton(btn_frame, text="Copier", width=72, height=30, font=FONT_SUB,
                      fg_color=ACCENT2, hover_color="#6a5d9e", text_color=TEXT,
                      command=lambda e=entry: self._copy_password(e)).pack(side="left", padx=4)
        ctk.CTkButton(btn_frame, text="✏", width=36, height=30, font=FONT_SUB,
                      fg_color=CARD, hover_color=BORDER, text_color=TEXT,
                      border_width=1, border_color=BORDER,
                      command=lambda e=entry: self._open_edit_dialog(e)).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="✕", width=36, height=30, font=FONT_SUB,
                      fg_color=CARD, hover_color="#3a1a1a", text_color=RED,
                      border_width=1, border_color=BORDER,
                      command=lambda e=entry: self._delete_entry(e)).pack(side="left", padx=2)

    def _site_icon(self, url):
        u = url.lower()
        icons = {"google":"🔵","github":"⚫","facebook":"🔷","twitter":"🐦",
                 "instagram":"📸","amazon":"🟠","netflix":"🔴","discord":"💬",
                 "linkedin":"💼","apple":"🍎","microsoft":"🟦","reddit":"🟧"}
        for k, v in icons.items():
            if k in u:
                return v
        return "🔑"

    # ── Copy with auto-clear ───────────────────────────────────────────────────
    def _copy_password(self, entry):
        try:
            pyperclip.copy(entry.get("password", ""))
            self._set_status("✓ Mot de passe copié — presse-papier effacé dans 30s")
            if self._clipboard_timer:
                self._clipboard_timer.cancel()
            self._clipboard_timer = threading.Timer(30, self._clear_clipboard)
            self._clipboard_timer.start()
        except Exception:
            self._set_status("⚠ Impossible d'accéder au presse-papier")

    def _clear_clipboard(self):
        try:
            pyperclip.copy("")
        except Exception:
            pass
        self.after(0, lambda: self._set_status("🗑 Presse-papier effacé automatiquement"))

    def _set_status(self, msg):
        if hasattr(self, "_status"):
            self._status.configure(text=msg)

    # ── Add / Edit dialog ─────────────────────────────────────────────────────
    def _open_add_dialog(self):
        self._open_entry_dialog()

    def _open_edit_dialog(self, entry):
        self._open_entry_dialog(entry)

    def _open_entry_dialog(self, entry=None):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Modifier l'entrée" if entry else "Nouvelle entrée")
        dlg.geometry("460x660")
        dlg.configure(fg_color=PANEL)
        dlg.grab_set()
        dlg.resizable(False, False)

        title_txt = "Modifier l'entrée" if entry else "Nouvelle entrée"
        ctk.CTkLabel(dlg, text=title_txt, font=("Courier New", 16, "bold"),
                     text_color=ACCENT).pack(pady=(28, 20))

        fields = {}
        defs = [
            ("name", "Nom *", entry.get("name","") if entry else ""),
            ("username", "Identifiant / Email", entry.get("username","") if entry else ""),
            ("url", "URL / Site", entry.get("url","") if entry else ""),
            ("notes", "Notes", entry.get("notes","") if entry else ""),
        ]
        for key, label, default in defs:
            ctk.CTkLabel(dlg, text=label, font=FONT_SUB, text_color=SUBTEXT).pack(anchor="w", padx=36)
            e = ctk.CTkEntry(dlg, height=38, font=FONT_MAIN, fg_color=CARD,
                             border_color=BORDER, text_color=TEXT)
            e.insert(0, default)
            e.pack(padx=36, fill="x", pady=(2, 10))
            fields[key] = e

        ctk.CTkLabel(dlg, text="Mot de passe *", font=FONT_SUB, text_color=SUBTEXT).pack(anchor="w", padx=36)
        pw_frame = ctk.CTkFrame(dlg, fg_color="transparent")
        pw_frame.pack(padx=36, fill="x", pady=(2, 4))
        pw_entry = ctk.CTkEntry(pw_frame, show="•", height=38, font=FONT_MAIN,
                                fg_color=CARD, border_color=BORDER, text_color=TEXT)
        pw_entry.pack(side="left", fill="x", expand=True)
        if entry:
            pw_entry.insert(0, entry.get("password",""))

        show_var = ctk.BooleanVar(value=False)
        def toggle_show():
            pw_entry.configure(show="" if show_var.get() else "•")
        ctk.CTkCheckBox(pw_frame, text="👁", variable=show_var, command=toggle_show,
                        width=36, fg_color=ACCENT, hover_color=ACCENT2,
                        text_color=SUBTEXT, font=FONT_SUB).pack(side="left", padx=8)

        # Strength bar
        strength_label = ctk.CTkLabel(dlg, text="", font=FONT_SUB, text_color=SUBTEXT)
        strength_label.pack(anchor="w", padx=36)
        strength_bar = ctk.CTkProgressBar(dlg, height=6, fg_color=BORDER)
        strength_bar.pack(padx=36, fill="x", pady=(2, 8))
        strength_bar.set(0)

        def update_strength(*_):
            pw = pw_entry.get()
            score, label = password_strength(pw)
            color = RED if score < 30 else "#e0a840" if score < 55 else GREEN if score < 75 else ACCENT
            strength_bar.configure(progress_color=color)
            strength_bar.set(score / 100)
            strength_label.configure(text=f"Force : {label}", text_color=color)

        pw_entry.bind("<KeyRelease>", update_strength)

        ctk.CTkButton(dlg, text="⚡ Générer", height=32, font=FONT_SUB,
                      fg_color=CARD, hover_color=BORDER, text_color=ACCENT,
                      border_width=1, border_color=BORDER,
                      command=lambda: (pw_entry.delete(0,"end"),
                                       pw_entry.insert(0, generate_password()),
                                       update_strength())).pack(padx=36, anchor="w", pady=(0,10))

        err = ctk.CTkLabel(dlg, text="", font=FONT_SUB, text_color=RED)
        err.pack()

        def do_save():
            name = fields["name"].get().strip()
            password = pw_entry.get()
            if not name:
                err.configure(text="⚠ Le nom est requis"); return
            if not password:
                err.configure(text="⚠ Le mot de passe est requis"); return

            new_entry = {
                "id": entry["id"] if entry else str(uuid.uuid4()),
                "name": name,
                "username": fields["username"].get().strip(),
                "url": fields["url"].get().strip(),
                "password": password,
                "notes": fields["notes"].get().strip(),
            }
            if entry:
                idx = next((i for i, e in enumerate(self.entries) if e["id"] == entry["id"]), None)
                if idx is not None:
                    self.entries[idx] = new_entry
            else:
                self.entries.append(new_entry)

            save_vault(self.master_password, self.entries)
            dlg.destroy()
            self._refresh_list()
            self._set_status("✓ Entrée sauvegardée")

        for f in fields.values():
            f.bind("<Return>", lambda e: do_save())
        pw_entry.bind("<Return>", lambda e: do_save())

        btn_row = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_row.pack(padx=36, fill="x", pady=(4, 0))

        ctk.CTkButton(btn_row, text="Sauvegarder", height=42, font=FONT_MAIN,
                      fg_color=ACCENT, hover_color="#b8943e", text_color="#0d0d0f",
                      command=do_save).pack(side="left", fill="x", expand=True, padx=(0, 4))

        def copy_pw():
            pw = pw_entry.get()
            if pw:
                try:
                    pyperclip.copy(pw)
                    copy_btn.configure(text="✓ Copié !")
                    dlg.after(1500, lambda: copy_btn.configure(text="📋 Copier"))
                except Exception:
                    pass

        copy_btn = ctk.CTkButton(btn_row, text="📋 Copier", height=42, font=FONT_MAIN,
                                  fg_color=CARD, hover_color=BORDER, text_color=TEXT,
                                  border_width=1, border_color=BORDER,
                                  command=copy_pw)
        copy_btn.pack(side="left", fill="x", expand=True, padx=(4, 0))

    # ── Delete ────────────────────────────────────────────────────────────────
    def _delete_entry(self, entry):
        if messagebox.askyesno("Supprimer", f"Supprimer « {entry.get('name')} » ?"):
            self.entries = [e for e in self.entries if e["id"] != entry["id"]]
            save_vault(self.master_password, self.entries)
            self._refresh_list()
            self._set_status("🗑 Entrée supprimée")

    # ── Generator window ──────────────────────────────────────────────────────
    def _open_generator(self):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Générateur de mot de passe")
        dlg.geometry("400x420")
        dlg.configure(fg_color=PANEL)
        dlg.grab_set()
        dlg.resizable(False, False)

        ctk.CTkLabel(dlg, text="⚙ Générateur", font=("Courier New", 16, "bold"),
                     text_color=ACCENT).pack(pady=(24, 16))

        result_var = StringVar(value=generate_password())
        result = ctk.CTkEntry(dlg, textvariable=result_var, height=44, font=FONT_MAIN,
                              fg_color=CARD, border_color=ACCENT, text_color=ACCENT,
                              state="readonly")
        result.pack(padx=24, fill="x")

        length_var = ctk.IntVar(value=20)
        ctk.CTkLabel(dlg, text="Longueur", font=FONT_SUB, text_color=SUBTEXT).pack(anchor="w", padx=24, pady=(12,0))
        ctk.CTkSlider(dlg, from_=8, to=64, variable=length_var,
                      button_color=ACCENT, button_hover_color="#b8943e",
                      progress_color=ACCENT).pack(padx=24, fill="x")
        len_label = ctk.CTkLabel(dlg, textvariable=length_var, font=FONT_MAIN, text_color=TEXT)
        len_label.pack()

        opts = {}
        for key, label, default in [("upper","Majuscules",True),("lower","Minuscules",True),
                                     ("digits","Chiffres",True),("symbols","Symboles",True)]:
            v = ctk.BooleanVar(value=default)
            opts[key] = v
            ctk.CTkCheckBox(dlg, text=label, variable=v, fg_color=ACCENT,
                            hover_color=ACCENT2, font=FONT_MAIN, text_color=TEXT).pack(anchor="w", padx=24, pady=2)

        def regen():
            pw = generate_password(
                length=length_var.get(),
                use_upper=opts["upper"].get(),
                use_lower=opts["lower"].get(),
                use_digits=opts["digits"].get(),
                use_symbols=opts["symbols"].get(),
            )
            result_var.set(pw)

        def copy_gen():
            pyperclip.copy(result_var.get())
            copy_btn.configure(text="✓ Copié !")
            dlg.after(1500, lambda: copy_btn.configure(text="📋 Copier"))

        btn_row = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_row.pack(padx=24, fill="x", pady=(16, 0))
        ctk.CTkButton(btn_row, text="↻ Générer", height=40, font=FONT_MAIN,
                      fg_color=ACCENT, hover_color="#b8943e", text_color="#0d0d0f",
                      command=regen).pack(side="left", fill="x", expand=True, padx=(0,4))
        copy_btn = ctk.CTkButton(btn_row, text="📋 Copier", height=40, font=FONT_MAIN,
                                  fg_color=CARD, hover_color=BORDER, text_color=TEXT,
                                  border_width=1, border_color=BORDER,
                                  command=copy_gen)
        copy_btn.pack(side="left", fill="x", expand=True, padx=(4,0))

    # ── Lock ──────────────────────────────────────────────────────────────────
    def _lock(self):
        self.master_password = None
        self.entries = []
        if self._clipboard_timer:
            self._clipboard_timer.cancel()
        try:
            pyperclip.copy("")
        except Exception:
            pass
        self._show_unlock()

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _clear(self):
        for w in self.winfo_children():
            w.destroy()


def main():
    app = FortisApp()
    app.mainloop()


if __name__ == "__main__":
    main()