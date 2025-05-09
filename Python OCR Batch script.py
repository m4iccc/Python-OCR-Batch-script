# ocr_compiler_gui_singlefile_modtime_sort_es_unique_txt.py

# --- Standard Library Imports ---
import tkinter
import tkinter.messagebox
import tkinter.filedialog
import os
import threading
import time
import sys
import queue  # For thread communication
import traceback # For detailed error logging

# --- Third-Party Library Imports ---
# Attempt imports and provide guidance if they fail
try:
    import customtkinter
except ImportError:
    print("ERROR: customtkinter library not found.")
    print("Please install it: pip install customtkinter")
    sys.exit(1)

try:
    import easyocr
except ImportError:
    print("ERROR: easyocr library not found.")
    print("Please install it: pip install easyocr")
    # Also mention dependencies implicitly needed by easyocr
    print("Ensure you also have PyTorch installed (check easyocr documentation).")
    print("You might also need: pip install opencv-python-headless numpy")
    sys.exit(1)

try:
    import cv2 # OpenCV
except ImportError:
    print("ERROR: OpenCV (cv2) library not found.")
    print("Please install it: pip install opencv-python-headless")
    sys.exit(1)

try:
    import numpy as np
except ImportError:
    print("ERROR: numpy library not found.")
    print("Please install it: pip install numpy")
    sys.exit(1)

try:
    # Optional: Check for torch availability for GPU message
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


# --- Constants ---
APP_NAME = "Batch OCR & Compiler (Sort by Mod Time, ES/EN)"
DEFAULT_COMPILED_FILENAME = "_compiled_ocr_output_by_time.txt"
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif')
OCR_LANGUAGES = ['es', 'en'] # Spanish and English

# --- Appearance Settings ---
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")


# ==============================================================================
# --- BACKEND LOGIC FUNCTIONS ---
# ==============================================================================

def find_image_files(folder_path):
    """
    Finds all image files in the specified folder.
    Returns a list of paths sorted by modification time (oldest first), and error_msg.
    """
    images_with_time = []
    try:
        abs_folder_path = os.path.abspath(folder_path)
        if not os.path.isdir(abs_folder_path):
            return None, f"Error: Folder not found or is not a directory: {abs_folder_path}"

        for filename in os.listdir(abs_folder_path):
            # Check BOTH extension and ensure it's a file (not directory)
            base, ext = os.path.splitext(filename)
            if ext.lower() in IMAGE_EXTENSIONS: # Check against our tuple of valid extensions
                full_path = os.path.join(abs_folder_path, filename)
                if os.path.isfile(full_path): # Double-check it's a file
                    try:
                        mod_time = os.path.getmtime(full_path)
                        images_with_time.append((mod_time, full_path))
                    except OSError as e:
                        print(f"Warning: Could not get modification time for {filename}: {e}")
                        images_with_time.append((0, full_path)) # Sorts first if time unreadable

        if not images_with_time:
             return [], "No image files found matching extensions."

        images_with_time.sort(key=lambda item: item[0]) # Sort by mod_time
        sorted_image_files = [path for mod_time, path in images_with_time]
        return sorted_image_files, None # Success

    except Exception as e:
        print(f"Unexpected error in find_image_files for folder: {folder_path}")
        print(traceback.format_exc())
        return None, f"Unexpected error accessing folder {folder_path}: {e}"


# --- MODIFIED: Function to generate the unique txt filename ---
def get_unique_txt_path(image_path):
    """Generates the unique .txt filename based on the image path."""
    # Example: /path/to/image.png -> /path/to/image.png.txt
    return image_path + '.txt'


def check_existing_txt_files(folder_path):
    """Checks if any unique .txt files corresponding to image files exist."""
    image_files, error = find_image_files(folder_path)
    if error or not image_files: return False

    for img_path in image_files:
        # Use the new function to check for the unique filename
        unique_txt_path = get_unique_txt_path(img_path)
        if os.path.exists(unique_txt_path): return True
    return False


