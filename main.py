from PIL import Image
from midiutil import MIDIFile
import threading
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import subprocess
import os


def window(height=300, width=550):
    global current_state_label

    # Window properties
    root = tk.Tk()
    root.resizable(False, False)
    root.title('Img2Midi')
    root.iconbitmap(default='logo.ico')
    ttk.Style().theme_use('vista')

    def choose_image_button_func():
        img_path = filedialog.askopenfilename(filetypes=[('Image files', '*.png *.jpg *.jpeg *.gif')])
        choose_image_label.config(text=img_path)
        info['img_path'] = img_path

    def save_as_button_func():
        save_path = filedialog.asksaveasfilename(filetypes=[('MIDI files', '*.mid')])
        save_path += '.mid' if save_path[-4:] != '.mid' else ''
        save_as_label.config(text=save_path)
        info['save_path'] = save_path

    def convert():
        info['duration'] = int(duration_entry_text.get())
        info['notes_high'] = int(height_entry_text.get())
        info['draw_mode'] = True if draw_mode_checkbutton_state == 1 else False

        if info['img_path'] == '' or info['save_path'] == '':
            messagebox.showerror('Error!', 'You need to give file paths for both input and output first!')
            return

        threading.Thread(target=main).start()

    # Canvas and Frame
    canvas = tk.Canvas(root, height=height, width=width)
    canvas.pack()

    frame = tk.Frame(root, bd=15)
    frame.place(relheight=1, relwidth=1)

    padx = 15
    pady = 10

    # 1st row: choose image dialog
    row = 0

    choose_image_button = ttk.Button(frame, text='Choose Image', width=20, command=choose_image_button_func)
    choose_image_button.grid(column=0, row=row, padx=padx, pady=pady)

    choose_image_label = ttk.Label(frame, text='')
    choose_image_label.grid(column=1, row=row, padx=padx, pady=pady, sticky='W')

    # 2nd row: save as dialog
    row += 1

    save_as_button = ttk.Button(frame, text='Save as', width=20, command=save_as_button_func)
    save_as_button.grid(column=0, row=row, padx=padx, pady=pady)

    save_as_label = ttk.Label(frame, text='')
    save_as_label.grid(column=1, row=row, padx=padx, pady=pady, sticky='W')

    # 3rd row: duration input
    row += 1

    duration_label = ttk.Label(frame, text='Duration in seconds:')
    duration_label.grid(column=0, row=row, padx=padx, pady=pady, sticky='E')

    duration_entry_text = tk.StringVar()
    duration_entry_text.set('60')
    duration_entry = ttk.Entry(frame, width=10, textvariable=duration_entry_text, justify='right')
    duration_entry.grid(column=1, row=row, padx=padx, pady=pady, sticky='W')

    # 4th row: height input
    row += 1

    height_label = ttk.Label(frame, text='Height in notes:')
    height_label.grid(column=0, row=row, padx=padx, pady=pady, sticky='E')

    height_entry_text = tk.StringVar()
    height_entry_text.set('100')
    height_entry = ttk.Entry(frame, width=10, textvariable=height_entry_text, justify='right')
    height_entry.grid(column=1, row=row, padx=padx, pady=pady, sticky='W')

    # 5th row: draw mode toggle
    row += 1

    draw_mode_label = ttk.Label(frame, text='Draw Mode:')
    draw_mode_label.grid(column=0, row=row, padx=padx, pady=pady, sticky='E')

    draw_mode_checkbutton_state = tk.IntVar()
    draw_mode_checkbutton_state.set(1)
    draw_mode_checkbutton = ttk.Checkbutton(frame, variable=draw_mode_checkbutton_state, takefocus=False)
    draw_mode_checkbutton.grid(column=1, row=row, padx=padx, pady=pady, sticky='W')

    # 6th row: convert button
    row += 1

    convert_button = ttk.Button(frame, width=20, text='Convert', command=convert)
    convert_button.grid(column=0, row=row, padx=padx, pady=pady + 10)

    current_state_label = ttk.Label(frame, text='')
    current_state_label.grid(column=1, row=row, padx=padx, pady=pady + 10, sticky='W')

    # Start Window
    root.mainloop()


def display_state(state=None):
    state = str(state)
    current_state_label.config(text=state)


