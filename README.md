Okay, here's the GitHub-style description in English:

🖼️📄 Batch OCR & Text Compiler GUI 🚀

Transform folders full of images into organized text with a single click! This desktop application with a modern graphical interface allows you to batch OCR (Optical Character Recognition) all images within a folder and then compile all extracted text into a single, chronologically sorted file. 🇪🇸🇬🇧 Supports OCR in Spanish and English.

![alt text](https://img.shields.io/badge/python-3.7+-blue.svg)


![alt text](https://img.shields.io/badge/License-MIT-yellow.svg)


![alt text](https://img.shields.io/badge/GUI-CustomTkinter-brightgreen.svg)


![alt text](https://img.shields.io/badge/OCR-EasyOCR-orange.svg)

✨ Key Features

Modern GUI: 💅 Simple, minimalist, and user-friendly interface built with CustomTkinter.

Batch OCR: 🗂️ Processes all images (.png, .jpg, .jpeg, .bmp, .tiff) within the selected folder.

Multilingual Support: 🇪🇸🇬🇧 Text recognition optimized for Spanish and English using EasyOCR.

Chronological Order: 🕰️ Images are processed and text is compiled based on the image file's modification date and time (oldest first).

Unique Output Filenames: 🛡️ Prevents overwriting of .txt files when images share the same base name but have different extensions (e.g., photo.png and photo.jpg), by saving as photo.png.txt and photo.jpg.txt.

Text Compilation: 📝 Combines all extracted text from individual .txt files into a single output file.

Clear Separators: 📑 The compiled file includes separators indicating the source .txt filename for each text snippet.

Overwrite Option: ❓ Prompts you whether to overwrite existing .txt files or use their content if OCR has already been performed.

Background Processing: ⚙️ OCR and compilation run in a separate thread to keep the UI responsive.

Detailed Status Logging: 📋 Displays progress and any errors in a textbox within the GUI.

GPU Support: ⚡ Attempts to use GPU for faster OCR if available and configured (via PyTorch and CUDA).

🛠️ Use Cases

Document Digitization: 📄 Convert scans or photos of documents into editable text.

Note Archiving: ✍️ Extract text from screenshots of presentations or handwritten notes (quality may vary).

Data Collection: 📊 Gather textual information from large sets of images.

Accessibility: 👁️‍🗨️ Create text versions of visual content for screen readers.

Research Organization: 📚 Quickly group text from multiple visual sources into a single document for review.

✅ Pros

Easy to Use: 👌 The graphical interface simplifies the process; no command line needed for basic use.

Time-Saving: ⏱️ Automates the tedious process of individually OCRing images.

Organized: 🗄️ Chronological ordering and separators help maintain text traceability.

Flexible: 🤸 The option to overwrite or use existing files is useful for resuming or updating.

Potentially Portable: 💻 As a Python script, with the right dependencies, it could run on various operating systems.

⚠️ Cons

Dependencies: 🧱 Requires installation of several Python libraries (CustomTkinter, EasyOCR, OpenCV, PyTorch, etc.).

OCR Quality: 🖼️ OCR accuracy heavily depends on the quality of the input images (resolution, lighting, font clarity).

Initial Model Download: ⏳ The first time it's used (or with a new language), EasyOCR will download language models, which can take time.

Resource Usage: 💻 OCR, especially in batch, can be CPU/GPU and memory intensive.

Error Handling: 🐞 While errors are handled, very complex scenarios or heavily corrupted files might still cause issues.

🚀 Getting Started

Clone the Repository (or download the .py file):

git clone (https://github.com/m4iccc/Python-OCR-Batch-script).git
cd Python-OCR-Batch-script

Install Dependencies:
Ensure you have Python 3.7+ installed. Then, install the required libraries:

pip install customtkinter easyocr opencv-python-headless numpy torch torchvision torchaudio

(Note: torch, torchvision, torchaudio are for EasyOCR. Check the EasyOCR documentation for specific PyTorch versions if you encounter issues, especially with GPU usage.)

Run the Application:

python Python OCR Batch script.py
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

Use the GUI:

Click "Browse..." to select the folder containing your images.

Click "Click me to Batch OCR and Compile!".

If existing .txt files (from previous runs) are found, you'll be asked whether to overwrite them or use them.

Watch the progress in the status text box.

Once completed, you'll find individual .txt files per image (e.g., imagename.ext.txt) and a compiled file (e.g., _compiled_ocr_output_by_time.txt) inside your selected folder.

📝 License

This project is licensed under the MIT License - see the LICENSE file for details (if you create one).

🙏 Acknowledgements

CustomTkinter for the amazing modern GUI library.

EasyOCR for the powerful and accessible OCR library.

Feel free to fork, contribute, or open issues! ⭐
