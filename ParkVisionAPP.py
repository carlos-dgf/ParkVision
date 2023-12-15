# Importing OpenCV for image processing
import cv2
# Importing NumPy for numerical operations
import numpy as np
# Importing JSON for data handling
import json
# Importing Tkinter for GUI creation
import tkinter as tk
from tkinter import filedialog, simpledialog

# Initializing file path variable
file_path = None
# Initializing configuration path variable
config_path = None
# Initializing variable for file type
file_type = None
# Initializing list for storing points
points = []
# Initializing list for parking spaces
parking_spaces = []

# Defining the presentation screen function
def presentation(root):
    root.withdraw()
    
    presentation_window = tk.Toplevel()
    presentation_window.title("ParkVision")
    presentation_window.geometry('600x350')
    presentation_window.geometry("+{}+{}".format(int(presentation_window.winfo_screenwidth()/2 - 200), int(presentation_window.winfo_screenheight()/2 - 150)))
    presentation_window.grab_set()

    top_margin = tk.Frame(presentation_window, height=20)
    top_margin.pack(side='top', fill='x')
    
    title = tk.Label(presentation_window, text="ParkVision", font=("Arial", 16, 'bold'))
    title.pack(pady=10)
    description = tk.Label(presentation_window, text="App for smart parking management. It detects and allocates parking spaces with a simple, user-friendly interface.", wraplength=380, font=("Arial", 12))
    description.pack(pady=10)
    
    developers_info = "Developed By:\nCarlos Gonzalez"
    developers = tk.Label(presentation_window, text=developers_info, justify=tk.CENTER, font=("Arial", 12))
    developers.pack(pady=10)
    
    button_frame = tk.Frame(presentation_window)
    button_frame.pack(pady=20)
    continue_button = tk.Button(button_frame, text="Continue", command=lambda:[presentation_window.destroy(), root.deiconify()], height=2, width=10)
    continue_button.pack(side='left', padx=10)
    exit_button = tk.Button(button_frame, text="Exit", command=lambda:[presentation_window.destroy(), root.destroy()], height=2, width=10)
    exit_button.pack(side='right', padx=10)

# Function to Select Parking Spaces
def define_points(event, x, y, flags, param):
    global points, parking_spaces
    frame_copy = param

    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        
        if len(points) == 2:
            parking_spaces.append(tuple(points))
            cv2.rectangle(frame_copy, points[0], points[1], (0, 255, 0), 2)
