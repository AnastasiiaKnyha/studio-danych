import tkinter as tk
from tkinter import ttk

from studio.gui.widgets import DataTable
from studio.session import DataSession

PREVIEW_ROWS = 200


class DataTab(ttk.Frame):
    # preview of the current data

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, padding=10)
        self.info = tk.StringVar(value="Nie wczytano jeszcze pliku.")
        ttk.Label(self, textvariable=self.info).pack(anchor="w", pady=(0, 6))
        self.table = DataTable(self, height=20)
        self.table.pack(fill="both", expand=True)

    def refresh(self, session: DataSession | None) -> None:
        if session is None:
            self.table.clear()
            self.info.set("Nie wczytano jeszcze pliku.")
            return
        frame = session.current
        shown = min(PREVIEW_ROWS, len(frame))
        self.info.set(f"Podgląd bieżących danych, pokazano {shown} z {len(frame)} rekordów.")
        self.table.show(frame, PREVIEW_ROWS)