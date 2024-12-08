import cv2
import numpy as np
import tensorflow as tf
import tkinter as tk
from tkinter import messagebox
import csv
import threading

# Load the model
model = tf.keras.models.load_model('engage_not_engage_cnn_modelv2.h5')

# Class labels for 4 engagement levels
class_labels = ["Engagement 0", "Engagement 1", "Engagement 2", "Engagement 3"]

# Initialize global variables for recording state
is_recording = False
engagement_counts = {"Engagement 0": 0, "Engagement 1": 0, "Engagement 2": 0, "Engagement 3": 0}
csv_file = "engagement_results.csv"

# Initialize the video capture
cap = cv2.VideoCapture(0)  # 0 for the default camera

# Function to record the frames and classify them
def start_recording():
    global is_recording, engagement_counts
    is_recording = True

    # Open the CSV file and write the header
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Frame", "Engagement Level", "Confidence"])

    # Start capturing frames
    while is_recording:
        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to read the camera feed.")
            break

        # Preprocess the frame for prediction
        resized_frame = cv2.resize(frame, (64, 64))  # Match the input shape of the model
        normalized_frame = resized_frame / 255.0  # Normalize pixel values
        input_data = np.expand_dims(normalized_frame, axis=0)  # Add batch dimension

        # Perform prediction
        predictions = model.predict(input_data)
        predicted_class = np.argmax(predictions, axis=1)[0]
        confidence = np.max(predictions)

        # Map the predictions to engagement levels
        engagement_level = class_labels[predicted_class]

        # Update engagement counts
        engagement_counts[engagement_level] += 1

        # Save the results to CSV
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([frame, engagement_level, confidence])

        # Overlay the result on the video feed
        label = f"{engagement_level}: {confidence:.2f}"
        cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Display the frame
        cv2.imshow("Real-Time Testing", frame)

        # Break the loop if 'q' is pressed (in case of emergency stop)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Function to stop recording
def stop_recording():
    global is_recording
    is_recording = False
    cap.release()
    cv2.destroyAllWindows()

    # Show the results of the engagement levels
    message = "Total Engagement Counts:\n"
    for engagement_level, count in engagement_counts.items():
        message += f"{engagement_level}: {count}\n"
    
    messagebox.showinfo("Recording Stopped", message)

# Function to handle start/stop recording
def toggle_recording():
    if is_recording:
        stop_button.config(state=tk.DISABLED)
        start_button.config(state=tk.NORMAL)
        stop_recording()
    else:
        start_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.NORMAL)
        threading.Thread(target=start_recording, daemon=True).start()

# Setting up the Tkinter GUI
root = tk.Tk()
root.title("Engagement Detection")

start_button = tk.Button(root, text="Start Recording", command=toggle_recording, width=20, height=2)
start_button.pack(pady=20)

stop_button = tk.Button(root, text="Stop Recording", state=tk.DISABLED, command=toggle_recording, width=20, height=2)
stop_button.pack(pady=20)

root.mainloop()
