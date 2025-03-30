# CogniChat - Memory-Powered AI Chatbot

CogniChat is an intelligent chatbot built with Streamlit, Supabase, and DeepSeek API. It remembers your explicit instructions across sessions, making it a personalized conversational companion. Created by [navneetr7](https://github.com/navneetr7).

## Features

- **Persistent Memory**: Save and recall explicit memories using commands like `remember this:` and `what i asked you to remember?`.
- **Sentiment-Aware Responses**: Adjusts tone (cheerful, empathetic, neutral) based on your input.
- **Command Support**: Includes `/joke`, `/summary`, `time`, and `remind me`.
- **Web Interface**: Powered by Streamlit for an interactive UI.
- **Vector Embeddings**: Uses SentenceTransformers for semantic memory search.

## Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Backend**: Python, [Supabase](https://supabase.com/) (PostgreSQL with vector support)
- **AI**: [DeepSeek API](https://deepseek.com/)
- **Embeddings**: [SentenceTransformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`)

## Prerequisites

- Python 3.8+
- Git
- Supabase account and project
- DeepSeek API key

## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/navneetr7/cognichat.git
   cd cognichat
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   If `requirements.txt` isn’t present, install manually:
   ```bash
   pip install streamlit python-dotenv supabase requests textblob sentence-transformers
   ```

3. **Configure Environment Variables**:
   Create a `.env` file in the root directory:
   ```plaintext
   SUPABASE_URL=your-supabase-url
   SUPABASE_KEY=your-supabase-key
   DEEPSEEK_API_KEY=your-deepseek-api-key
   ```
   Get these from your Supabase project and DeepSeek account.

4. **Run the App**:
   ```bash
   python run.py
   ```
   Open your browser to [http://localhost:8501](http://localhost:8501).

## Usage

### Sign Up / Sign In:
Use the sidebar to create an account or log in.

### Chat Commands:
- `remember this: I love coding` - Stores a memory.
- `what i asked you to remember?` - Lists stored memories.
- `remind me: Call mom` - Saves a reminder (no timers yet).
- `/joke` - Hear a joke!
- `time` - Get the current time.

#### Example:
```text
User: remember this: I have diabetes
CogniChat: Got it! I’ll remember: 'I have diabetes'.
User: what i asked you to remember?
CogniChat: Here’s what I remember you asked me to store:
- I have diabetes (saved 2025-03-30T18:14:08)
```

## Project Structure
```text
cognichat/
├── app.py          # Main Streamlit app
├── run.py          # Entry point script
├── .gitignore      # Excludes .env, __pycache__, etc.
└── README.md       # This file
```

## Contributing

1. Fork the repo.
2. Create a branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit changes:
   ```bash
   git commit -m "Add feature"
   ```
4. Push to your fork:
   ```bash
   git push origin feature-name
   ```
5. Open a Pull Request.

## Next Steps

- Async embedding for faster memory storage.
- Memory deletion/editing commands.
- UI theme switcher (light/dark mode).

## License
MIT License - feel free to use, modify, and distribute!

Happy coding with CogniChat! 🚀
