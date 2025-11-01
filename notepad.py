"""
Simple Notepad-like text editor for Windows using Python and Tkinter.

Save this file as `notepad.py` and run with: `python notepad.py`

Features:
- New / Open / Save / Save As
- Cut / Copy / Paste / Undo / Redo
- Find / Replace
- Go To Line
- Toggle Word Wrap
- Change Font (family & size)
- Status bar with line/column
- About dialog

Requires only the Python standard library (Tkinter). Works on Windows, macOS and Linux.

Author: ChatGPT (example)
"""

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, font
import os

class Notepad:
    def __init__(self, root):
        self.root = root
        self.root.title('Untitled - Notepad')
        self.root.geometry('900x600')
        self.filename = None
        self._set_icons()

        # Default font
        self.current_font_family = 'Consolas'
        self.current_font_size = 12
        self.text_font = font.Font(family=self.current_font_family, size=self.current_font_size)

        # Create UI
        self._create_widgets()
        self._create_menu()
        self._bind_shortcuts()
        self._update_title()
        self._update_status()

    def _set_icons(self):
        # Placeholder for icon setup if you want to add a .ico file on Windows
        try:
            self.root.iconbitmap(default='notepad.ico')
        except Exception:
            pass

    def _create_widgets(self):
        # Main text area with scrollbar
        self.text = tk.Text(self.root, wrap='none', undo=True, font=self.text_font)
        self.v_scroll = tk.Scrollbar(self.root, orient='vertical', command=self.text.yview)
        self.h_scroll = tk.Scrollbar(self.root, orient='horizontal', command=self.text.xview)
        self.text.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)

        self.v_scroll.pack(side='right', fill='y')
        self.h_scroll.pack(side='bottom', fill='x')
        self.text.pack(fill='both', expand=1)

        # Status bar
        self.status = tk.StringVar()
        self.status_bar = tk.Label(self.root, textvariable=self.status, anchor='w')
        self.status_bar.pack(side='bottom', fill='x')

        # Track modifications for status updates
        self.text.bind('<<Modified>>', self._on_modified)

    def _create_menu(self):
        menubar = tk.Menu(self.root)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label='New', accelerator='Ctrl+N', command=self.new_file)
        file_menu.add_command(label='Open...', accelerator='Ctrl+O', command=self.open_file)
        file_menu.add_command(label='Save', accelerator='Ctrl+S', command=self.save_file)
        file_menu.add_command(label='Save As...', accelerator='Ctrl+Shift+S', command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', accelerator='Alt+F4', command=self.exit_app)
        menubar.add_cascade(label='File', menu=file_menu)

        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label='Undo', accelerator='Ctrl+Z', command=self.text.edit_undo)
        edit_menu.add_command(label='Redo', accelerator='Ctrl+Y', command=self.text.edit_redo)
        edit_menu.add_separator()
        edit_menu.add_command(label='Cut', accelerator='Ctrl+X', command=lambda: self.text.event_generate('<<Cut>>'))
        edit_menu.add_command(label='Copy', accelerator='Ctrl+C', command=lambda: self.text.event_generate('<<Copy>>'))
        edit_menu.add_command(label='Paste', accelerator='Ctrl+V', command=lambda: self.text.event_generate('<<Paste>>'))
        edit_menu.add_separator()
        edit_menu.add_command(label='Find...', accelerator='Ctrl+F', command=self.find_text)
        edit_menu.add_command(label='Replace...', accelerator='Ctrl+H', command=self.replace_text)
        edit_menu.add_command(label='Go To Line...', accelerator='Ctrl+G', command=self.goto_line)
        menubar.add_cascade(label='Edit', menu=edit_menu)

        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0)
        self.wrap_var = tk.BooleanVar(value=False)
        view_menu.add_checkbutton(label='Word Wrap', onvalue=True, offvalue=False, variable=self.wrap_var, command=self.toggle_wrap)
        view_menu.add_command(label='Font...', command=self.choose_font)
        menubar.add_cascade(label='View', menu=view_menu)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label='About', command=self.show_about)
        menubar.add_cascade(label='Help', menu=help_menu)

        self.root.config(menu=menubar)

    def _bind_shortcuts(self):
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-S>', lambda e: self.save_as())
        self.root.bind('<Control-f>', lambda e: self.find_text())
        self.root.bind('<Control-h>', lambda e: self.replace_text())
        self.root.bind('<Control-g>', lambda e: self.goto_line())
        self.root.bind('<Key>', lambda e: self._update_status())

    # File operations
    def new_file(self):
        if self._maybe_save():
            self.text.delete('1.0', tk.END)
            self.filename = None
            self._update_title()

    def open_file(self):
        if not self._maybe_save():
            return
        file = filedialog.askopenfilename(defaultextension='.txt', filetypes=[('Text Documents', '*.txt'), ('All Files', '*.*')])
        if file:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = f.read()
                self.text.delete('1.0', tk.END)
                self.text.insert('1.0', data)
                self.filename = file
                self._update_title()
                self.text.edit_modified(False)
            except Exception as e:
                messagebox.showerror('Open File', f'Failed to open file: {e}')

    def save_file(self):
        if self.filename:
            try:
                data = self.text.get('1.0', tk.END)
                with open(self.filename, 'w', encoding='utf-8') as f:
                    f.write(data.rstrip('\n'))
                self.text.edit_modified(False)
                self._update_title()
                return True
            except Exception as e:
                messagebox.showerror('Save File', f'Failed to save file: {e}')
                return False
        else:
            return self.save_as()

    def save_as(self):
        file = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text Documents', '*.txt'), ('All Files', '*.*')])
        if file:
            try:
                data = self.text.get('1.0', tk.END)
                with open(file, 'w', encoding='utf-8') as f:
                    f.write(data.rstrip('\n'))
                self.filename = file
                self.text.edit_modified(False)
                self._update_title()
                return True
            except Exception as e:
                messagebox.showerror('Save File', f'Failed to save file: {e}')
                return False
        return False

    def exit_app(self):
        if self._maybe_save():
            self.root.destroy()

    def _maybe_save(self):
        if self.text.edit_modified():
            choice = messagebox.askyesnocancel('Save', 'You have unsaved changes. Save before continuing?')
            if choice:  # Yes
                return self.save_file()
            elif choice is None:  # Cancel
                return False
            else:  # No
                return True
        return True

    # Edit helpers
    def find_text(self):
        FindDialog(self.root, self.text)

    def replace_text(self):
        ReplaceDialog(self.root, self.text)

    def goto_line(self):
        line = simpledialog.askinteger('Go To Line', 'Enter line number:')
        if line is None:
            return
        max_line = int(self.text.index('end-1c').split('.')[0])
        if line < 1:
            line = 1
        if line > max_line:
            line = max_line
        self.text.mark_set('insert', f'{line}.0')
        self.text.see('insert')
        self._update_status()

    def toggle_wrap(self):
        if self.wrap_var.get():
            self.text.config(wrap='word')
            self.h_scroll.pack_forget()
        else:
            self.text.config(wrap='none')
            self.h_scroll.pack(side='bottom', fill='x')

    def choose_font(self):
        FontDialog(self.root, self)

    def show_about(self):
        messagebox.showinfo('About', 'Simple Notepad in Python\nBuilt with Tkinter')

    # Status updates
    def _on_modified(self, event=None):
        # reset modified flag (to catch future edits)
        self.text.edit_modified(False)
        self._update_status()

    def _update_status(self):
        row, col = self.text.index('insert').split('.')
        mode = 'WRAP' if self.wrap_var.get() else 'NOWRAP'
        name = os.path.basename(self.filename) if self.filename else 'Untitled'
        self.status.set(f'{name}    Ln {row}, Col {int(col)+1}    {mode}')

    def _update_title(self):
        name = os.path.basename(self.filename) if self.filename else 'Untitled'
        changed = '*' if self.text.edit_modified() else ''
        self.root.title(f'{name}{changed} - Notepad')


