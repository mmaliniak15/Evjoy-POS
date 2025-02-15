import tkinter as tk
from tkinter import messagebox
from tkinter import font
from tkinter import simpledialog
from datetime import datetime
from pytz import timezone
import math
import csv

class POS:
    def __init__(self, master):
        self.master = master
        self.read_inventory()
        self.app_config()

    def read_inventory(self):
        inventory = dict()

        with open('Inventory.csv', 'r') as csv_file:
            
            csv_reader = csv.reader(csv_file, delimiter=',')

            for row in csv_reader:

                item = row[0]
                if item != 'Item':
                    package = row[2]
                    price = row[3].replace('$','').replace(' ','')
                    price = float(price)

                    if item in inventory.keys():
                        inventory[item][package] = price
                    else:
                        inventory[item] = {package:price}

        self.inventory = inventory

    def app_config(self):

        default_font = font.nametofont('TkDefaultFont')
        default_font.configure(size=10)
        
        self.master.title('Evjoy POS system')

        frm_item = tk.Frame(self.master, borderwidth=3, padx=5, pady=5, highlightbackground="black", highlightthickness=1)
        frm_item.pack(side='top', fill='both', expand=1)

        max_cols = 0

        for i, item in enumerate(self.inventory.keys()):
            lbl_item = tk.Label(frm_item, text=item)
            lbl_item.grid(row=i, column=0, sticky='nsew')
            for j,package in enumerate(self.inventory[item].keys()):
                max_cols = j if j > max_cols else max_cols
                btn_product = tk.Button(frm_item, text=package, command=lambda x=(item,package):self.add_item(f"{x[0]}-{x[1]}", self.inventory[x[0]][x[1]]))
                btn_product.grid(row=i, column=j+1, sticky='nsew')

        frm_item.columnconfigure(0, weight=1)
        for col in range(max_cols+1):
            frm_item.columnconfigure(col+1, weight=1)
        for row_num in range(frm_item.grid_size()[1]):
            frm_item.rowconfigure(row_num, weight=1)

        frm_cart = tk.Frame(self.master, borderwidth=3, padx=20, pady=20, highlightbackground="black", highlightthickness=1)
        frm_cart.pack(side='top', fill='both', expand=1)
        frm_cart.columnconfigure([0,1], weight=1)
        lbl_cart = tk.Label(frm_cart, text="Cart:")
        lbl_cart.grid(row=0, column=0, sticky='w')
        self.cart_text = tk.Text(frm_cart, height=5, width=40)
        self.cart_text.grid(row=1, column=0, columnspan=2, sticky='nsew')
        self.subtotal_label = tk.Label(frm_cart, text="Subtotal: $0.00")
        self.subtotal_label.grid(row=2, column=0, columnspan=2)
        # frm_cart.rowconfigure(0,weight=1)
        frm_cart.rowconfigure(1,weight=1)
        # frm_cart.rowconfigure(2,weight=1)

        self.cart = []
        self.subtotal = 0
        self.total = 0

        frm_final = tk.Frame(self.master, padx=5, pady=5)
        frm_final.pack(fill='none', expand=0)
        btn_cash = tk.Button(frm_final, text='Cash Payment', command=lambda: self.calc_total('cash'))
        btn_cash.grid(row=0, column=0)
        btn_credit = tk.Button(frm_final, text='Credit Payment', command=lambda: self.calc_total('credit'))
        btn_credit.grid(row=0, column=1)
        self.lbl_total = tk.Label(frm_final, text='Total: $0.00')
        self.lbl_total.grid(row=1,column=0, columnspan=2)
        btn_clear = tk.Button(frm_final, text='Cancel/Clear Form', command=lambda: self.cancel_order())
        btn_clear.grid(row=2, column=0)
        self.btn_submit = tk.Button(frm_final, text='Submit Order Record', command=lambda: self.submit_order(), state=tk.DISABLED)
        self.btn_submit.grid(row=2, column=1)
        

    def add_item(self, name, price):
        self.cart.append((name, price))
        self.update_cart()
        self.btn_submit.config(state=tk.DISABLED)

    def update_cart(self):
        self.cart_text.delete("1.0", tk.END)
        for item, price in self.cart:
            self.cart_text.insert(tk.END, f"{item} - ${price:.2f}\n")
        if self.cart:
            self.subtotal += price
        else:
            self.subtotal = 0.0
        self.subtotal_label.config(text=f"Subtotal: ${self.subtotal:.2f}")

    def calc_total(self, payment_method):
        self.payment_method = payment_method
        if payment_method == 'cash':
            self.total = self.subtotal
        else:
            self.total = math.ceil((self.subtotal * 1.045 + .1) * 100) / 100
        self.lbl_total.config(text=f"Total: ${self.total:.2f}")
        self.btn_submit.config(state=tk.ACTIVE)

    def submit_order(self):
        if self.payment_method == 'cash':
            cash_return = self.get_cash_return()
            print(cash_return)
        if self.payment_method == 'credit' or (self.payment_method == 'cash' and cash_return):
            self.record_order()
            messagebox.showinfo(message=f"Recorded order for ${self.total:.2f}")
            self.cart = []
            self.total = 0.0
            self.subtotal = 0.0
            self.update_cart()
            self.calc_total('cash')
            self.btn_submit.config(state=tk.DISABLED)

    def cancel_order(self):
        self.cart = []
        self.total = 0.0
        self.subtotal = 0.0
        self.update_cart()
        self.calc_total('cash')
        self.btn_submit.config(state=tk.DISABLED)

    def record_order(self):
        with open('Purchase_History.csv', 'a') as fd:
            for i in self.cart:
                item_package = i[0].split('-')
                tz = timezone('EST')
                timestamp = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
                fd.write(','.join([item_package[0], item_package[1], str(i[1]), timestamp])+'\n')


    def get_cash_return(self):
        dialog = CashDialog(self.master, self.total)
        self.master.wait_window(dialog)

        return dialog.result

class CashDialog(tk.Toplevel):
    def __init__(self, parent, total_value):
        super().__init__(parent)
        self.total_value = total_value
        self.result = None

        self.title("Enter Payment")
        self.geometry("300x150")
        self.grab_set()  # Make the dialog modal

        tk.Label(self, text=f"Enter an amount greater than {total_value}:").pack(pady=5)

        self.entry = tk.Entry(self)
        self.entry.pack(pady=5)
        self.entry.focus()

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="OK", command=self.validate).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Exact Change", command=self.exact_change).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Cancel", command=self.cancel).grid(row=0, column=2, padx=5)

    def validate(self):
        try:
            value = float(self.entry.get())
            if value > self.total_value:
                self.result = value
                messagebox.showinfo("Cash Return", f"Cash to be returned: ${value - self.total_value:.2f}")
                self.destroy()
            else:
                messagebox.showerror("Invalid Input", f"Please enter a value greater than {self.total_value}.")
                self.lift()  # Bring dialog back to front
                self.focus_force()  # Force focus on the dialog
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number.")
            self.lift()  # Bring dialog back to front
            self.focus_force()  # Force focus on the dialog

    def exact_change(self):
        self.result = "Exact Change"
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()        
        


if __name__ == "__main__":
    root = tk.Tk()
    pos = POS(root)
    root.mainloop()