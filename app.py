import os
import streamlit as st
from dotenv import load_dotenv
import supabase
import requests
from textblob import TextBlob
from datetime import datetime
import json
import time
import logging
import difflib
from sentence_transformers import SentenceTransformer

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase_client = supabase.create_client(supabase_url, supabase_key)

# DeepSeek API setup
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
deepseek_url = "https://api.deepseek.com/chat/completions"

# Streamlit config
st.set_page_config(
    page_title="CogniChat - Memory-Powered AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Supabase Vector Store
class SupabaseVectorStore:
    def __init__(self, client):
        self.client = client
        self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        logger.info("Initialized SupabaseVectorStore")

    def _get_embedding(self, text):
        start = time.time()
        embedding = self.embedder.encode(text).tolist()
        logger.info(f"Embedding for '{text[:50]}...' took {time.time() - start:.2f}s")
        return embedding

    def add(self, messages, user_id, metadata):
        try:
            memory_text = messages[0]["content"].strip() if messages else ""
            embedding = self._get_embedding(memory_text)
            data = {
                "user_id": user_id,
                "memory_text": memory_text,
                "embedding": embedding,
                "metadata": metadata
            }
            response = self.client.table("memories").insert(data).execute()
            logger.info(f"Added memory for user {user_id}: {memory_text} with metadata {metadata}")
            return [response.data[0]["id"]]
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
            return []

    def search(self, query, user_id, limit=5, filters=None):
        try:
            if filters and "tag" in filters and filters["tag"] == "explicit":
                response = self.client.table("memories")\
                    .select("id, memory_text, metadata, created_at")\
                    .eq("user_id", user_id)\
                    .eq("metadata->>tag", "explicit")\
                    .order("created_at", desc=True)\
                    .limit(limit)\
                    .execute()
                results = [
                    {"id": r["id"], "memory": r["memory_text"], "metadata": r["metadata"], "created_at": r["created_at"]}
                    for r in response.data
                ]
                logger.info(f"Direct search for tag 'explicit' returned {len(results)} memories: {[r['memory'] for r in results]}")
                return results
            
            # Vector search for general queries
            query_embedding = self._get_embedding(query)
            params = {
                "query_embedding": query_embedding,
                "match_threshold": 0.8,
                "match_count": limit,
                "user_id_filter": user_id,
                "tag_filter": filters.get("tag") if filters else None
            }
            response = self.client.rpc("match_memories", params).execute()
            results = [
                {"id": r["id"], "memory": r["memory_text"], "metadata": r["metadata"]}
                for r in response.data
            ]
            logger.info(f"Vector search for '{query}' with filters {filters} returned {len(results)} memories: {[r['memory'] for r in results]}")
            return results
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []

def get_memory():
    return SupabaseVectorStore(supabase_client)

def sign_up(email, password, name):
    try:
        response = supabase_client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"name": name}}
        })
        if response.user:
            st.session_state.authenticated = True
            st.session_state.user = response.user
            st.rerun()
    except Exception as e:
        st.error(f"Sign-up error: {e}")

def sign_in(email, password):
    try:
        response = supabase_client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if response.user:
            st.session_state.authenticated = True
            st.session_state.user = response.user
            st.rerun()
    except Exception as e:
        st.error(f"Login error: {e}")

def sign_out():
    supabase_client.auth.sign_out()
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.messages = []
    st.rerun()

def normalize_command(message):
    commands = {
        "remember this:": ["remeber this:", "rember this:", "remember this", "remembr this:"],
        "what i asked you to remember": ["what i ask you to remeber", "wht i asked to remember", "what i asked to rember"],
        "did i ask you to remember": ["did i ask you to remeber", "did i ask to rember"],
        "remind me": ["rimind me", "remind meee"]
    }
    message_lower = message.lower().strip()
    for correct, variants in commands.items():
        for variant in variants:
            if message_lower.startswith(variant):
                content = message[len(variant):].strip().lstrip(": ")
                return f"{correct}{content}"
    return message

