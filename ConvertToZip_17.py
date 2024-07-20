import os
import zipfile
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from tkinterdnd2 import DND_FILES, TkinterDnD
import json
import shutil


# Austausch der Messegeboxen mit eigenen Benachrichtigungen in Feldern mit Verblassungseffekt (austellbar)

# Freie Auswahl der Dateiformate (mehrere Dateiformate als Ausgänge, auch mehrere für eine Datei/ Ordner)
# right click Funktion hinzufügen und wie oben prüfen. Menü wie beim Dropdown hinzufügen mit vom Element abhängigen Inhalten

# Farblicher Unterschied Ordner und Dateien
# Auto Convert mit Timer frei auswählbar von sofort bis 5 Minuten (nur mit löschen alter Datein), und 5 bis 59 Minuten und 59 Sekunden auch mit Erhalt 

# Suche nach letztem Speicherort (Logdaten als Array) und gelagerten Dateien, wenn verschoben (Frage nach löschen alter Default Ordner/ öffnen Explorer)
 


# Globale Variablen
aktueller_ort = os.path.abspath(__file__)
aktuelles_verzeichnis = os.path.dirname(aktueller_ort)

defaultInputFolderName = "InputAndCacheFolder"
defaultInputPath = os.path.join(aktuelles_verzeichnis, defaultInputFolderName)
selectedDefaultInputPath = ""

defaultOutputFolderName = "Converted"
defaultOutputPath = os.path.join(aktuelles_verzeichnis, defaultOutputFolderName)
selectedDefaultOutputPath = ""

config_file_path = os.path.join(aktuelles_verzeichnis, "config.json")

# Funktionen

def load_config():
    global selectedDefaultInputPath, selectedDefaultOutputPath
    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as config_file:
            config = json.load(config_file)
            selectedDefaultInputPath = config.get('input_path', "")
            selectedDefaultOutputPath = config.get('output_path', "")
    else:
        selectedDefaultInputPath = ""
        selectedDefaultOutputPath = ""

def save_config():
    config = {
        'input_path': selectedDefaultInputPath,
        'output_path': selectedDefaultOutputPath
    }
    with open(config_file_path, 'w') as config_file:
        json.dump(config, config_file)

def ResetAll():
    global selectedDefaultInputPath, selectedDefaultOutputPath
    selectedDefaultInputPath = ""
    selectedDefaultOutputPath = ""
    messagebox.showinfo("Erfolg", "Alle Pfade wurden auf Standard zurückgesetzt")
    save_config()  # Speichern Sie die Konfiguration
    update_table()

def update_table():
    folder_path = selectedDefaultInputPath or defaultInputPath
    table.delete(*table.get_children())

    if os.path.exists(folder_path):
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path) or os.path.isdir(item_path):
                table.insert('', 'end', values=(item, 'X'))

def changeInputPath():
    global selectedDefaultInputPath
    selectedDefaultInputPath = filedialog.askdirectory()
    if selectedDefaultInputPath:
        messagebox.showinfo("Erfolg", f"Der Standardpfad wurde geändert zu: {selectedDefaultInputPath}")
        save_config()  # Speichern Sie die Konfiguration
        update_table()
        
def changeOutputPath():
    global selectedDefaultOutputPath
    selectedDefaultOutputPath = filedialog.askdirectory()
    if selectedDefaultOutputPath:
        messagebox.showinfo("Erfolg", f"Der Standardpfad wurde geändert zu: {selectedDefaultOutputPath}")
        save_config()  # Speichern Sie die Konfiguration

def createFolder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
        while not os.path.exists(folder):
            time.sleep(0.1)
        print(f"Ordner '{folder}' wurde erstellt")

def FolderChecker(folder):
    if not os.path.exists(folder):
        createFolder(folder)

def create_zip(folder_path, output_path):
    if not os.path.exists(folder_path):
        messagebox.showerror("Fehler", "Der angegebene Ordnerpfad existiert nicht.")
        return
    
    base_output_path, ext = os.path.splitext(output_path)
    counter = 1
    while os.path.exists(output_path):
        output_path = f"{base_output_path} ({counter}){ext}"
        counter += 1

    try:
        with zipfile.ZipFile(output_path, 'w') as zipf:
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path):
                    zipf.write(file_path, os.path.relpath(file_path, folder_path))
                    os.remove(file_path)  # Datei nach dem Hinzufügen löschen
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Ordner nach dem Hinzufügen löschen
        messagebox.showinfo("Erfolg", f"Dateien wurden erfolgreich nach {output_path} konvertiert und gelöscht.")
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Erstellen des ZIP-Archivs: {e}")
    update_table()