# Initializing list for storing points
            points = []

    elif event == cv2.EVENT_RBUTTONDOWN:
        # Delete last Point
        if parking_spaces:
            parking_spaces.pop()
            frame_copy[:] = frame[:]
            for espacio in parking_spaces:
                cv2.rectangle(frame_copy, espacio[0], espacio[1], (0, 255, 0), 2)

    # Dibujar la Leyenda
    info1 = "Key: q - Exit"
    info2 = "Mouse Left - Select"
    info3 = "Mouse Right - Delete"
    cv2.putText(frame_copy, info1, (frame_copy.shape[1] - 200, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    cv2.putText(frame_copy, info2, (frame_copy.shape[1] - 200, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    cv2.putText(frame_copy, info3, (frame_copy.shape[1] - 200, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    cv2.imshow('Select Parking Spaces', frame_copy)

# Supplementary Function for Parking Spaces
def define_spaces():
    Video = cv2.VideoCapture('Parking.mp4') #Change this line to get Live Video
    ret, frame = Video.read()
    if not ret:
        print("Failed to read video. Please check the file path.")
        return
    frame_copy = frame.copy()

    cv2.namedWindow('Select parking spaces')
    cv2.setMouseCallback('Select Parking Spaces', define_points, frame_copy)
    
    while True:
        cv2.imshow('Select Parking Spaces', frame_copy)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit with Q
            break

    cv2.destroyAllWindows()
    Video.release()

    # Save JSON of the Configuration
    with open('Parking.json', 'w') as file:
        json.dump(parking_spaces, file)

# Function to process a frame
def process_frame(frame, parking_spaces):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    occupied_spaces = 0

    for spaces in parking_spaces:
        pt1, pt2 = spaces
        if pt1[0] >= pt2[0] or pt1[1] >= pt2[1]:
            continue
        roi = gray[pt1[1]:pt2[1], pt1[0]:pt2[0]]
        if roi.size == 0:
            continue

        # Detect if the Space is Full or Empty
        blurred_roi = cv2.GaussianBlur(roi, (5, 5), 0)
        edges = cv2.Canny(blurred_roi, 50, 150)
        color = (0, 0, 255) if np.mean(edges) > 10 else (0, 255, 0)
        status = "Full" if color == (0, 0, 255) else "Empty"
        occupied_spaces += 1 if status == "Full" else 0

        # Rectangle and Text
        cv2.rectangle(frame, pt1, pt2, color, 2)
        cv2.putText(frame, status, (pt1[0] + 5, pt1[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # Info and Counter
    total_spaces = len(parking_spaces)
    info1 = "Key: q - Exit"
    cv2.putText(frame, info1, (frame.shape[1] - 180, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    counter = f"Spaces: {total_spaces - occupied_spaces}/{total_spaces}"
    cv2.putText(frame, counter, (frame.shape[1] - 180, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    return frame

# Function to process a Video
def process_video(file_path, config_path):
    video = cv2.VideoCapture(file_path)
    with open(config_path, 'r') as file:
        parking_spaces = json.load(file)

    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break
        frame = process_frame(frame, parking_spaces)
        cv2.imshow('Parking Lot', frame)
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()

# Function to process a Image
def process_image(file_path, config_path):
    image = cv2.imread(file_path)
    if image is None:
        print("Error loading the image:", file_path)
        return
    with open(config_path, 'r') as file:
        parking_spaces = json.load(file)

    image = process_frame(image, parking_spaces)
    cv2.imshow('Parking Lot', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# Function to Ask the User if They Have a Configuration File
def ask_config():
    def answer_config(answer):
        global config_path, file_type
        if answer == 'No':
            define_spaces()
        elif answer == 'Yes':
            config_path = filedialog.askopenfilename(
                title="Select the configuration file",
                filetypes=[("Files JSON", "*.json")]
            )
            if config_path:
                # Call the correct function according to the file type
                if file_type == "Video":
                    process_video(file_path, config_path)
                elif file_type == "Image":
                    process_image(file_path, config_path)
        config_window.destroy()

    config_window = tk.Toplevel()
    config_window.title("Configuration")
    config_window.geometry('300x150')
    config_window.geometry("+{}+{}".format(int(config_window.winfo_screenwidth()/2 - 150), int(config_window.winfo_screenheight()/2 - 75)))
    frame = tk.Frame(config_window)
    frame.pack(pady=20)
    
    tk.Label(frame, text="¿Do you have a configuration file?").pack()
    tk.Button(frame, text="Yes", command=lambda: answer_config('Yes'), height=2, width=10).pack(side='left', padx=10, pady=10)
    tk.Button(frame, text="No", command=lambda: answer_config('No'), height=2, width=10).pack(side='right', padx=10, pady=10)

# Function to Handle Which Type of File the User Will Load Depending on the Selected Option
def select_file(option):
    global file_path, file_type
    file_types = [("All files", "*.*")]
    if option == "Video":
        file_types = [("Video Files", "*.mp4;*.avi;*.mov")]
        file_type = "Video"
    elif option == "Image":
        file_types = [("Image Files", "*.jpg;*.jpeg;*.png")]
        file_type = "Image"

    file_path = filedialog.askopenfilename(filetypes=file_types, title="Select a file")
    if file_path:
        ask_config()

# Function to Handle the Main Interface
def start_interface():
    root = tk.Tk()
    root.title("File Selector")
    root.geometry('400x300')
    root.geometry("+{}+{}".format(int(root.winfo_screenwidth()/2 - 200), int(root.winfo_screenheight()/2 - 100)))

    frame = tk.Frame(root)
    frame.pack(pady=40)

    tk.Button(frame, text="Read Video", command=lambda: select_file("Video"), height=2, width=20).pack(pady=10)
    tk.Button(frame, text="Read Image", command=lambda: select_file("Image"), height=2, width=20).pack(pady=10)

    exit_button = tk.Button(root, text="Exit", command=root.destroy, height=2, width=20)
    exit_button.pack(pady=10)

    presentation(root)

    root.mainloop()

# Iniciar la Interfaz
start_interface()