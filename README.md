# E-learning_Website

# GK Quiz - Smart Scholars

Welcome to the **GK Quiz - Smart Scholars** project! This is an interactive General Knowledge Quiz web application built using HTML, CSS, and JavaScript. The quiz features 10 questions, a timer, user feedback, a detailed report with correct/incorrect answers, and navigation buttons to review answers. It’s designed to be engaging, elegant, and responsive for smart learners.

## Features
- **10 Unique GK Questions**: Covering topics like geography, science, and history.
- **Timer**: 10 seconds per question to add challenge.
- **User Input**: Enter a username to personalize the experience.
- **Feedback**: Immediate feedback with ✅ for correct and ❌ for incorrect answers.
- **Report Navigation**: Use "<" and ">" buttons to review each question’s result.
- **Summary**: Displays total score, correct, and incorrect answers at the end.
- **Responsive Design**: Works on desktops, tablets, and mobile devices.
- **Stylish UI**: Features a professional color scheme and smooth animations.

## Prerequisites
- A modern web browser (e.g., Chrome, Firefox, Edge).
- Basic web server (optional, for local testing; see "Running the Project" below).
- (Optional) A static image file named `banner2.jpg` in a `static` folder for the background (can be replaced or omitted).

## Project Structure
- `gkquiz.html`: The main HTML file containing the quiz logic, styles, and JavaScript.
- `static/banner2.jpg`: (Optional) Background image file (place in a `static` folder if used).

## Running the Project

### Locally (Without a Server)
1. **Clone or Download the Project**:
   - Download the `gkquiz.html` file from the repository.
   - (Optional) If using the background image, create a `static` folder and place `banner2.jpg` inside it.

2. **Open in Browser**:
   - Double-click `gkquiz.html` to open it directly in your web browser.
   - Note: Some features (e.g., the POST request to `/gkquiz`) won’t work without a server. For full functionality, proceed to the server setup.

### With a Local Web Server
1. **Install a Web Server**:
   - Use a simple server like **Python’s HTTP server**:
     - Ensure Python is installed (download from [python.org](https://www.python.org/)).
     - Open a terminal in the project directory and run:
       ```bash
       python -m http.server 8000