# --- MODIFIED: perform_batch_ocr uses unique txt filenames ---
def perform_batch_ocr(folder_path, languages=OCR_LANGUAGES, use_gpu=True, overwrite_mode=True, status_callback=None):
    """
    Performs OCR on images (sorted by mod time) using specified languages.
    Saves output to unique .txt files (imagename.ext.txt).
    Skips based on overwrite_mode.
    Returns (processed_count, skipped_count, error_count, error_message).
    """
    def log(msg):
        if status_callback:
            try: status_callback(msg)
            except Exception as e: print(f"Error in status_callback: {e}")

    log(f"OCR Task: Scanning folder for images (sorted by modification time): {folder_path}")
    image_files, error = find_image_files(folder_path)

    if error: return 0, 0, 0, error
    if not image_files: return 0, 0, 0, "No image files found in the specified folder."

    log(f"OCR Task: Found {len(image_files)} image file(s). Processing oldest first.")

    processed_count, error_count, skipped_count = 0, 0, 0
    reader = None

    ocr_needed = False
    if overwrite_mode: ocr_needed = True
    else:
        for image_path in image_files:
            # Check existence using the unique filename format
            unique_txt_path = get_unique_txt_path(image_path)
            if not os.path.exists(unique_txt_path):
                ocr_needed = True; break

    if not ocr_needed and not overwrite_mode:
        log("OCR Task: All images seem to have existing unique .txt files and overwrite is OFF. Skipping OCR.")
        skipped_count = len(image_files)
        return 0, skipped_count, 0, None

    log(f"OCR Task: Initializing EasyOCR for languages: {languages} (GPU: {use_gpu})")
    try:
        reader = easyocr.Reader(languages, gpu=use_gpu)
        log("OCR Task: EasyOCR initialized successfully.")
    except Exception as e:
        err_msg = f"Error initializing EasyOCR: {e}\nCheck dependencies (PyTorch, CUDA if using GPU)."
        log(f"!!! {err_msg} !!!")
        return 0, 0, 0, err_msg

    total_start_time = time.time()

    for i, image_path in enumerate(image_files):
        filename = os.path.basename(image_path)
        # --- Use the new function to get the unique output path ---
        output_filename = get_unique_txt_path(image_path)
        output_txt_basename = os.path.basename(output_filename) # For logging

        # --- Check for existing file using unique name ---
        if not overwrite_mode and os.path.exists(output_filename):
            log(f"---> Skipping ({i+1}/{len(image_files)}): {filename} (using existing '{output_txt_basename}')")
            skipped_count += 1
            continue

        log(f"===> Processing ({i+1}/{len(image_files)}): Image '{filename}'")
        start_time = time.time()

        try:
            # --- Image Loading ---
            log(f"     Reading image file: {image_path}")
            with open(image_path, "rb") as f: img_bytes = f.read()
            if not img_bytes: raise IOError(f"File is empty: {filename}")

            img_np = np.frombuffer(img_bytes, np.uint8)
            log(f"     Decoding image data for: {filename}")
            img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
            if img is None:
                img = cv2.imdecode(img_np, cv2.IMREAD_UNCHANGED)
                if img is None: raise IOError(f"OpenCV could not decode image: {filename}")
                if len(img.shape) > 2 and img.shape[2] == 4:
                     log(f"     INFO: Converting RGBA/BGRA image to BGR for {filename}")
                     img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            # --- OCR Execution ---
            if reader is None: raise RuntimeError("EasyOCR reader was not initialized.")
            log(f"     Performing OCR ({'/'.join(languages)}) on image data from: {filename}")
            results = reader.readtext(img, detail=0, paragraph=True)
            extracted_text = "\n".join(results).strip()
            elapsed_time = time.time() - start_time
            log(f"     OCR complete for {filename} in {elapsed_time:.2f}s. Text length: {len(extracted_text)}")

            # --- Save to UNIQUE TXT File ---
            log(f"     Saving extracted text to unique file: '{output_txt_basename}'")
            try:
                with open(output_filename, 'w', encoding='utf-8') as f:
                    f.write(extracted_text)
                log(f"     Successfully saved: '{output_txt_basename}'")
                processed_count += 1
            except Exception as e:
                error_count += 1
                log(f"     !!! Error SAVING text file '{output_txt_basename}': {e} !!!")

        except Exception as e:
            log(f"!!! Error PROCESSING image '{filename}': {e} !!!")
            log(f"     Full image path with error: {image_path}")
            # log(traceback.format_exc()) # Uncomment for full traceback
            error_count += 1

    total_elapsed_time = time.time() - total_start_time
    summary = f"OCR Task Finished. Processed: {processed_count}, Skipped: {skipped_count}, Errors: {error_count}, Time: {total_elapsed_time:.2f}s"
    log(summary)

    return processed_count, skipped_count, error_count, None


