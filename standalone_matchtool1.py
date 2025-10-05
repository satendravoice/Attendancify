import os
import re
import threading
import pandas as pd
from rapidfuzz import fuzz
import customtkinter as ctk
from tkinter import filedialog, messagebox

# ----------- Name Normalization -----------
def normalize_name(name: str) -> str:
    if not isinstance(name, str):
        name = str(name)
    name = re.sub(r"[^\w\s]", "", name)
    name = re.sub(r"\s+", " ", name)
    return name.strip().lower()

FILETYPES = [
    ("CSV & Excel files", ("*.csv", "*.xlsx", "*.xls")),
    ("CSV files", "*.csv"),
    ("Excel files", ("*.xlsx", "*.xls")),
]

def read_raw_file(raw_path: str) -> pd.DataFrame:
    df = pd.read_csv(raw_path) if raw_path.lower().endswith(".csv") else pd.read_excel(raw_path)
    df.columns = [str(c).strip() for c in df.columns]
    name_col = next((c for c in df.columns if c.lower() in ("name", "participant name")), None)
    if name_col is None:
        raise ValueError("Raw file needs a 'Name' column.")
    session_cols = [c for c in df.columns if c != name_col]
    if not session_cols:
        raise ValueError("Raw file contains no session/status columns.")
    def norm(x): return x if str(x) in ("P", "A") else "N/A"
    for col in session_cols:
        df[col] = df[col].apply(norm)
    out = df[[name_col] + session_cols].copy()
    out.columns = ["Name"] + session_cols
    return out

def postprocess_attendance(df, session_cols):
    # Replace P→present, A→absent (case-insensitive), but only in session columns
    for col in session_cols:
        df[col] = df[col].replace({"P": "present", "A": "absent", "p": "present", "a": "absent"})
    return df

def match_and_write(master_file: str, raw_file: str, out_fmt: str = "xlsx") -> str:
    mdf = pd.read_csv(master_file) if master_file.lower().endswith(".csv") else pd.read_excel(master_file)
    email_col = next((c for c in mdf.columns if str(c).strip().lower() in ("email", "email_id")), None)
    name_col = next((c for c in mdf.columns if str(c).strip().lower() in ("participant name", "name")), None)
    if email_col is None or name_col is None:
        raise ValueError("Master file must have 'Email' and 'Participant Name' columns.")
    mdf = mdf[[email_col, name_col]].copy()
    mdf.columns = ["Email", "Participant Name"]
    rdf = read_raw_file(raw_file)
    session_cols = list(rdf.columns[1:])
    raw_norm_names = [normalize_name(n) for n in list(rdf["Name"])]
    matched_df = mdf.copy()
    for col in session_cols:
        matched_df[col] = "N/A"
    threshold = 85
    matched_indices = set()
    for idx, row in matched_df.iterrows():
        master_name = normalize_name(str(row["Participant Name"]))
        best_score, best_j = -1, None
        for j, raw_norm in enumerate(raw_norm_names):
            score = fuzz.token_set_ratio(master_name, raw_norm)
            if score > best_score:
                best_score = score
                best_j = j
        if best_score >= threshold:
            raw_row = rdf.iloc[best_j]
            for col in session_cols:
                matched_df.at[idx, col] = raw_row[col]
            matched_indices.add(best_j)
    unmatched_df = rdf.iloc[[i for i in range(len(rdf)) if i not in matched_indices]].copy()
    if not unmatched_df.empty:
        unmatched_df.rename(columns={"Name": "Raw Name (not found in Master)"}, inplace=True)
    # ---- Here: replace P/A
    matched_df = postprocess_attendance(matched_df, session_cols)
    if not unmatched_df.empty:
        unmatched_df = postprocess_attendance(unmatched_df, session_cols)
    out_dir = os.path.dirname(master_file)
    mbase = os.path.splitext(os.path.basename(master_file))[0]
    rbase = os.path.splitext(os.path.basename(raw_file))[0]
    if out_fmt == "xlsx":
        out_path = os.path.join(out_dir, f"{mbase}_matched_with_{rbase}_attendance.xlsx")
        with pd.ExcelWriter(out_path, engine="openpyxl") as w:
            matched_df.to_excel(w, index=False, sheet_name="Matched")
            if not unmatched_df.empty:
                unmatched_df.to_excel(w, index=False, sheet_name="Unmatched Raw")
            pd.DataFrame([], columns=["email_id", "attendance(absent/present/leave)"]).to_excel(w, index=False, sheet_name="Summary")
        return os.path.basename(out_path)
    prefix = os.path.join(out_dir, f"{mbase}_matched_with_{rbase}_")
    matched_df.to_csv(prefix + "matched.csv", index=False)
    if not unmatched_df.empty:
        unmatched_df.to_csv(prefix + "unmatched.csv", index=False)
    pd.DataFrame([], columns=["email_id", "attendance(absent/present/leave)"]).to_csv(prefix + "summary.csv", index=False)
    return os.path.basename(prefix + "matched.csv")

