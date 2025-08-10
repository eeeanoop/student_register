# Classroom Sentry 📸

Welcome to Classroom Sentry! This is a fun project that uses your computer's webcam to automatically take attendance or act as a security guard for your room. It uses face recognition to see who is present and can even alert you if it sees someone it doesn't recognize.

## Getting Started: Let's Get This Running!

Follow these steps to get the project working on your computer. Don't worry, we'll go through it one step at a time.

### Step 1: What You Need (Prerequisites)

Before we begin, make sure you have these two things installed:

1.  **Python 3**: This is the programming language the project is written in. You can download it from [python.org](https://www.python.org/downloads/).
2.  **Git**: This is a tool to copy the project files to your computer. You can get it from [git-scm.com](https://git-scm.com/downloads).

### Step 2: Get the Code

First, you need to download the project files. Open your terminal (like Command Prompt, PowerShell, or Terminal on Mac/Linux) and run this command:

```bash
git clone https://github.com/your-username/classroom_sentry.git
cd classroom_sentry
```
*(Replace `your-username/classroom_sentry.git` with the actual URL of your project's repository if you have one!)*

### Step 3: Create a Virtual Workspace

It's a good habit to create a "virtual environment" for every Python project. This keeps all the project's tools separate from your main computer's tools.

```bash
# Create the virtual environment (you only do this once)
python3 -m venv venv

# Activate it (you need to do this every time you work on the project)
```

**On Windows:**
```bash
venv\Scripts\activate
```

**On macOS or Linux:**
```bash
source venv/bin/activate
```

You'll know it's working if you see `(venv)` at the beginning of your terminal prompt.

### Step 4: Install Build Tools (macOS, Windows, & Linux)

The `face-recognition` library depends on another library called `dlib`, which is written in C++. To install it, `pip` needs to compile this C++ code from scratch. This requires a C++ compiler and development tools on your system.

Please follow the instructions for your operating system.

**On macOS:**

1.  **Install Xcode Command Line Tools:** This provides the C++ compiler. Open your terminal and run:
```bash
xcode-select --install
```
A dialog box will appear. Click "Install" to proceed.

**On Linux (Ubuntu/Debian):**
You will need the `build-essential` and `cmake` packages.
```bash
sudo apt-get update
sudo apt-get install build-essential cmake
```

### Step 5: Install the Special Tool - CMake (Windows)

This is the most important step! One of our key Python libraries, `face-recognition`, needs a special tool called **CMake** to install correctly. Think of CMake as a master builder that knows how to construct the complex parts of the library from its C++ source code.

Without CMake, the installation will fail with an error.

**On macOS (using Homebrew):**
If you don't have Homebrew, you can get it at brew.sh.
```bash
sudo apt-get update
sudo apt-get install cmake
```

**On Windows:**
1.  Go to the official CMake website: cmake.org/download/.
2.  Download the latest installer (the file ending in `.msi`).
3.  Run the installer. **This is important:** When it asks, make sure you check the box that says **"Add CMake to the system PATH for all users"** (or for the current user). This lets your terminal find the `cmake` command.

To check if it worked, open a **new** terminal and type `cmake --version`. If you see a version number, you're good to go!

### Step 6: Install the Python Libraries

Now that the build tools are ready, we can install all the Python libraries the project needs with one command.

```bash
pip install -r requirements.txt
```

### Step 6: Set Up Your Email

The app can send you email reports. To do this securely, we'll use an "App Password" for Gmail and an environment variable (a secret variable that lives outside the code).

1.  **Create a Gmail App Password**: Follow the guide here: support.google.com/accounts/answer/185833
2.  **Set the Environment Variable**: Before you run the app, run one of the following commands in your terminal.

**On Windows:**
```bash
set GMAIL_APP_PASSWORD="your_16_digit_app_password"
```
**On macOS or Linux:**
```bash
export GMAIL_APP_PASSWORD="your_16_digit_app_password"
```

### Step 7: Run the App!

You're all set! To run the application, just run:

```bash
python app.py
```