class FindDialog(tk.Toplevel):
    def __init__(self, parent, text_widget):
        super().__init__(parent)
        self.text_widget = text_widget
        self.title('Find')
        self.transient(parent)
        self.resizable(False, False)

        tk.Label(self, text='Find:').grid(row=0, column=0, sticky='e')
        self.find_entry = tk.Entry(self, width=30)
        self.find_entry.grid(row=0, column=1, padx=2, pady=2)
        self.find_entry.focus_set()

        self.match_case = tk.BooleanVar()
        tk.Checkbutton(self, text='Match case', variable=self.match_case).grid(row=1, column=1, sticky='w')

        btn_frame = tk.Frame(self)
        tk.Button(btn_frame, text='Find Next', command=self.find_next).pack(side='left', padx=2)
        tk.Button(btn_frame, text='Cancel', command=self.destroy).pack(side='left')
        btn_frame.grid(row=2, column=1, sticky='e', pady=2)

        self.protocol('WM_DELETE_WINDOW', self.destroy)

    def find_next(self):
        needle = self.find_entry.get()
        if not needle:
            return
        start = self.text_widget.index('insert')
        if self.match_case.get():
            idx = self.text_widget.search(needle, start, stopindex='end')
        else:
            idx = self.text_widget.search(needle, start, nocase=1, stopindex='end')
        if not idx:
            messagebox.showinfo('Find', 'No more matches found')
            return
        end = f"{idx}+{len(needle)}c"
        self.text_widget.tag_remove('find_highlight', '1.0', 'end')
        self.text_widget.tag_add('find_highlight', idx, end)
        self.text_widget.tag_config('find_highlight', underline=True)
        self.text_widget.mark_set('insert', end)
        self.text_widget.see(idx)