# ----------- Modern CustomTkinter GUI -----------
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class FilePair(ctk.CTkFrame):
    def __init__(self, master, idx, remove_cb):
        super().__init__(master)
        self.mpath = {"v": None}
        self.rpath = {"v": None}
        self.row_num = idx
        self.remove_cb = remove_cb
        self.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(self, text=f"Master {idx+1}:", width=120, anchor="w").grid(row=0, column=0, padx=(10,2), sticky="w")
        self.master_entry = ctk.CTkEntry(self, placeholder_text="No master file", width=260)
        self.master_entry.grid(row=0, column=1, padx=2, pady=4, sticky="ew")
        ctk.CTkButton(self, text="Browse", width=80, command=self.pick_master).grid(row=0, column=2, padx=4)
        ctk.CTkLabel(self, text=f"Raw {idx+1}:", width=120, anchor="w").grid(row=1, column=0, padx=(10,2), sticky="w")
        self.raw_entry = ctk.CTkEntry(self, placeholder_text="No raw file", width=260)
        self.raw_entry.grid(row=1, column=1, padx=2, pady=4, sticky="ew")
        ctk.CTkButton(self, text="Browse", width=80, command=self.pick_raw).grid(row=1, column=2, padx=4)
        ctk.CTkButton(self, text="Remove", fg_color="#fee2e2", text_color="black", width=80, command=self.remove_cb).grid(row=0, column=3, rowspan=2, padx=(24,9))
    def pick_master(self):
        path = filedialog.askopenfilename(filetypes=FILETYPES)
        if path:
            self.mpath["v"] = path
            self.master_entry.delete(0, 'end')
            self.master_entry.insert(0, os.path.basename(path))
    def pick_raw(self):
        path = filedialog.askopenfilename(filetypes=FILETYPES)
        if path:
            self.rpath["v"] = path
            self.raw_entry.delete(0, 'end')
            self.raw_entry.insert(0, os.path.basename(path))

class AttendanceMatchApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Attendance Match Tool – Modern Edition")
        self.geometry("900x520")
        ctk.CTkLabel(self, text="Attendance Match Tool", font=("Segoe UI Black", 26), anchor="w",
            fg_color="#244773", width=900, height=54, corner_radius=8, text_color="white").pack(fill="x", pady=(8,5))
        main = ctk.CTkFrame(self, fg_color="#f7fafc", corner_radius=10)
        main.pack(expand=True, fill="both", padx=20, pady=10)
        control = ctk.CTkFrame(main, fg_color="transparent")
        control.pack(fill="x", pady=(0,7))
        ctk.CTkButton(control, text="+ Add Pair", width=110, fg_color="#3573e6", command=self.add_pair).pack(side="right", padx=10)
        ctk.CTkLabel(control, text="Output format:", font=("Segoe UI", 13)).pack(side="left", padx=8)
        self.fmt_var = ctk.StringVar(value="xlsx")
        ctk.CTkComboBox(control, values=["xlsx", "csv"], width=88, variable=self.fmt_var, state="readonly").pack(side="left", padx=2)
        self.pair_area = ctk.CTkScrollableFrame(main, width=720, height=230, fg_color="#eef3f7")
        self.pair_area.pack(expand=True, fill="both", padx=10, pady=(4,10))
        self.file_pairs = []
        self.add_pair()
        bottom = ctk.CTkFrame(main)
        bottom.pack(fill="x", pady=(8,4))
        self.proc_btn = ctk.CTkButton(bottom, text="Process All", width=160, height=38,
                                      font=("Segoe UI", 15, "bold"),
                                      fg_color="#233860", hover_color="#496fab", command=self.process_all)
        self.proc_btn.pack(side="right", padx=20, pady=10)
        self.pbar = ctk.CTkProgressBar(bottom, width=300, height=14, progress_color="#3573e6")
        self.pbar.pack(side="left", padx=(16,4), pady=(10,6))
        self.plabel = ctk.CTkLabel(bottom, text="", font=("Segoe UI", 12))
        self.plabel.pack(anchor="w", padx=(6,10), side="left")

    def add_pair(self):
        idx = len(self.file_pairs)
        def remove_pair():
            pf.destroy()
            self.file_pairs.remove(pf)
        pf = FilePair(self.pair_area, idx, remove_pair)
        self.file_pairs.append(pf)
        self.redraw_pairs()
    def redraw_pairs(self):
        for idx, pf in enumerate(self.file_pairs):
            pf.grid(row=idx, column=0, pady=7, sticky="ew", padx=5)
            pf.row_num = idx
    def process_all(self):
        pairs = []
        for pf in self.file_pairs:
            mf = pf.mpath["v"]
            rf = pf.rpath["v"]
            if mf and rf:
                pairs.append((mf, rf))
        if not pairs:
            messagebox.showerror("No Files Selected", "Please select at least one Master/Raw pair.")
            return
        self.proc_btn.configure(state="disabled")
        self.pbar.set(0)
        self.plabel.configure(text="Starting...")
        def worker():
            for idx, (mf, rf) in enumerate(pairs, 1):
                self.plabel.configure(text=f"Processing: {os.path.basename(mf)} + {os.path.basename(rf)}")
                try:
                    out = match_and_write(mf, rf, self.fmt_var.get())
                    self.plabel.configure(text=f"Created: {out}")
                except Exception as exc:
                    messagebox.showerror("Error", f"{os.path.basename(mf)} + {os.path.basename(rf)}\n{exc}")
                self.pbar.set(idx/len(pairs))
            self.proc_btn.configure(state="normal")
            self.plabel.configure(text="Finished!")
        threading.Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    app = AttendanceMatchApp()
    app.mainloop()
