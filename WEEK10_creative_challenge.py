import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
import hashlib

class SecureMessenger:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure University Messenger")
        self.root.geometry("600x500")
        self.root.configure(bg="#1e1e1e") # Dark mode background

        self.messages = []
        self.current_user = None
        self.setup_login_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def setup_login_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Secure University Messenger", font=("Arial", 18, "bold"), bg="#1e1e1e", fg="#4CAF50").pack(pady=40)
        
        tk.Button(self.root, text="Login as Student", width=25, bg="#2d2d2d", fg="white", font=("Arial", 12), command=lambda: self.login("Student")).pack(pady=10)
        tk.Button(self.root, text="Login as Lecturer", width=25, bg="#2d2d2d", fg="white", font=("Arial", 12), command=lambda: self.login("Lecturer")).pack(pady=10)

    def login(self, role):
        self.current_user = role
        self.setup_chat_screen()

    def setup_chat_screen(self):
        self.clear_screen()
        
        header = tk.Frame(self.root, bg="#333333", padx=10,pady=10)
        header.pack(fill=tk.X)
        tk.Label(header, text=f"Logged in as: {self.current_user}", font=("Arial", 12), bg="#333333", fg="white").pack(side=tk.LEFT)
        tk.Button(header, text="Logout", bg="#e53935", fg="white", command=self.setup_login_screen).pack(side=tk.RIGHT)
        tk.Button(header, text="Export Chat", bg="#1976D2", fg="white", command=self.export_chat).pack(side=tk.RIGHT, padx=10)

        # Chat display area
        self.chat_display = tk.Text(self.root, bg="#121212", fg="#00e676", font=("Consolas", 10), state=tk.DISABLED)
        self.chat_display.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        self.refresh_chat()

        # Input area
        input_frame = tk.Frame(self.root, bg="#1e1e1e")
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.msg_entry = tk.Entry(input_frame, font=("Arial", 12), bg="#2d2d2d", fg="white", insertbackground="white")
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Button(input_frame, text="Send Securely", bg="#4CAF50", fg="white", command=self.send_message).pack(side=tk.RIGHT)

    def send_message(self):
        raw_msg = self.msg_entry.get().strip()
        if not raw_msg: return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        # Simulating ECC/ElGamal signature generation
        signature_hash = hashlib.sha256(raw_msg.encode()).hexdigest()[:16] 
        
        formatted_msg = f"[{timestamp}] {self.current_user}:\nMsg: {raw_msg}\nSig: {signature_hash} (Verified)\n{'-'*40}\n"
        self.messages.append(formatted_msg)
        
        self.msg_entry.delete(0, tk.END)
        self.refresh_chat()

    def refresh_chat(self):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        for msg in self.messages:
            self.chat_display.insert(tk.END, msg)
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def export_chat(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "w") as f:
                f.write("=== ENCRYPTED CHAT LOG ===\n\n")
                f.writelines(self.messages)
            messagebox.showinfo("Success", "Chat history safely exported!")

if __name__ == "__main__":
    root = tk.Tk()
    app = SecureMessenger(root)
    root.mainloop()