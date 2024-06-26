import os
import zipfile
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from tkinterdnd2 import DND_FILES, TkinterDnD

# Globale Variablen
aktueller_ort = os.path.abspath(__file__)
aktuelles_verzeichnis = os.path.dirname(aktueller_ort)

defaultInputFolderName = "InputAndCacheFolder"
defaultInputPath = os.path.join(aktuelles_verzeichnis, defaultInputFolderName)
selectedDefaultInputPath = ""

defaultOutputFolderName = "Converted"
defaultOutputPath = os.path.join(aktuelles_verzeichnis, defaultOutputFolderName)
selectedDefaultOutputPath = ""

# Funktionen

def ResetAll():
    global selectedDefaultInputPath, selectedDefaultOutputPath
    selectedDefaultInputPath = ""
    selectedDefaultOutputPath = ""
    update_table(selectedDefaultInputPath)
    messagebox.showinfo("Erfolg", "Alle Pfade wurden auf Standard zurückgesetzt")

def changeInputPath():
    global selectedDefaultInputPath
    selectedDefaultInputPath = filedialog.askdirectory()
    if selectedDefaultInputPath:
        messagebox.showinfo("Erfolg", f"Der Standardpfad wurde geändert zu: {selectedDefaultInputPath}")
        update_table(selectedDefaultInputPath)

def changeOutputPath():
    global selectedDefaultOutputPath
    selectedDefaultOutputPath = filedialog.askdirectory()
    if selectedDefaultOutputPath:
        messagebox.showinfo("Erfolg", f"Der Standardpfad wurde geändert zu: {selectedDefaultOutputPath}")

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
    
    try:
        with zipfile.ZipFile(output_path, 'w') as zipf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Überprüfen, ob die Datei sich im InputAndCacheFolder oder einem Unterordner befindet
                    if os.path.commonpath([file_path, folder_path]) == folder_path:
                        zipf.write(file_path, os.path.relpath(file_path, folder_path))
        messagebox.showinfo("Erfolg", f"Dateien wurden erfolgreich nach {output_path} konvertiert.")
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Erstellen des ZIP-Archivs: {e}")

    update_table(folder_path)

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
        os.rename(file, dest_path)
    
    messagebox.showinfo("Erfolg", f"{len(files)} Datei(en) wurden erfolgreich nach {target_folder} verschoben.")
    update_table(target_folder)

def update_table(folder_path):
    for i in table.get_children():
        table.delete(i)
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            table.insert('', 'end', values=(file, os.path.join(root, file), 'ZIP', 'Reset', 'Delete'))

def setup_gui():
    global root, table
    root = TkinterDnD.Tk()
    root.title("ConvertToZip")
    root.geometry("800x600")  # Setze eine Standardgröße für das Fenster

    # Hauptframe für die gesamte GUI
    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    # Oberer Frame für linke und rechte Frames
    top_frame = tk.Frame(main_frame)
    top_frame.pack(side="top", fill="both", expand=True)

    # Linker Frame für Drag-and-Drop
    left_frame = tk.Frame(top_frame)
    left_frame.pack(side="left", fill="both", expand=True)

    # Rechter Frame für Buttons
    right_frame = tk.Frame(top_frame)
    right_frame.pack(side="right", fill="both", expand=True)

    # Drag-and-drop Label im linken Frame
    drop_label = tk.Label(left_frame, text="Ziehen Sie Dateien hierher", width=50, height=10, relief="solid")
    drop_label.pack(pady=20, padx=10)

    drop_label.drop_target_register(DND_FILES)
    drop_label.dnd_bind('<<Drop>>', on_drop)

    # Buttons im rechten Frame
    ResetAllButton = tk.Button(right_frame, text="Reset Path to Default", command=ResetAll)
    ResetAllButton.pack(side="top", pady=10, padx=20, anchor="e")

    ChangeInputPathButton = tk.Button(right_frame, text="Change Input Path to Wanted Default", command=changeInputPath)
    ChangeInputPathButton.pack(side="top", pady=10, padx=20, anchor="e")

    ChangeOutputPathButton = tk.Button(right_frame, text="Change Output Path to Wanted Default", command=changeOutputPath)
    ChangeOutputPathButton.pack(side="top", pady=10, padx=20, anchor="e")

    StartConvertingButton = tk.Button(right_frame, text="Convert Files to Folder that is Set to Default", command=start_conversion)
    StartConvertingButton.pack(side="top", pady=10, padx=20, anchor="e")

    # Unterer Frame für die Tabelle mit Scrollbar
    bottom_frame = tk.Frame(main_frame)
    bottom_frame.pack(side="bottom", fill="both", expand=True)

    # Vertikale Scrollbar für die Tabelle
    yscrollbar = ttk.Scrollbar(bottom_frame, orient="vertical")
    yscrollbar.pack(side="right", fill="y", expand=True)

    # Tabelle mit 5 Spalten und Verknüpfung der vertikalen Scrollbar
    table = ttk.Treeview(bottom_frame, columns=('col1', 'col2', 'col3', 'col4', 'col5'), show='headings', yscrollcommand=yscrollbar.set)
    table.heading('col1', text='Name')
    table.heading('col2', text='Path')
    table.heading('col3', text='Output format')
    table.heading('col4', text='Reset')
    table.heading('col5', text='Delete')

    table.pack(expand=True, fill='both')

    yscrollbar.config(command=table.yview)

    root.mainloop()

# Starte die GUI
setup_gui()