# --- MODIFIED: compile_text_files reads unique txt filenames ---
def compile_text_files(input_folder, output_file, status_callback=None):
    """
    Compiles unique .txt files (imagename.ext.txt) based on the modification time
    of their corresponding image files (oldest first).
    Includes a separator with the unique source filename before each file's content.
    Returns (compiled_count, error_message).
    """
    def log(msg):
        if status_callback:
            try: status_callback(msg)
            except Exception as e: print(f"Error in status_callback: {e}")

    log(f"Compile Task: Starting Text Compilation")
    log(f"Compile Task: Finding images sorted by modification time in: {input_folder}")

    # --- Step 1: Get the correctly time-sorted list of IMAGE files ---
    image_files, error = find_image_files(input_folder)

    if error:
        err_msg = f"Compile Task: Error finding image files needed for ordering: {error}"
        log(f"!!! {err_msg} !!!")
        return 0, err_msg
    if not image_files:
        msg = "Compile Task: No image files found. Nothing to compile."
        log(msg)
        return 0, None

    log(f"Compile Task: Found {len(image_files)} images. Will compile corresponding unique .txt files in this order (oldest first).")

    # --- Step 2: Iterate through SORTED image list and process corresponding UNIQUE .txt files ---
    compiled_count = 0
    error_in_compilation = False
    output_base_name = os.path.basename(output_file) # To avoid compiling itself

    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for i, image_path in enumerate(image_files):
                image_filename = os.path.basename(image_path)
                # --- Construct the expected UNIQUE .txt file path ---
                unique_txt_filepath = get_unique_txt_path(image_path)
                unique_txt_filename = os.path.basename(unique_txt_filepath)

                # Skip if the txt file happens to be the compilation target itself (unlikely now)
                if unique_txt_filename == output_base_name:
                    log(f"  Skipping '{unique_txt_filename}' as it is the compilation target file.")
                    continue

                log(f"  Checking for unique .txt file ({i+1}/{len(image_files)}): '{unique_txt_filename}' (from image '{image_filename}')")

                # Check if the corresponding UNIQUE .txt file exists
                if os.path.isfile(unique_txt_filepath):
                    try:
                        log(f"    Reading content from: '{unique_txt_filename}'")
                        with open(unique_txt_filepath, 'r', encoding='utf-8') as infile:
                            content = infile.read().strip()
                        log(f"    Read {len(content)} characters.")

                        # --- Use the UNIQUE .txt filename in the separator ---
                        leading_newlines = "\n\n" if compiled_count > 0 else ""
                        separator = f"{leading_newlines}{'=' * 60}\n=== Source File: {unique_txt_filename} ===\n{'=' * 60}\n\n"

                        log(f"    Writing separator and content for '{unique_txt_filename}' to output.")
                        outfile.write(separator)
                        if content:
                            outfile.write(content)
                        else:
                            log(f"    Note: Source file '{unique_txt_filename}' was empty.")
                        compiled_count += 1

                    except Exception as e:
                        error_in_compilation = True
                        log(f"    !!! Warning: Could not read or process file '{unique_txt_filename}'. Error: {e} !!!")
                        error_marker = f"\n\n{'!' * 60}\n!!! Error processing file: {unique_txt_filename} - {e} !!!\n{'!' * 60}\n\n"
                        try: outfile.write(error_marker); log(f"    Wrote error marker to output for '{unique_txt_filename}'.")
                        except Exception as write_err: log(f"    !!! Additionally failed to write error marker to output file: {write_err} !!!")
                else:
                    # Corresponding unique .txt file does not exist
                    log(f"    Skipping: Corresponding unique file '{unique_txt_filename}' not found for image '{image_filename}'.")


        # --- Compilation Loop Finished ---
        total_expected = len(image_files)
        summary = f"Compile Task Finished. Compiled content from {compiled_count}/{total_expected} existing source file(s) into:"
        log(summary)
        log(os.path.abspath(output_file))

        if compiled_count == 0 and len(image_files) > 0: log("Compile Task: Warning - No unique .txt files were available for compilation.")
        if error_in_compilation:
             log("Compile Task: Completed, but one or more source .txt files could not be read/processed.")
             return compiled_count, "Compilation completed with errors reading source files (check log)."
        else:
             if compiled_count < total_expected: log(f"Compile Task: Note - {total_expected - compiled_count} expected unique .txt file(s) were not found.")
             return compiled_count, None # Success

    except IOError as e: # Error writing the main output file
        err_msg = f"Compile Task: Critical Error writing to output file '{output_file}': {e}"
        log(f"!!! {err_msg} !!!"); return compiled_count, err_msg
    except Exception as e: # Other unexpected errors
        err_msg = f"Compile Task: An unexpected critical error occurred during compilation: {e}"
        log(f"!!! {err_msg} !!!"); log(traceback.format_exc())
        return compiled_count, err_msg


# ==============================================================================
# --- GUI Application Class (Essentially Unchanged) ---
# ==============================================================================