def start_conversion():
    folder_path = selectedDefaultInputPath or defaultInputPath
    output_folder = selectedDefaultOutputPath or defaultOutputPath
    output_path = os.path.join(output_folder, 'output.zip')

    FolderChecker(output_folder)
    FolderChecker(folder_path)

    threading.Thread(target=create_zip, args=(folder_path, output_path)).start()

def on_drop(event):
    files = root.tk.splitlist(event.data)
    target_folder = selectedDefaultInputPath or defaultInputPath
    
    if not os.path.exists(target_folder):
        createFolder(target_folder)
    
    for file in files:
        file_name = os.path.basename(file)
        dest_path = os.path.join(target_folder, file_name)
        if os.path.isfile(file):
            shutil.copy(file, dest_path)
        elif os.path.isdir(file):
            shutil.copytree(file, dest_path)
    
    messagebox.showinfo("Erfolg", f"{len(files)} Datei(en) wurden erfolgreich nach {target_folder} kopiert.")
    update_table()

def copy_to_input_path():
    files = filedialog.askopenfilenames()
    target_folder = selectedDefaultInputPath or defaultInputPath
    
    if not os.path.exists(target_folder):
        createFolder(target_folder)
    
    for file in files:
        file_name = os.path.basename(file)
        dest_path = os.path.join(target_folder, file_name)
        if os.path.isfile(file):
            shutil.copy(file, dest_path)
        elif os.path.isdir(file):
            shutil.copytree(file, dest_path)
    
    messagebox.showinfo("Erfolg", f"{len(files)} Datei(en) wurden erfolgreich nach {target_folder} kopiert.")
    update_table()

def handle_menu_selection(selection):
    if selection == "Reset Path to Default":
        ResetAll()
    elif selection == "Change Input Path to Wanted Default":
        changeInputPath()
    elif selection == "Change Output Path to Wanted Default":
        changeOutputPath()
    elif selection == "Convert Files to Folder that is Set to Default":
        start_conversion()
    elif selection == "Copy File to Input Path":
        copy_to_input_path()


class ToolTip:
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.current_text = ""

    def hidetip(self):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None
            self.current_text = ""

    def showtip(self, text, x, y):
        # Zerstöre den aktuellen Tooltip nur, wenn sich der Text ändert
        if self.tipwindow and self.current_text != text:
            self.hidetip()

        if not self.tipwindow:
            self.current_text = text

            # Text umbrechen
            wrap_length = 40  # Max Zeichen pro Zeile
            wrapped_text = self.wrap_text(text, wrap_length)

            self.tipwindow = tk.Toplevel(self.widget)
            self.tipwindow.wm_overrideredirect(True)
            self.tipwindow.wm_geometry("+%d+%d" % (x, y))
            self.tipwindow.config(bg="#ffffe0")  # Hintergrundfarbe
            label = tk.Label(self.tipwindow, text=wrapped_text, justify=tk.LEFT,
                             background="#ffffe0", relief=tk.SOLID, borderwidth=1)
            label.pack(ipadx=1)

    def wrap_text(self, text, wrap_length):
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            if sum(len(w) for w in current_line) + len(current_line) + len(word) > wrap_length:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)
        lines.append(' '.join(current_line))  # Fügt die letzte Zeile hinzu

        return '\n'.join(lines)

def create_tooltip(widget, text):
    tooltip = ToolTip(widget)

    def enter(event):
        row_id = widget.identify_row(event.y)
        col_id = widget.identify_column(event.x)

        if row_id and col_id and int(col_id[1:]) - 1 < 2:
            col_index = int(col_id[1:]) - 1  # Konvertiert in 0-basierte Index
            bbox = widget.bbox(row_id, col_id)
            if bbox:
                x, y, width, height = bbox

                x = widget.winfo_rootx() + x + width // 2  # Zentriert über der Zelle
                y = widget.winfo_rooty() + y + height  # Position Tooltip unterhalb der Zelle
                cell_value = widget.set(row_id, col_id)
                tooltip.showtip(cell_value, x, y)

    def leave(event):
        tooltip.hidetip()

    widget.bind('<Motion>', enter)
    widget.bind('<Leave>', leave)

