# 🖼️📄 Batch OCR & Text Compiler GUI 🚀

Transform folders full of images into organized text with a single click! This desktop application features a modern graphical interface to batch OCR (Optical Character Recognition) all images within a folder and then compile all extracted text into a single, chronologically sorted file. 🇪🇸🇬🇧 Supports OCR in Spanish and English.

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Made with CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-brightgreen.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![Powered by EasyOCR](https://img.shields.io/badge/OCR-EasyOCR-orange.svg)](https://github.com/JaidedAI/EasyOCR)

---

## ✨ Key Features

*   **Modern GUI:** 💅 Simple, minimalist, and user-friendly interface built with `CustomTkinter`.
*   **Batch OCR:** 🗂️ Processes all images (`.png`, `.jpg`, `.jpeg`, `.bmp`, `.tiff`) within the selected folder.
*   **Multilingual Support:** 🇪🇸🇬🇧 Text recognition optimized for **Spanish** and **English** using `EasyOCR`.
*   **Chronological Order:** 🕰️ Images are processed and text is compiled based on the image file's **modification date and time** (oldest first).
*   **Unique Output Filenames:** 🛡️ Prevents overwriting of `.txt` files when images share the same base name but have different extensions (e.g., `photo.png` and `photo.jpg`), by saving as `photo.png.txt` and `photo.jpg.txt`.
*   **Text Compilation:** 📝 Combines all extracted text from individual unique `.txt` files into a single output file.
*   **Clear Separators:** 📑 The compiled file includes separators indicating the unique source `.txt` filename (e.g., `imagename.ext.txt`) for each text snippet.
*   **Overwrite Option:** ❓ Prompts you whether to overwrite existing `.txt` files or use their content if OCR has already been performed.
*   **Background Processing:** ⚙️ OCR and compilation run in a separate thread to keep the UI responsive.
*   **Detailed Status Logging:** 📋 Displays progress and any errors in a textbox within the GUI.
*   **GPU Support:** ⚡ Attempts to use GPU for faster OCR if available and configured (via PyTorch and CUDA).

---

## 🛠️ Use Cases

*   **Document Digitization:** 📄 Convert scans or photos of documents into editable text.
*   **Note Archiving:** ✍️ Extract text from screenshots of presentations or handwritten notes (quality may vary).
*   **Data Collection:** 📊 Gather textual information from large sets of images.
*   **Accessibility:** 👁️‍🗨️ Create text versions of visual content for screen readers.
*   **Research Organization:** 📚 Quickly group text from multiple visual sources into a single document for review.

---

## ✅ Pros

*   **Easy to Use:** 👌 The graphical interface simplifies the process; no command line needed for basic use.
*   **Time-Saving:** ⏱️ Automates the tedious process of individually OCRing images.
*   **Organized:** 🗄️ Chronological ordering and unique filenames/separators help maintain text traceability.
*   **Flexible:** 🤸 The option to overwrite or use existing files is useful for resuming or updating.
*   **Potentially Portable:** 💻 As a Python script, with the right dependencies, it could run on various operating systems.

## ⚠️ Cons

*   **Dependencies:** 🧱 Requires installation of several Python libraries (`CustomTkinter`, `EasyOCR`, `OpenCV`, `PyTorch`, etc.).
*   **OCR Quality:** 🖼️ OCR accuracy heavily depends on the quality of the input images (resolution, lighting, font clarity).
*   **Initial Model Download:** ⏳ The first time it's used (or with a new language like Spanish), `EasyOCR` will download language models, which can take time.
*   **Resource Usage:** 💻 OCR, especially in batch, can be CPU/GPU and memory intensive.
*   **Error Handling:** 🐞 While errors are handled, very complex scenarios or heavily corrupted files might still cause issues.

---

## 🚀 Getting Started

1.  **Clone the Repository (or download the `.py` file):**
    ```bash
    git clone https://[YOUR-REPO-URL-HERE].git
    cd [YOUR-REPO-DIRECTORY-NAME]
    ```
    (Replace the URL and directory name accordingly)

2.  **Install Dependencies:**
    Ensure you have Python 3.7+ installed. Then, install the required libraries using pip:
    ```bash
    pip install customtkinter easyocr opencv-python-headless numpy torch torchvision torchaudio
    ```
    *Note: `torch`, `torchvision`, `torchaudio` are required by `EasyOCR`. Check the [EasyOCR documentation](https://github.com/JaidedAI/EasyOCR) for specific PyTorch version compatibility if you encounter issues, especially with GPU usage.*

3.  **Run the Application:**
    Navigate to the directory containing the script in your terminal and run:
    ```bash
    python ocr_compiler_gui_singlefile_modtime_sort_es_unique_txt.py
    ```
    *(Make sure to use the correct filename if you saved it differently).*

4.  **Use the GUI:**
    *   Click the `Browse...` button to select the folder containing your images. The selected path will appear next to the button.
    *   Click the large `Click me to Batch OCR and Compile!` button.
    *   If existing unique `.txt` files (from previous runs, e.g., `imagename.ext.txt`) are found, you'll be prompted whether to **Overwrite** them (Yes), **Use Existing** ones where available (No), or **Cancel** the process.
    *   Watch the progress and any messages in the status text box at the bottom.
    *   Once completed, you'll find:
        *   Individual unique `.txt` files for each processed image (e.g., `photo.png.txt`, `scan.jpg.txt`) inside your selected folder.
        *   A single compiled file named `_compiled_ocr_output_by_time.txt` (or similar) inside the same folder, containing all the text ordered chronologically by image modification time.

---

## 📝 License

This project is licensed under the **GNU General Public License v3.0**.

A copy of the license should be included in the repository (e.g., in a file named `LICENSE`). You can view the full license text here:
[https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html)

---

## 🙏 Acknowledgements

*   [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for the amazing modern GUI library.
*   [EasyOCR](https://github.com/JaidedAI/EasyOCR) for the powerful and accessible OCR library.

---

Feel free to fork, contribute, or open issues! ⭐
