import os
import pandas as pd
import customtkinter as ctk
from tkinter import filedialog, messagebox

DEFAULT_OUTDIR = os.path.join(os.getcwd(), "RawFiles")
SHEET_NAME = "Attendance"

def extract_raw_from_excel(xl_path):
    # Always extract sheet2 (named "Attendance" in your example)
    xl = pd.ExcelFile(xl_path)
    if SHEET_NAME not in xl.sheet_names:
        raise ValueError(f"Sheet '{SHEET_NAME}' not found in the file.")
    df = xl.parse(SHEET_NAME)
    name_col = next((c for c in df.columns if str(c).strip().lower() in ("name", "participant name")), None)
    if not name_col:
        raise ValueError("No 'Name' column found.")
    session_cols = [c for c in df.columns if str(df[c].dropna().unique()).strip("[]").replace("'", "").lower() in ("p, a", "p", "a")]
    # Fallback for cases session columns have headers with "Session" or contain P/A markers
    if not session_cols:
        session_cols = [c for c in df.columns if "session" in str(c).lower()]
    out = df[[name_col]+session_cols].copy()
    out.columns = ["Name"] + [str(c) for c in session_cols]
    # Only keep "P"/"A", replace anything else with "N/A"
    for col in session_cols:
        out[col] = out[col].apply(lambda x: x if str(x).strip().upper() in ("P","A") else "N/A")
    return out

class RawExcelApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Raw Excel Generator")
        self.geometry("700x400")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.file_paths = []
        self.out_dir = DEFAULT_OUTDIR

        title_lbl = ctk.CTkLabel(self, text="Raw Excel Generator", font=("Segoe UI Black", 22),
                                 fg_color="#244773", text_color="white", width=700, height=40, corner_radius=8)
        title_lbl.pack(fill="x", padx=6, pady=(10,3))

        mframe = ctk.CTkFrame(self, fg_color="#f3f8fc", corner_radius=10)
        mframe.pack(expand=True, fill="both", padx=17, pady=(3,12))

        self.file_btn = ctk.CTkButton(mframe, text="Select Excel File(s)", width=170, fg_color="#3573e6",
                                      command=self.select_files)
        self.file_btn.pack(padx=12, pady=(14,6))

        od_frame = ctk.CTkFrame(mframe, fg_color="transparent")
        od_frame.pack(fill="x", pady=(0,8))
        ctk.CTkLabel(od_frame, text="Output Folder:", font=("Segoe UI", 13)).pack(side="left", padx=6)
        self.od_lbl = ctk.CTkLabel(od_frame, text=self.out_dir, font=("Segoe UI", 12), anchor="w")
        self.od_lbl.pack(side="left", padx=2)
        ctk.CTkButton(od_frame, text="Change...", width=100, command=self.change_output_folder).pack(side="left", padx=9)

        self.gen_btn = ctk.CTkButton(mframe, text="Generate Raw File(s)", width=200, height=34,
                                     fg_color="#244773", hover_color="#2c426e", font=("Segoe UI", 14, "bold"),
                                     command=self.generate_raw)
        self.gen_btn.pack(padx=24, pady=(8,6))

        pbar_frame = ctk.CTkFrame(mframe, fg_color="transparent")
        pbar_frame.pack(fill="x", pady=(2,6))
        self.pbar = ctk.CTkProgressBar(pbar_frame, width=290, height=16, progress_color="#3573e6")
        self.pbar.pack(side="left", padx=16)
        self.plabel = ctk.CTkLabel(pbar_frame, text="Ready.", font=("Segoe UI", 11))
        self.plabel.pack(side="left", padx=7)

        log_frame = ctk.CTkFrame(mframe, fg_color="#e7ecef", corner_radius=6)
        log_frame.pack(expand=True, fill="both", padx=(12,12), pady=(9,5))
        self.logbox = ctk.CTkTextbox(log_frame, width=620, height=110, font=("Consolas", 11))
        self.logbox.pack(expand=True, fill="both")
        self.log("App started. Select file(s) and output folder.")

        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)

    def log(self, msg):
        self.logbox.insert("end", f"{msg}\n")
        self.logbox.see("end")

    def select_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Excel files", "*.xlsx;*.xls")])
        if files:
            self.file_paths = list(files)
            self.log(f"Selected files: {', '.join([os.path.basename(f) for f in files])}")
            self.plabel.configure(text=f"{len(files)} file(s) selected.")

    def change_output_folder(self):
        pth = filedialog.askdirectory()
        if pth:
            self.out_dir = pth
            self.od_lbl.configure(text=self.out_dir)
            self.log(f"Output folder changed to: {pth}")
            if not os.path.exists(self.out_dir):
                os.makedirs(self.out_dir)

    def generate_raw(self):
        if not self.file_paths:
            messagebox.showerror("No Files", "Please select Excel file(s) first!")
            return
        self.gen_btn.configure(state="disabled")
        n = len(self.file_paths)
        self.pbar.set(0)
        self.log("Processing started.")
        for idx, fpath in enumerate(self.file_paths, 1):
            fname = os.path.splitext(os.path.basename(fpath))[0]
            self.plabel.configure(text=f"Processing: {fname} ({idx}/{n})")
            try:
                raw_df = extract_raw_from_excel(fpath)
                out_path = os.path.join(self.out_dir, f"{fname}-RAW.xlsx")
                raw_df.to_excel(out_path, index=False)
                self.log(f"Output: {out_path}")
            except Exception as e:
                self.log(f"ERROR in {fname}: {e}")
            self.pbar.set(idx/n)
        self.gen_btn.configure(state="normal")
        self.plabel.configure(text=f"Finished! {n} file(s) processed.")

if __name__ == "__main__":
    app = RawExcelApp()
    app.mainloop()
