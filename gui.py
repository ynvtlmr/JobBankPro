import tkinter as tk
from tkinter import ttk
import pickle
from back_end import invite_eligible_candidates
import os
import sys
from datetime import datetime

# Set the expiration date (year, month, day)
expiration_date = datetime(2023, 6, 1)

# Compare the current date with the expiration date
if datetime.now() > expiration_date:
    print("This script has expired.\nContact the author for a new version.\nynvtlmr@gmail.com")
    sys.exit()


def run_app():
    CACHE_FILE = os.path.join(os.path.expanduser("~"), ".job_bank_pro.pkl")

    root = tk.Tk()
    root.title("Job Inviter")

    labels = [
        "Username:",
        "Password:",
        "Security Question 1:",
        "Security Answer 1:",
        "Security Question 2:",
        "Security Answer 2:",
        "Security Question 3:",
        "Security Answer 3:",
        "Job Posting Link:",
    ]

    entries = [ttk.Entry(root) if "Password" not in label and "Answer" not in label else ttk.Entry(root, show="*") for
               label
               in labels[:-1]]

    for i, (label, entry) in enumerate(zip(labels, entries)):
        ttk.Label(root, text=label).grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
        entry.grid(row=i, column=1, padx=5, pady=5)

    job_posting_link_label = ttk.Label(root, text="Job Posting Links:")
    job_posting_link_label.grid(row=8, column=0, padx=5, pady=5, sticky=tk.W)
    job_posting_link_entry = tk.Text(root, wrap=tk.WORD, width=50, height=10)
    job_posting_link_entry.grid(row=8, column=1, padx=5, pady=5)

    def load_cache():
        try:
            with open(CACHE_FILE, "rb") as f:
                data = pickle.load(f)
                for i, entry in enumerate(entries):
                    entry.insert(0, data['entries'][i])
                job_posting_link_entry.insert(tk.END, data['job_posting_link'])
        except FileNotFoundError:
            pass

    def save_cache():
        data = {
            'entries': [entry.get() for entry in entries],
            'job_posting_link': job_posting_link_entry.get("1.0", tk.END)
        }
        with open(CACHE_FILE, "wb") as f:
            pickle.dump(data, f)

    def submit():
        username = entries[0].get()
        password = entries[1].get()
        security = {
            entries[2].get(): entries[3].get(),
            entries[4].get(): entries[5].get(),
            entries[6].get(): entries[7].get(),
        }
        job_posting_link = list(job_posting_link_entry.get("1.0", tk.END).split('\n'))
        job_posting_link = [link.strip() for link in job_posting_link if link != '']

        invite_eligible_candidates(username, password, security, job_posting_link)
        save_cache()

    submit_button = ttk.Button(root, text="Submit", command=submit)
    submit_button.grid(row=10, column=0, columnspan=2, padx=5, pady=5)

    load_cache()
    root.mainloop()


if __name__ == "__main__":
    run_app()
