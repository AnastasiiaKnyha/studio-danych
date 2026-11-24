import tkinter as tk
from tkinter import ttk

import pandas as pd


class DataTable(ttk.Frame):
    # table that shows a DataFrame, with scrollbars

    def __init__(self, master: tk.Misc, height: int = 10) -> None:
        super().__init__(master)
        self.tree = ttk.Treeview(self, show="headings", height=height)
        y_bar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        x_bar = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_bar.set, xscrollcommand=x_bar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        y_bar.grid(row=0, column=1, sticky="ns")
        x_bar.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def show(self, frame: pd.DataFrame, limit: int = 200) -> None:
        # remove old rows and columns first
        self.tree.delete(*self.tree.get_children())
        shown = frame.head(limit)
        columns = [str(column) for column in frame.columns]
        self.tree["columns"] = columns
        for name, column in zip(columns, frame.columns):
            # width from the longest text in the column, but not wider than 300 pixels
            longest = 0 if shown.empty else shown[column].astype(str).str.len().max()
            width = int(min(300, max(len(name), longest) * 8 + 20))
            self.tree.heading(name, text=name)
            self.tree.column(name, width=width, anchor="w", stretch=False)

        for row in shown.itertuples(index=False):
            values = ["" if pd.isna(value) else value for value in row]
            self.tree.insert("", "end", values=values)

    def clear(self) -> None:
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = []


def set_choices(box: ttk.Combobox, values: list[str]) -> None:
    # new values for a list, the old choice stays if it is still on the list
    box["values"] = values
    if box.get() not in values:
        box.set(values[0] if values else "")