class App(customtkinter.CTk):
    # --- __init__ and other GUI methods remain the same as the previous version ---
    # They don't need modification as the backend function changes handle the logic.
    # Make sure to copy the complete App class from the previous correct version.
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("700x550")
        self.selected_folder = ""
        self.status_queue = queue.Queue()
        self.processing_thread = None
        self.is_processing = False
        self.grid_columnconfigure(0, weight=0); self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0); self.grid_rowconfigure(1, weight=1)
        # Controls Frame
        self.control_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.control_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="nsew")
        self.control_frame.grid_columnconfigure(0, weight=0); self.control_frame.grid_columnconfigure(1, weight=1); self.control_frame.grid_columnconfigure(2, weight=0)
        self.folder_label = customtkinter.CTkLabel(self.control_frame, text="Image Folder:")
        self.folder_label.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")
        self.folder_path_label = customtkinter.CTkLabel(self.control_frame, text="No folder selected", anchor="w", fg_color="transparent", text_color="gray")
        self.folder_path_label.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.browse_button = customtkinter.CTkButton(self.control_frame, text="Browse...", width=100, command=self.browse_folder)
        self.browse_button.grid(row=0, column=2, padx=(5, 10), pady=10, sticky="e")
        self.run_button = customtkinter.CTkButton(self.control_frame, text="Click me to Batch OCR and Compile!", height=40, command=self.start_processing)
        self.run_button.grid(row=1, column=0, columnspan=3, padx=10, pady=(5, 10), sticky="ew")
        # Status Frame
        self.status_frame = customtkinter.CTkFrame(self)
        self.status_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="nsew")
        self.status_frame.grid_rowconfigure(0, weight=1); self.status_frame.grid_columnconfigure(0, weight=1)
        self.status_textbox = customtkinter.CTkTextbox(self.status_frame, wrap=tkinter.WORD, state="disabled", corner_radius=0, font=("Consolas", 10) or ("Courier New", 10))
        self.status_textbox.grid(row=0, column=0, sticky="nsew")
        self.after(100, self.check_status_queue)

    def browse_folder(self):
        if self.is_processing: return
        folder = tkinter.filedialog.askdirectory(title="Select Folder Containing Images")
        if folder:
            self.selected_folder = folder
            max_len = 60
            display_path = self.selected_folder
            if len(display_path) > max_len: display_path = "..." + display_path[-(max_len-3):]
            theme_text_color = customtkinter.ThemeManager.theme["CTkLabel"]["text_color"]
            self.folder_path_label.configure(text=display_path, text_color=theme_text_color)
            self.log_status(f"Selected folder: {self.selected_folder}")

    def log_status(self, message):
        try:
            self.status_textbox.configure(state="normal")
            if not message.endswith("\n"): message += "\n"
            self.status_textbox.insert(tkinter.END, message)
            self.status_textbox.configure(state="disabled")
            self.status_textbox.see(tkinter.END)
            self.update_idletasks()
        except Exception as e: print(f"Error updating status textbox: {e}")

    def start_processing(self):
        if self.is_processing: tkinter.messagebox.showwarning("Busy", "Processing is already in progress."); return
        if not self.selected_folder or not os.path.isdir(self.selected_folder): tkinter.messagebox.showerror("Error", "Please select a valid image folder first."); return

        overwrite_mode = True
        try: has_existing = check_existing_txt_files(self.selected_folder)
        except Exception as e: tkinter.messagebox.showerror("Error", f"Failed check for existing files:\n{e}"); return

        if has_existing:
            self.log_status("Existing unique OCR (.txt) files found...")
            user_choice = tkinter.messagebox.askyesnocancel("Confirm Overwrite", "Existing OCR (.txt) files found.\n\nYES: Overwrite.\nNO: Use existing.\nCANCEL: Stop.", icon=tkinter.messagebox.WARNING)
            if user_choice is None: self.log_status("Process cancelled."); return
            elif not user_choice: overwrite_mode = False; self.log_status("Choice: USE EXISTING .txt files.")
            else: overwrite_mode = True; self.log_status("Choice: OVERWRITE existing .txt files.")

        self.is_processing = True
        self.status_textbox.configure(state="normal"); self.status_textbox.delete("1.0", tkinter.END); self.status_textbox.configure(state="disabled")
        self.run_button.configure(state="disabled", text="Processing..."); self.browse_button.configure(state="disabled")
        self.log_status(f"--- Starting Full Process (Overwrite: {overwrite_mode}, Sort: Mod Time, Langs: {OCR_LANGUAGES}) ---")
        self.log_status(f"--- Target Folder: {self.selected_folder} ---")

        self.processing_thread = threading.Thread(target=self.run_ocr_and_compile_thread, args=(self.selected_folder, overwrite_mode, self.status_queue), daemon=True)
        self.processing_thread.start()

    def check_status_queue(self):
        try:
            while True:
                message = self.status_queue.get_nowait()
                if message == "PROCESS_COMPLETE": self.log_status("\n=== Process Finished Successfully ==="); self.reset_gui_state()
                elif message == "PROCESS_ERROR": self.log_status("\n=== Process Finished with Errors (see log) ==="); self.reset_gui_state()
                elif message == "THREAD_STARTED": pass
                else: self.log_status(str(message))
        except queue.Empty: pass
        except Exception as e: print(f"Error processing status queue: {e}"); self.log_status(f"GUI Error: {e}"); self.reset_gui_state()
        if self.winfo_exists(): self.after(150, self.check_status_queue)

    def reset_gui_state(self):
        self.is_processing = False
        self.run_button.configure(state="normal", text="Click me to Batch OCR and Compile!")
        self.browse_button.configure(state="normal")

    def run_ocr_and_compile_thread(self, folder_path, overwrite_mode, status_q):
        def callback(message):
            try: status_q.put(message)
            except Exception as e: print(f"Queue Error: {message} - {e}")

        overall_success = True
        try:
            callback("THREAD_STARTED")
            # Step 1: OCR
            use_gpu = False
            if TORCH_AVAILABLE:
                try:
                    if torch.cuda.is_available(): use_gpu = True; callback("INFO: PyTorch CUDA found, attempting GPU.")
                    else: callback("INFO: PyTorch CUDA not available, using CPU.")
                except Exception as torch_err: callback(f"INFO: Error checking Torch CUDA ({torch_err}), using CPU.")
            else: callback("INFO: PyTorch not found, using CPU.")

            ocr_processed, ocr_skipped, ocr_errors, ocr_msg = perform_batch_ocr(
                folder_path, languages=OCR_LANGUAGES, use_gpu=use_gpu,
                overwrite_mode=overwrite_mode, status_callback=callback
            )
            if ocr_msg and not ("No image files found" in ocr_msg): overall_success = False; raise Exception(f"OCR Step Failed Critically: {ocr_msg}")
            if ocr_errors > 0: callback(f"Warning: OCR process completed with {ocr_errors} file errors.")
            if ocr_processed == 0 and ocr_skipped == 0 and ocr_errors == 0 : callback("OCR Task: No images were processed, skipped, or errored.")

            # Step 2: Compile
            output_filename = os.path.join(folder_path, DEFAULT_COMPILED_FILENAME)
            compile_count, compile_msg = compile_text_files(
                folder_path, output_filename, status_callback=callback
            )
            if compile_msg and not ("Compilation completed with errors" in compile_msg or "No .txt files found" in compile_msg): overall_success = False; raise Exception(f"Compilation Step Failed Critically: {compile_msg}")
            if compile_msg and "Compilation completed with errors" in compile_msg: callback(f"Warning: {compile_msg}"); overall_success = False
            if compile_msg and "No .txt files found" in compile_msg: callback("Info: Compilation found no .txt files to combine.")

            # Finished
            if overall_success: status_q.put("PROCESS_COMPLETE")
            else: status_q.put("PROCESS_ERROR")
        except Exception as e:
            callback(f"\n!!! THREAD ERROR: {e} !!!\n{traceback.format_exc()}"); status_q.put("PROCESS_ERROR")


# ==============================================================================
# --- Main Execution Block ---
# ==============================================================================
if __name__ == "__main__":
    try: # Pre-check Tkinter
        dummy_root = tkinter.Tk(); dummy_root.withdraw(); dummy_root.destroy()
    except tkinter.TclError as e: print(f"FATAL ERROR: Tkinter not available: {e}"); sys.exit(1)
    except Exception as e: print(f"FATAL ERROR: Tkinter init failed: {e}"); sys.exit(1)

    app = None
    try:
        print("Initializing application window...")
        app = App()
        print("Starting GUI main loop...")
        app.mainloop()
        print("GUI main loop finished.")
    except Exception as e:
        print("\n--- FATAL APPLICATION STARTUP ERROR ---"); print(f"{e}"); print("\n--- Traceback ---"); print(traceback.format_exc())
        try: root = tkinter.Tk(); root.withdraw(); tkinter.messagebox.showerror("App Startup Error", f"Failed to start:\n\n{e}\n\nSee console."); root.destroy()
        except Exception: pass
        sys.exit(1)