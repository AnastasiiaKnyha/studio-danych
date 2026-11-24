import tkinter as tk
from tkinter import ttk

from studio.gui.widgets import DataTable
from studio.profile import basic_info, column_profile, numeric_stats
from studio.session import DataSession


class ProfileTab(ttk.Frame):
    # profile of the current data

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, padding=10)
        self.summary = tk.StringVar(value="Nie wczytano jeszcze pliku.")
        ttk.Label(self, textvariable=self.summary, font=("TkDefaultFont", 11, "bold")).pack(anchor="w", pady=(0, 6))

        ttk.Label(self, text="Kolumny, typy, braki i wartości unikalne").pack(anchor="w")
        self.columns_table = DataTable(self, height=8)
        self.columns_table.pack(fill="both", expand=True, pady=(0, 10))

        ttk.Label(self, text="Statystyki opisowe kolumn liczbowych").pack(anchor="w")
        self.stats_table = DataTable(self, height=8)
        self.stats_table.pack(fill="both", expand=True)

    def refresh(self, session: DataSession | None) -> None:
        if session is None:
            self.summary.set("Nie wczytano jeszcze pliku.")
            self.columns_table.clear()
            self.stats_table.clear()
            return

        frame = session.current
        info = basic_info(frame)
        self.summary.set(
            f"Rekordy: {info['rekordy']}    Kolumny: {info['kolumny']}    Pełne duplikaty: {info['pelne_duplikaty']}"
        )
        # reset_index turns column names into a normal column of the table
        self.columns_table.show(column_profile(frame).rename_axis("kolumna").reset_index())
        self.stats_table.show(numeric_stats(frame).rename_axis("kolumna").reset_index())