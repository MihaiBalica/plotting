import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk, Label, Entry, Button, Frame, filedialog, StringVar, OptionMenu
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class SDRPlotter:
    def __init__(self, root):
        self.root = root
        self.root.title("SDR Data Plotter")

        # Create a grid layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.zoom_in_button = None
        self.zoom_out_button = None

        self.sample_rate = 1.0  # Default sample rate in MHz
        self.jump_entry = 0.0

        self.load_data_button = None
        self.plot_button = None

        self.sample_rate_entry = None

        self.figure = None
        self.canvas = None
        self.toolbar = None

        self.input_data_file_path = None

        # Saved mouse position
        self.saved_mouse_x = None

        self.plot_types = ["Time Domain", "Constellation Diagram", "Frequency Domain", "Spectrogram", "IQ Histogram",
                           "Phase vs. Time"]
        self.selected_plot = None

        self.create_widgets()

    def on_key_press(self, event):
        ax = self.figure.get_axes()[0]
        xlim = ax.get_xlim()
        new_xlim = xlim
        x_range = xlim[1] - xlim[0]

        # Move the plot to the left by a certain percentage of the current x-range
        if event.key == 'left':
            pan_percentage = 0.1  # Adjust the pan percentage as needed
            pan_amount = x_range * pan_percentage
            new_xlim = [xlim[0] - pan_amount, xlim[1] - pan_amount]

        # Move the plot to the right by a certain percentage of the current x-range
        elif event.key == 'right':
            pan_percentage = 0.1  # Adjust the pan percentage as needed
            pan_amount = x_range * pan_percentage
            new_xlim = [xlim[0] + pan_amount, xlim[1] + pan_amount]

        ax.set_xlim(new_xlim)
        self.canvas.draw()

    def zoom_in(self):
        # Get the Axes object from the Figure object
        ax = self.figure.get_axes()[0]

        # Get the current limits of the plot
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        # Zoom in by a factor of 2
        xlim = [xlim[0] / 2, xlim[1] / 2]
        # ylim = [ylim[0] / 2, ylim[1] / 2]

        # Set the new limits of the plot
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

        # Redraw the canvas
        self.canvas.draw()

    def zoom_out(self):
        # Get the Axes object from the Figure object
        ax = self.figure.get_axes()[0]

        # Get the current limits of the plot
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        # Zoom out by a factor of 2
        xlim = [xlim[0] * 2, xlim[1] * 2]
        # ylim = [ylim[0] * 2, ylim[1] * 2]

        # Set the new limits of the plot
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

        # Redraw the canvas
        self.canvas.draw()

    def create_widgets(self):
        # Create a Frame to contain the buttons
        button_frame = Frame(self.root)
        button_frame.pack(side="top", fill="x")

        # Add zoom-in and zoom-out buttons
        self.zoom_in_button = Button(button_frame, text="Zoom In", command=self.zoom_in)
        self.zoom_in_button.pack(side="left", padx=5)

        self.zoom_out_button = Button(button_frame, text="Zoom Out", command=self.zoom_out)
        self.zoom_out_button.pack(side="left", padx=5)

        # Load Data Buttons
        self.load_data_button = Button(button_frame, text="Load Input Data", command=self.load_input_data)
        self.load_data_button.pack(side="left", padx=5)  # Align the button to the left with padding

        # Plot Button
        self.plot_button = Button(button_frame, text="Plot Data", state='disabled', command=self.plot_data)
        self.plot_button.pack(side="left", padx=5)  # Align the button to the left with padding

        # Sample Rate Label
        sample_rate_label = Label(button_frame, text="Sample Rate (MHz):")
        sample_rate_label.pack(side="left", padx=5)

        # Sample Rate Entry
        self.sample_rate_entry = Entry(button_frame)
        self.sample_rate_entry.insert(0, str(self.sample_rate))
        self.sample_rate_entry.pack(side="left", padx=5)

        # Entry Field for Timestamp
        self.jump_entry = Entry(button_frame)
        self.jump_entry.pack(side="left", padx=5)

        # Button to Jump to Timestamp
        jump_button = Button(button_frame, text="Jump to Timestamp", command=self.jump_to_timestamp)
        jump_button.pack(side="left", padx=5)

        self.selected_plot = StringVar(self.root)
        self.selected_plot.set(self.plot_types[0])  # Default plot selection

        plot_dropdown = OptionMenu(button_frame, self.selected_plot, *self.plot_types)
        plot_dropdown.pack(side="left", padx=5)
        self.selected_plot.trace("w", self.on_dropdown_change)

        # Create Matplotlib Figure and Subplot
        self.figure = plt.figure()
        # ax = self.figure.add_subplot(111)

        # Matplotlib Canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        # Bind the left and right arrow keys to the ax.scroll() method
        self.canvas.mpl_connect('key_press_event', self.on_key_press)

        # Saved mouse position
        self.saved_mouse_x = None

        # Matplotlib Navigation Toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.root)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack()

    def load_input_data(self):
        file_path = filedialog.askopenfilename(title="Select SDR Input Data File",
                                               filetypes=(("Binary Files", "*.bin"), ("All Files", "*.*")))
        if file_path:
            self.input_data_file_path = file_path
            self.plot_button.config(state='active')
        else:
            print("No file selected.")

    def jump_to_timestamp(self):
        try:
            timestamp = float(self.jump_entry.get())
        except ValueError:
            print("Invalid timestamp. Please enter a valid number.")
            return

        ax = self.figure.get_axes()[0]

        # Get the current x-limits
        current_x_limits = ax.get_xlim()

        new_x_limits = (timestamp, timestamp + (current_x_limits[1] - current_x_limits[0]))

        # Update the x-limits of the plot without redrawing the entire plot
        ax.set_xlim(new_x_limits)
        self.canvas.draw_idle()

    def plot_data(self):
        if self.input_data_file_path is None:
            print("No data file selected. Please load a data file.")
            return

        try:
            self.sample_rate = float(self.sample_rate_entry.get())
        except ValueError:
            print("Invalid sample rate. Please enter a valid number.")
            return

        # Read the binary file
        samples = np.fromfile(self.input_data_file_path, dtype=np.complex64)

        plot_type = self.selected_plot.get()

        self.figure.clear()
        ax = self.figure.add_subplot(1, 1, 1)

        if plot_type == "Time Domain":
            time_axis = np.arange(len(samples)) / (self.sample_rate * 1e6)
            ax.plot(time_axis, np.real(samples), label='I')
            ax.plot(time_axis, np.imag(samples), label='Q')
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Amplitude')
            ax.set_title('SDR Input Data in Time Domain')
            ax.legend()

        elif plot_type == "Constellation Diagram":
            ax.scatter(np.real(samples), np.imag(samples), s=5)
            ax.set_title('Constellation Diagram')
            ax.set_xlabel('I')
            ax.set_ylabel('Q')

        elif plot_type == "Frequency Domain":
            sampling_rate = self.sample_rate * 1e6
            spectrum = np.fft.fft(samples)
            spectrum_shifted = np.fft.fftshift(spectrum)

            freq_axis = np.fft.fftfreq(len(samples), 1 / sampling_rate) / 1e6
            freq_axis_shifted = freq_axis - min(freq_axis)

            magnitude_spectrum = np.abs(spectrum_shifted)  # Calculate magnitude of the shifted spectrum
            magnitude_spectrum_dB = 20 * np.log10(magnitude_spectrum)

            ax.plot(freq_axis_shifted, magnitude_spectrum_dB)
            ax.set_title('Frequency Domain Representation')
            ax.set_xlabel('Frequency (MHz)')
            ax.set_ylabel('Magnitude (dB)')

        elif plot_type == "Spectogram":
            # Spectrogram
            ax.specgram(samples, Fs=1)
            ax.set_title('Spectrogram')
            ax.set_xlabel('Time')
            ax.set_ylabel('Frequency')

        elif plot_type == "IQ Histogram":
            # IQ Histogram
            ax.hist2d(np.real(samples), np.imag(samples), bins=50)
            ax.set_title('IQ Histogram')
            ax.set_xlabel('I')
            ax.set_ylabel('Q')

        elif plot_type == "Phase vs. Time":
            # Phase vs. Time Plot
            time_axis = np.arange(len(samples)) / (self.sample_rate * 1e6)
            phase = np.angle(samples)
            ax.plot(time_axis, phase)
            ax.set_title('Phase vs. Time Plot')
            ax.set_xlabel('Time')
            ax.set_ylabel('Phase')

        ax.minorticks_on()
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        self.canvas.draw()

    def on_dropdown_change(self, *args):
        # Trigger plot update when the dropdown selection changes
        self.plot_data()


if __name__ == "__main__":
    root = Tk()
    app = SDRPlotter(root)
    root.mainloop()
