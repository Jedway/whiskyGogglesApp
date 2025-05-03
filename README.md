![App preview](baxuslogo.png)

# BAXUS WHISKEY GOGGLES BY JED

- A live, hosted, ready-to-use version of this app is available 👉🏽
<a href="https://whisky-goggles-production.up.railway.app/" target="_blank" rel="noopener noreferrer">Whisky Goggles Live app</a>

### How it works: 
WhiskyGoggles is a web-based computer vision application that identifies whisky bottles from images. Users can upload photos or use their device's camera to capture bottle images. The app uses OpenCV's ORB feature detection to match bottles against a reference database and provides detailed information about identified bottles. It's built with Python/Flask backend, JavaScript frontend, and uses TailwindCSS for styling.

---

> ℹ️ **Info**  
> Whiskey Goggles App has been updated to v1.5. New look and new features🎊
> Watch the showcase video here 👉🏽 [v1.5 Showcase Video](https://youtu.be/kKtvLdJE_JQ?si=pqHP1xZL1aFVcpye)

---

Read more here: <a href="https://gist.github.com/Jedway/4c0a8c7b0a5c4ea48a96996ed6792634" target="_blank" rel="noopener noreferrer">Whisky Goggles app full documentation</a>

### Demo and Walkthrough
- Watch the demo video of how the app works here 👉🏽 <a href="https://youtu.be/kKtvLdJE_JQ?si=pqHP1xZL1aFVcpye" target="_blank" rel="noopener noreferrer">Whiskey Goggles App Demo</a>

## Prerequisites
- Python 3.8+
- Webcam (for real-time recognition)
- macOS/Linux/Windows

## Installation

1. Clone the repository (might take a bit of time because of project size/internet speed, please be patient 🙏🏽) :
```bash
git clone https://github.com/Jedway/whiskyGogglesApp.git
```

2. Enter the project directory
```bash
cd whiskyGogglesApp
```

3. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  
```
Or if you're on Windows:
```bash
python -m venv venv
source venv\Scripts\activate
```

4. Install required packages:
```bash
pip install -r requirements.txt
```

5. Run the dev server with:
```bash
python app.py
```

It will start up a server on port `5000`

6. Copy and paste this into your browser:
```bash
http://127.0.0.1:5000
```

> [!TIP]
> The app is best experienced on mobile as a PWA (Progressive Web App).
> Use your browser to "Add To HomePage".
> Chrome and Safari are recommended

### Minor quirks and features:
- The live hosted version of the app can be installed as a PWA for a somewhat native feel
- The app is intuitive to use. You can either upload an image or take a picture using your webcam or the rear camera of your mobile device.
- Dark/Light mode toggle to set the mood
- Hamburger menu features an "Analysis History" that lists all the scan results you've gotten for your session
- When using the camera mode on the live PWA, only press the "Take Photo" button once then press "X", as it captures and immediately starts analyzing on click

### Gallery
On mac as a PWA:
| Dark Mode      | Light Mode     |
|----------------|----------------|
| ![](dark1.png) | ![](light1.png) |

On mobile as a PWA:
| Dark Mode      | Light Mode     |
|----------------|----------------|
| ![](mobiledark1.PNG) | ![](mobilelight1.PNG) |

### 👋🏽To the team at Baxus
Hi there, My name is Jed and I was very enthusiastic to work on this. I've made a roadmap of more features I intend to add and how far I'm willing to push this app so as to push the BAXUS brand and what it stands for even further. Check it out here: <a href="https://gist.github.com/Jedway/4c0a8c7b0a5c4ea48a96996ed6792634" target="_blank" rel="noopener noreferrer">Whisky Goggles app full documentation</a>



