# CogniChat - Memory-Powered AI Chatbot

CogniChat is an intelligent chatbot that remembers user inputs across sessions, built with Streamlit, Supabase, and DeepSeek API. It supports commands like "remember this:" to store explicit memories and "what i asked you to remember?" to retrieve them, with a clean UI and persistent storage.

## Features
- Memory Persistence: Stores user memories in Supabase with tags (e.g., "explicit").
- Command-Based Interaction: Supports commands like /joke, remember this:, and what i asked you to remember?.
- Sentiment-Aware Responses: Adjusts tone (cheerful, empathetic, neutral) based on input.
- Customizable Response Length: Short, medium, or long replies via a sidebar slider.

## Tech Stack
- Frontend: Streamlit
- Backend: Python, Supabase (PostgreSQL with vector extension)
- AI: DeepSeek API
- Embedding: SentenceTransformers (all-MiniLM-L6-v2)

## Prerequisites
- Python 3.9+
- Git
- Supabase account and project
- DeepSeek API key

## Setup
1. Clone the Repository:
   git clone https://github.com/navneetr7/cognichat.git
   cd cognichat

2. Install Dependencies:
   Install required Python packages:
   pip install streamlit python-dotenv supabase requests textblob sentence-transformers torch

3. Configure Environment Variables:
   Create a .env file in the project root:
   echo SUPABASE_URL=your-supabase-url > .env
   echo SUPABASE_KEY=your-supabase-key >> .env
   echo DEEPSEEK_API_KEY=your-deepseek-api-key >> .env
   Replace your-supabase-url, your-supabase-key, and your-deepseek-api-key with your credentials.
   Note: .env is ignored by .gitignore for security.

4. Set Up Supabase:
   Create a Supabase project at supabase.com.
   Enable the pgvector extension in your database:
   Go to SQL Editor and run:
   CREATE EXTENSION IF NOT EXISTS vector;
   Create the memories table:
   CREATE TABLE memories (
     id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
     user_id UUID REFERENCES auth.users(id),
     memory_text TEXT NOT NULL,
     embedding VECTOR(384),
     metadata JSONB,
     created_at TIMESTAMP DEFAULT NOW()
   );
   Create the match_memories function for vector search:
   CREATE OR REPLACE FUNCTION match_memories(
     query_embedding VECTOR(384),
     match_threshold FLOAT,
     match_count INT,
     user_id_filter UUID,
     tag_filter TEXT DEFAULT NULL
   )
   RETURNS TABLE (id UUID, memory_text TEXT, metadata JSONB) AS $$
   BEGIN
     RETURN QUERY
     SELECT m.id, m.memory_text, m.metadata
     FROM memories m
     WHERE m.user_id = user_id_filter
     AND (tag_filter IS NULL OR m.metadata->>'tag' = tag_filter)
     AND m.embedding <=> query_embedding < match_threshold
     ORDER BY m.embedding <=> query_embedding
     LIMIT match_count;
   END;
   $$ LANGUAGE plpgsql;

## Running the App
1. Start the App:
   python run.py
   Or directly with Streamlit:
   streamlit run app.py

2. Access the App:
   Open your browser to http://localhost:8501.
   Sign up or log in to start chatting.

## Usage
- Store a Memory: remember this: I love coding
- Retrieve Memories: what i asked you to remember?
- Get a Joke: /joke
- Check Time: what’s the time?

## Contributing
Feel free to fork this repo, submit issues, or send pull requests. Ideas for improvement:
- Async embedding for faster memory storage.
- Memory deletion/editing commands.
- UI theme customization.

## License
MIT License - feel free to use and modify this code!

## Author
Built by navneetr7 (https://github.com/navneetr7).