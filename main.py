from PIL import Image
from midiutil import MIDIFile
import threading
import tkinter as tk
from tkinter import filedialog
# from tkinter import messagebox
from tkinter import ttk


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

    def save_as_button_func():
        save_path = filedialog.asksaveasfilename(filetypes=[('MIDI files', '*.mid')])
        save_path += '.mid' if save_path[-4:] != '.mid' else ''
        save_as_label.config(text=save_path)

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

    convert_button = ttk.Button(frame, width=20, text='Convert', command=print)
    convert_button.grid(column=0, row=row, padx=padx, pady=pady + 10)

    current_state_label = ttk.Label(frame, text='')
    current_state_label.grid(column=1, row=row, padx=padx, pady=pady + 10, sticky='W')

    # Start Window
    root.mainloop()


def display_state(state=None):
    state = str(state)
    current_state_label.config(text=state)


def get_info():
    duration = 0
    draw_mode = True
    notes_high = 132
    while 1:
        img_path = input('Where is your image located?\n')
        try:
            file_test = open(img_path, 'r')
            file_test.close()
        except Exception as e:
            print('Incorrect file path given: ' + str(e))
            continue
        break
    while 1:
        save_path = input('Where should the MIDI file be saved?\n')
        try:
            file_test = open(save_path + '.mid', 'w')
            file_test.close()
        except Exception as e:
            print('Incorrect file path given: ' + str(e))
            continue
        break
    while 1:
        try:
            duration = int(input('How many seconds long should the MIDI file be?\n'))
        except ValueError:
            print('Incorrect duration given!')
            continue
        break
    while 1:
        draw_mode_input = input('Do you want to use draw mode? (Y/n)\n').upper()
        if draw_mode_input == 'Y' or draw_mode_input == '':
            draw_mode = True
            break
        elif draw_mode_input == 'N':
            draw_mode = False
            break
        else:
            print('Incorrect answer!')
            continue
    while 1:
        try:
            notes_high_input = int(input('How many notes should the image be high? (max 132)\n'))
        except ValueError:
            print('Please input a number!')
            continue
        if notes_high_input > 132 or notes_high_input < 1:
            print('Your given number is either too high or too low!')
            continue
        else:
            notes_high = notes_high_input
            break
    return [img_path, save_path, duration, draw_mode, notes_high]


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
        for x in range(total_beats):
            display_state('Calculating areas of pixels: Area ' + str(x) + ', ' + str(y))
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
        for area_x in range(len(areas[area_y])):
            area_colors = []
            for pixel_y in range(areas[area_y][area_x][3] - areas[area_y][area_x][1]):
                for pixel_x in range(areas[area_y][area_x][2] - areas[area_y][area_x][0]):
                    display_state('Calculating average color per area: Area '
                                  + str(area_x) + ' ' + str(area_y) + 'Pixel' + str(pixel_x) + ' ' + str(pixel_y))
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
            for x, color in enumerate(colors[y]):
                display_state('Converting to black or white: Color ' + str(x) + ' ' + str(y))
                colors[y][x] = (round((color + 1) / 256) * 256) - 1  # Either -1 or 255
                colors[y][x] += 1 if colors[y][x] == -1 else 0  # Change -1 to 0
        display_state('Converting to black or white: Finished')

    # Add all notes
    display_state('Adding notes to file: Calculating lowest note')
    lowest_note = round((132 - len(colors)) / 2) - 1
    lowest_note += 1 if lowest_note == -1 else 0
    display_state('Adding notes to file: Calculating lowest note: ' + str(lowest_note))
    for y in range(len(colors)):
        for x, color in enumerate(colors[y]):
            display_state('Adding notes to file: Note ' + str(x) + ' ' + str(y))
            if draw_mode and color == 0:
                midi.addNote(0, 0, lowest_note + (len(colors) - y), x, 1, 100)
            elif not draw_mode and color != 0:
                midi.addNote(0, 0, lowest_note + (len(colors) - y), x, 1, color)
    display_state('Adding notes to file: Finished')

    # Save midi file
    display_state('Writing MIDI file to disk')
    with open(save_path + '.mid', 'wb') as file:
        midi.writeFile(file)
    display_state('Finished!')


def main():
    info = get_info()
    write_midi(info[1], get_pixel_averages(int((120 / 60) * info[2]), info[0], info[4]), info[3])


if __name__ == '__main__':
    current_state_label: ttk.Label
    threading.Thread(target=window).start()