def get_pixel_averages(total_beats, img_path, notes_high):
    # Open image and convert to grayscale
    display_state('Opening image')
    img = Image.open(img_path).convert('L')
    display_state('Converting image to grayscale')

    # Find area widths based on total beats and notes high
    display_state('Calculating areas of pixels: Initiating')
    areas = []
    for y in range(notes_high):
        areas.append([])
        str_y = (3 - len(str(y))) * '0' + str(y)
        for x in range(total_beats):
            str_x = (3 - len(str(x))) * '0' + str(x)
            display_state('Calculating areas of pixels: Area ' + str_y + ', ' + str_x)
            areas[y].append([round(img.width / total_beats * x),
                             round(img.height / notes_high * y),
                             round(img.width / total_beats * (x + 1) - 1),
                             round(img.height / notes_high * (y + 1) - 1)])
    display_state('Calculating areas of pixels: Finished')

    # Create list of average colors per area
    display_state('Calculating average color per area: Initiating')
    average_colors = []
    for area_y in range(len(areas)):
        average_colors.append([])
        str_y = (3 - len(str(area_y))) * '0' + str(area_y)
        for area_x in range(len(areas[area_y])):
            str_x = (3 - len(str(area_x))) * '0' + str(area_x)
            display_state('Calculating average color per area: Area ' + str_y + ', ' + str_x)
            area_colors = []
            for pixel_y in range(areas[area_y][area_x][3] - areas[area_y][area_x][1]):
                for pixel_x in range(areas[area_y][area_x][2] - areas[area_y][area_x][0]):
                    area_colors.append(img.getpixel((pixel_x + areas[area_y][area_x][0],
                                                     pixel_y + areas[area_y][area_x][1])))
            average_colors[area_y].append(round(sum(area_colors) / len(area_colors)))  # Average color of area
    display_state('Calculating average color per area: Finished')

    return average_colors


def write_midi(save_path, colors, draw_mode):
    # Create midi object
    display_state('Creating MIDI file')
    midi = MIDIFile(1, file_format=1)

    # Set time signature, tempo and instrument
    display_state('Adding time signature')
    midi.addTimeSignature(0, 0, 4, 2, 24)
    display_state('Adding tempo')
    midi.addTempo(0, 0, 120)
    display_state('Adding instrument')
    midi.addProgramChange(0, 0, 0, 0)

    # Convert to black and white if draw mode is on
    if draw_mode:
        display_state('Converting to black or white: Initiating')
        for y in range(len(colors)):
            str_y = (3 - len(str(y))) * '0' + str(y)
            for x, color in enumerate(colors[y]):
                str_x = (3 - len(str(x))) * '0' + str(x)
                display_state('Converting to black or white: Color ' + str_y + ', ' + str_x)
                colors[y][x] = (round((color + 1) / 256) * 256) - 1  # Either -1 or 255
                colors[y][x] += 1 if colors[y][x] == -1 else 0  # Change -1 to 0
        display_state('Converting to black or white: Finished')

    # Add all notes
    display_state('Adding notes to file: Calculating lowest note')
    lowest_note = round((132 - len(colors)) / 2) - 1
    lowest_note += 1 if lowest_note == -1 else 0
    display_state('Adding notes to file: Calculating lowest note: ' + str(lowest_note))
    for y in range(len(colors)):
        str_y = (3 - len(str(y))) * '0' + str(y)
        for x, color in enumerate(colors[y]):
            str_x = (3 - len(str(x))) * '0' + str(x)
            display_state('Adding notes to file: Note ' + str_y + ', ' + str_x)
            if draw_mode and color == 0:
                midi.addNote(0, 0, lowest_note + (len(colors) - y), x, 1, 100)
            elif not draw_mode and color != 0:
                midi.addNote(0, 0, lowest_note + (len(colors) - y), x, 1, color)
    display_state('Adding notes to file: Finished')

    # Save midi file
    display_state('Writing MIDI file to disk')
    if os.path.exists(save_path):
        os.remove(save_path)
    with open(save_path, 'wb') as file:
        midi.writeFile(file)
    display_state('Finished!')
    open_explorer = messagebox.askyesno('Finished!', 'The Image was successfully converted to a MIDI file.\n'
                                        'The result can be found under ' + info['save_path'] +
                                        '\n\nDo you want to open the file explorer?', icon='info')
    if open_explorer:
        save_path_folder = ''
        for directory in save_path.split('/')[:-1]:
            save_path_folder += directory + '\\'
        subprocess.Popen('explorer "' + save_path_folder + '"')


def main():
    img_path = info['img_path']
    save_path = info['save_path']
    duration = info['duration']
    notes_high = info['notes_high']
    draw_mode = info['draw_mode']
    total_beats = 2 * duration

    write_midi(save_path, get_pixel_averages(total_beats, img_path, notes_high), draw_mode)


if __name__ == '__main__':
    current_state_label: ttk.Label
    info = {'img_path': '', 'save_path': '', 'duration': 0, 'notes_high': 0, 'draw_mode': True}
    threading.Thread(target=window).start()