class ReplaceDialog(tk.Toplevel):
    def __init__(self, parent, text_widget):
        super().__init__(parent)
        self.text_widget = text_widget
        self.title('Replace')
        self.transient(parent)
        self.resizable(False, False)

        tk.Label(self, text='Find:').grid(row=0, column=0, sticky='e')
        self.find_entry = tk.Entry(self, width=30)
        self.find_entry.grid(row=0, column=1, padx=2, pady=2)

        tk.Label(self, text='Replace:').grid(row=1, column=0, sticky='e')
        self.replace_entry = tk.Entry(self, width=30)
        self.replace_entry.grid(row=1, column=1, padx=2, pady=2)

        self.match_case = tk.BooleanVar()
        tk.Checkbutton(self, text='Match case', variable=self.match_case).grid(row=2, column=1, sticky='w')

        btn_frame = tk.Frame(self)
        tk.Button(btn_frame, text='Replace', command=self.replace_one).pack(side='left', padx=2)
        tk.Button(btn_frame, text='Replace All', command=self.replace_all).pack(side='left', padx=2)
        tk.Button(btn_frame, text='Cancel', command=self.destroy).pack(side='left')
        btn_frame.grid(row=3, column=1, sticky='e', pady=2)

        self.protocol('WM_DELETE_WINDOW', self.destroy)

    def replace_one(self):
        needle = self.find_entry.get()
        repl = self.replace_entry.get()
        if not needle:
            return
        start = self.text_widget.index('insert')
        if self.match_case.get():
            idx = self.text_widget.search(needle, start, stopindex='end')
        else:
            idx = self.text_widget.search(needle, start, nocase=1, stopindex='end')
        if not idx:
            messagebox.showinfo('Replace', 'No matches found')
            return
        end = f"{idx}+{len(needle)}c"
        self.text_widget.delete(idx, end)
        self.text_widget.insert(idx, repl)
        self.text_widget.mark_set('insert', f'{idx}+{len(repl)}c')
        self.text_widget.see('insert')

    def replace_all(self):
        needle = self.find_entry.get()
        repl = self.replace_entry.get()
        if not needle:
            return
        count = 0
        idx = '1.0'
        while True:
            if self.match_case.get():
                idx = self.text_widget.search(needle, idx, stopindex='end')
            else:
                idx = self.text_widget.search(needle, idx, nocase=1, stopindex='end')
            if not idx:
                break
            end = f"{idx}+{len(needle)}c"
            self.text_widget.delete(idx, end)
            self.text_widget.insert(idx, repl)
            idx = f"{idx}+{len(repl)}c"
            count += 1
        messagebox.showinfo('Replace All', f'Replaced {count} occurrence(s)')


class FontDialog(tk.Toplevel):
    def __init__(self, parent, notepad):
        super().__init__(parent)
        self.notepad = notepad
        self.title('Choose Font')
        self.transient(parent)
        self.resizable(False, False)

        tk.Label(self, text='Family:').grid(row=0, column=0, sticky='e')
        families = list(font.families())
        families.sort()
        self.family_var = tk.StringVar(value=self.notepad.current_font_family)
        self.family_box = tk.Listbox(self, listvariable=tk.StringVar(value=families), height=10)
        if self.notepad.current_font_family in families:
            idx = families.index(self.notepad.current_font_family)
            self.family_box.select_set(idx)
            self.family_box.see(idx)
        self.family_box.grid(row=0, column=1, padx=4, pady=4)

        tk.Label(self, text='Size:').grid(row=1, column=0, sticky='e')
        sizes = [8,9,10,11,12,14,16,18,20,24,28,32]
        self.size_var = tk.IntVar(value=self.notepad.current_font_size)
        self.size_box = tk.Listbox(self, listvariable=tk.StringVar(value=list(map(str,sizes))), height=6)
        try:
            idx = sizes.index(self.notepad.current_font_size)
            self.size_box.select_set(idx)
            self.size_box.see(idx)
        except ValueError:
            pass
        self.size_box.grid(row=1, column=1, padx=4, pady=4)

        btn_frame = tk.Frame(self)
        tk.Button(btn_frame, text='OK', command=self.apply).pack(side='left', padx=2)
        tk.Button(btn_frame, text='Cancel', command=self.destroy).pack(side='left')
        btn_frame.grid(row=2, column=1, sticky='e', pady=4)

    def apply(self):
        try:
            sel = self.family_box.curselection()
            if sel:
                family = self.family_box.get(sel[0])
                self.notepad.current_font_family = family
            size_sel = self.size_box.curselection()
            if size_sel:
                size = int(self.size_box.get(size_sel[0]))
                self.notepad.current_font_size = size
            self.notepad.text_font.config(family=self.notepad.current_font_family, size=self.notepad.current_font_size)
            self.notepad.text.configure(font=self.notepad.text_font)
        except Exception:
            pass
        self.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    app = Notepad(root)
    root.mainloop()