def chat_with_memories(message, user_id, memory, response_length):
    start_time = time.time()
    normalized_message = normalize_command(message)
    
    if normalized_message.startswith("/joke"):
        return "Why don’t skeletons fight each other? Because they don’t have the guts!"
    elif normalized_message.startswith("/summary"):
        summary = "\n".join([f"{m['role']}: {m['content'][:50]}..." for m in st.session_state.messages[-5:]])
        return f"Chat summary:\n{summary}"
    elif "time" in normalized_message.lower():
        return f"The current time is {datetime.now().strftime('%H:%M:%S %Y-%m-%d')}."
    elif normalized_message.startswith("remember this:"):
        fact = normalized_message[len("remember this:"):].strip()
        metadata = {"priority": 2.0, "timestamp": time.time(), "tag": "explicit"}
        memory.add([{"role": "user", "content": fact}], user_id, metadata)
        return f"Got it! I’ll remember: '{fact}'."
    elif any(phrase in normalized_message.lower() for phrase in ["what i asked you to remember", "did i ask you to remember"]):
        memories = memory.search(normalized_message, user_id, filters={"tag": "explicit", "user_id": user_id})
        if memories:
            memory_str = "\n".join([f"- {m['memory']} (saved {m['created_at'][:19]})" for m in memories])
            return f"Here’s what I remember you asked me to store:\n{memory_str}"
        return "You haven’t asked me to remember anything yet. Use 'remember this: [something]' to save info!"
    elif normalized_message.startswith("remind me"):
        reminder = normalized_message[len("remind me"):].strip()
        metadata = {"priority": 1.5, "timestamp": time.time(), "tag": "reminder"}
        memory.add([{"role": "user", "content": reminder}], user_id, metadata)
        return f"I’ve noted your reminder: '{reminder}'. No timers yet, but it’s stored!"

    search_start = time.time()
    memories = memory.search(normalized_message, user_id)
    search_time = time.time() - search_start
    st.info(f"Memory search took {search_time:.2f} seconds")

    memory_str = "\n".join([f"- {m['memory']} (Priority: {m.get('metadata', {}).get('priority', 1.0):.2f})" 
                           for m in memories]) if memories else "No relevant memories."
    
    blob = TextBlob(normalized_message)
    sentiment = "cheerful" if blob.sentiment.polarity > 0 else "empathetic" if blob.sentiment.polarity < 0 else "neutral"
    system_prompt = f"You are CogniChat, a smart AI by HeWhoCodes. Respond in a {sentiment} tone. Date: {datetime.now().strftime('%Y-%m-%d')}\nMemories:\n{memory_str}"
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": normalized_message}],
        "temperature": 0.7
    }
    
    with st.spinner("Thinking..."):
        api_start = time.time()
        response = requests.post(deepseek_url, headers={"Authorization": f"Bearer {deepseek_api_key}", "Content-Type": "application/json"}, json=payload)
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"]
        api_time = time.time() - api_start
        st.info(f"DeepSeek API call took {api_time:.2f} seconds")

        words = reply.split()
        if response_length == "short":
            reply = " ".join(words[:20])
        elif response_length == "medium":
            reply = " ".join(words[:50])
    
    messages = [{"role": "user", "content": normalized_message}, {"role": "assistant", "content": reply}]
    metadata = {"priority": 1.0 + abs(blob.sentiment.polarity), "timestamp": time.time()}
    memory.add(messages, user_id, metadata)

    total_time = time.time() - start_time
    st.info(f"Total processing took {total_time:.2f} seconds")
    logger.info(f"Responded to '{normalized_message}' with: {reply}")

    return reply

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None

# Sidebar
with st.sidebar:
    st.title("🧠 CogniChat")
    st.markdown("Built by HeWhoCodes")
    
    if not st.session_state.authenticated:
        tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
        with tab1:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Sign In"):
                sign_in(email, password)
        with tab2:
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            name = st.text_input("Name", key="signup_name")
            if st.button("Sign Up"):
                sign_up(email, password, name)
    else:
        st.write(f"Welcome, {st.session_state.user.user_metadata.get('name', 'User')}")
        if st.button("Sign Out"):
            sign_out()
        
        st.subheader("Settings")
        memory = get_memory()
        response_length = st.select_slider("Response Length", options=["short", "medium", "long"], value="medium")

# Main interface
if st.session_state.authenticated and st.session_state.user:
    user_id = st.session_state.user.id
    st.title("CogniChat - Your Memory-Powered Companion")
    st.write("Chat with an AI that remembers you. Built by HeWhoCodes.")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    if user_input := st.chat_input("What’s on your mind?"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        response = chat_with_memories(user_id=user_id, message=user_input, memory=memory, response_length=response_length)
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)
else:
    st.title("Welcome to CogniChat")
    st.write("Sign in or sign up to chat with an AI that remembers you.")