def update_table():
    folder_path = selectedDefaultInputPath or defaultInputPath
    table.delete(*table.get_children())

    if os.path.exists(folder_path):
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path) or os.path.isdir(item_path):
                table.insert('', 'end', values=(item, 'X'))


def on_double_click(event):
    item = table.identify_row(event.y)
    column = table.identify_column(event.x)
    if column == '#5':  # Column 5 corresponds to the 'Delete' column
        values = table.item(item, 'values')
        print(f"DEBUG: values = {values}")  # Debugging-Ausgabe
        if len(values) >= 2:  # Ensure that there are enough values
            file_path = values[1]
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            table.delete(item)  # Remove the item from the table
            messagebox.showinfo("Information", f"Die Datei {values[0]} wurde gelöscht.")
        else:
            messagebox.showwarning("Warnung", "Ungültiger Eintrag ausgewählt.")


def setup_gui():
    global root, table

    # Lade Konfiguration
    load_config()

    # Hauptfenster
    root = TkinterDnD.Tk()
    root.title("ConvertToZip")
    root.geometry("800x600")
    root.minsize(700, 500)

    # Unterteilung des Fensters in Frames
    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    top_frame = tk.Frame(main_frame)
    top_frame.pack(side="top", fill="both", expand=True)

    bottom_frame = tk.Frame(main_frame)
    bottom_frame.pack(side="bottom", fill="both", expand=True)

    left_frame = tk.Frame(top_frame)
    left_frame.pack(side="left", fill="both", expand=True)

    right_frame = tk.Frame(top_frame)
    right_frame.pack(side="right", fill="both", expand=True)

    # Variabeln für die GUI
    frameWidth = main_frame.winfo_width()

    # Nutzeroberfläche

    # Drag-and-drop Label im linken Frame
    drop_label = tk.Label(left_frame, text="Drag and Drop", relief="solid")
    drop_label.pack(padx=20, pady=20, expand=True, fill="both")

    drop_label.drop_target_register(DND_FILES)
    drop_label.dnd_bind('<<Drop>>', on_drop)
    drop_label.bind("<Double-1>", lambda event: copy_to_input_path())  # Doppelklick-Event binden

    # Button im rechten Frame, der das Menü öffnet
    options_button = tk.Button(right_frame, text="Options", command=lambda: show_menu(options_button))
    options_button.pack(side="top", pady=10, padx=20, anchor="e")

    # Menü, das bei Button-Klick angezeigt wird
    options_menu = tk.Menu(root, tearoff=0)
    options_menu.add_command(label="Reset Path to Default", command=lambda: handle_menu_selection("Reset Path to Default"))
    options_menu.add_command(label="Change Input Path to Wanted Default", command=lambda: handle_menu_selection("Change Input Path to Wanted Default"))
    options_menu.add_command(label="Change Output Path to Wanted Default", command=lambda: handle_menu_selection("Change Output Path to Wanted Default"))
    options_menu.add_command(label="Copy File to Input Path", command=lambda: handle_menu_selection("Copy File to Input Path"))

    # Funktion zum Anzeigen des Menüs an einer bestimmten Position


    # Funktion zum Anzeigen des Menüs an einer bestimmten Position
    def show_menu(widget):
        x = widget.winfo_rootx()
        y = widget.winfo_rooty() + widget.winfo_height()
        options_menu.tk_popup(x, y)

    # Zentriere den StartConvertingButton im rechten Frame und gleiche seine Unterseite mit der des Drag-and-Drop-Labels ab
    StartConvertingButton = tk.Button(right_frame, text="Convert Files", command=start_conversion)
    StartConvertingButton.place(relx=0.5, rely=drop_label.winfo_y() + drop_label.winfo_height(), anchor="s")
    StartConvertingButton.pack(side="bottom", pady=(0, 20))

    # Tabelle mit 5 Spalten und Verknüpfung der vertikalen Scrollbar
    table = ttk.Treeview(bottom_frame, columns=('col1', 'col2'), show='headings')
    table.heading('col1', text='Name')
    table.heading('col2', text='Delete')


    # Setze die initialen Spaltenbreiten
    table.column('col1', width=frameWidth * 600)
    table.column('col2', width=frameWidth * 50, anchor='center')
    
    
    table.pack(expand=True, fill='both', padx=20)

    update_table()
    
    # Tooltips für die Tabelle hinzufügen
    create_tooltip(table, "Tooltip")

    root.bind("<Double-1>", on_double_click)

    root.mainloop()

# Starte die GUI
setup_gui() 
