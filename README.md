AI Voice Dashboard (main.html)(First try to do using app.py but its not working)
A web-based, voice-controlled dashboard that integrates an AI assistant, real-time weather updates, web search, and task management. Built with modern web technologies and deployed on Vercel, this project offers a seamless, hands-free user experience for productivity and accessibility.
Table of Contents

Features
Tech Stack
Installation
Usage
Deployment on Vercel
Security Considerations
Contributing
License

Features

Voice Command System: Control the dashboard with voice inputs (e.g., "Ask AI about the weather," "Search for latest news").
AI Assistant: Powered by the Groq API for answering queries, summarizing content, and parsing intents.
Weather Widget: Displays real-time weather data for any location using the Open-Meteo API.
Web Search: Fetches search results via the DuckDuckGo Instant Answer API.
Task Management: Add, complete, or delete tasks with voice or manual input.
Responsive UI: Expandable widgets, modals, and a clean, grid-based layout.
Accessibility: Designed for hands-free operation, supporting users with diverse needs.

Tech Stack

Frontend:
HTML5: Structure of the dashboard.
CSS3: Styling with responsive design (grid, flexbox).
JavaScript (ES6): Core logic, event handling, and API integration.


APIs:
Web Speech API: Browser-based speech recognition.
Groq API: AI query processing and intent recognition.
Open-Meteo API: Weather forecasts and geocoding.
DuckDuckGo Instant Answer API: Web search results.


Deployment:
Vercel: Static site hosting and serverless functions.
Git/GitHub: Version control and CI/CD.


Tools:
Vercel CLI: Deployment automation.
Browser DevTools: Debugging and testing.



Installation
To run the project locally, follow these steps:


Project Structure:
ai-voice-dashboard/
# Serverless function for Groq API
├── main.html            # Main HTML file with embedded CSS and JS           # Vercel configuration
├── .gitignore            # Git ignore file
└── README.md             # This file


Install Dependencies (optional):

No Node.js dependencies are required for the static site.
If using Vercel CLI, install it globally:npm install -g vercel




Set Up Environment Variables:

Create a .env file in the root directory (not committed to Git):GROQ_API_KEY=your_groq_api_key_here


Replace your_groq_api_key_here with your actual Groq API key.


Run Locally:

Use a local server to serve index.html (e.g., with Python or VS Code Live Server):python -m http.server 8000


Open http://localhost:8000 in a browser (Chrome recommended for Web Speech API support).



Usage

Access the Dashboard:

Open the deployed URL (e.g., https://ai-voice-dashboard.vercel.app) or local server (http://localhost:8000).
The dashboard loads with four widgets: AI Assistant, Weather, Web Search, and Tasks.


Voice Commands:

Click the microphone icon to start listening.
Try commands like:
"Ask AI what is artificial intelligence"
"Search for Python tutorials"
"Show weather in London"
"Add task finish project"
"Expand tasks widget"
"Show commands" (displays help modal)




Manual Interaction:

Use the search bar to query the web.
Add or manage tasks via the Tasks widget.
Click "Show Commands" in the header to view available voice commands.


Browser Compatibility:

Best supported in Chrome due to Web Speech API.
Test voice recognition in a quiet environment for optimal results.



Deployment on Vercel
To deploy the AI Voice Dashboard on Vercel, follow these steps:

Push to GitHub:

Initialize a Git repository and push to GitHub:git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/OSAMAGHAFFARTKOJL/GDC_HACKATHON.git
git branch -M main
git push -u origin main




Set Up Vercel:

Sign up at vercel.com.
Install Vercel CLI (optional):npm install -g vercel
vercel login




Deploy via Vercel Dashboard:

Go to Vercel Dashboard > New Project > Import your GitHub repository.
Configure:
Framework Preset: Other (static site).
Root Directory: ./.
Build Command: None.
Output Directory: None (defaults to root).


Add environment variable:
Name: GROQ_API_KEY
Value: Your Groq API key


Click Deploy to get a live URL.


Deploy via Vercel CLI (alternative):

Run:vercel


Accept defaults or confirm vercel.json settings.
Deploy to production:vercel --prod




Verify Deployment:

Test the deployed URL to ensure all features (voice, AI, weather, search, tasks) work.
Check Vercel’s Logs tab for serverless function errors.


Vercel Configuration:

The vercel.json file configures the static site and serverless function:{
  "version": 2,
  "builds": [
    { "src": "index.html", "use": "@vercel/static" },
    { "src": "api/groq.js", "use": "@vercel/node" }
  ],
  "routes": [
    { "src": "/api/groq", "dest": "/api/groq.js" },
    { "src": "/(.*)", "dest": "/index.html" }
  ]
}





Security Considerations

API Key Security:
The GROQ_API_KEY is stored in Vercel’s environment variables and accessed by the api/groq.js serverless function to prevent client-side exposure.
Never hardcode API keys in index.html for production.


CORS:
DuckDuckGo and Open-Meteo APIs are CORS-enabled, ensuring browser compatibility.
If using other APIs, configure CORS headers in vercel.json or proxy via serverless functions.


Data Privacy:
Voice inputs are processed locally via Web Speech API and not stored.
Ensure compliance with privacy regulations (e.g., GDPR) if adding user data storage.



Contributing
We welcome contributions to enhance the AI Voice Dashboard! To contribute:

Fork the Repository:

Fork the project on GitHub.


Create a Branch:
git checkout -b feature/your-feature-name


Make Changes:

Add new features, fix bugs, or improve documentation.
Follow the existing code style (e.g., ES6 for JavaScript, consistent CSS).


Test Locally:

Ensure all features work as expected.
Test voice commands in Chrome.


Submit a Pull Request:

Push your branch to GitHub and create a PR with a clear description of changes.


Issues:

Report bugs or suggest features via GitHub Issues.



License
This project is licensed under the MIT License. See the LICENSE file for details.

Contact: For questions or support, open an issue on GitHub or contact [your-email@example.com].
Live Demo:[ https://ai-voice-dashboard.vercel.app](https://gdc-hackathon-3gs3gdmqx-osamaghaffars-projects.vercel.app/) 
