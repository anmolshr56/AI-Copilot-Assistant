# 🚀 BYOC: Build Your Own Copilot - From RAG to Agents

Welcome to the **BYOC (Build Your Own Copilot)** workshop! Today, you aren't just building a chatbot; you're building a personalized **AI Productivity Team**.

We will start with a local LLM "Brain," give it "Eyes" to read your PDFs, "Hands" to search the web, and finally, a "Team" of agents to work for you.

---

## 🛠️ Phase 0: The Skeleton & Local Brain

**Goal:** Get your local AI talking to your Python backend.

### 1. Setup your Environment
Open your terminal in the project root:
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install dependencies
python -m pip install langchain langchain-community langchain-classic pypdf langchain-ollama langchain-chroma langchain-openai fastapi uvicorn python-multipart python-dotenv duckduckgo-search crewai
```

### 2. Configure the Local LLM
Open `backend/llm_config.py` and paste this:
```python
import os
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI

load_dotenv()

def get_llm(use_cloud=False):
    if use_cloud:
        # Scale to Gemma 2 9B via OpenRouter for complex tasks
        return ChatOpenAI(
            model_name="google/gemma-2-9b-it",
            openai_api_key=os.getenv("OPENROUTER_API_KEY"),
            openai_api_base="https://openrouter.ai/api/v1",
        )
    # Default: Local Ollama
    return OllamaLLM(model="gemma2:2b")
```

### 3. Create the Initial API
Open `backend/main.py` and paste this:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.llm_config import get_llm

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/test-chat")
async def test_chat(q: str = "Hello"):
    llm = get_llm(use_cloud=False)
    response = llm.invoke(q)
    return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 4. Run Ollama & Verify
1. Open a new terminal and run: `ollama run gemma2:2b`
2. Run your backend: `python -m backend.main`
3. Visit `http://localhost:8000/test-chat?q=Who are you?` in your browser.

---

## 🧠 Phase 1: The Reader (RAG Engine)

**Goal:** Give your Copilot "Eyes" to read your PDFs.

### 1. Build the RAG Engine
Open `backend/engine.py` and paste this:
```python
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_classic.chains import RetrievalQA
from backend.llm_config import get_llm

embeddings = OllamaEmbeddings(model="gemma2:2b")
DB_DIR = "data/chroma_db"

def ingest_pdf(file_path):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)
    return Chroma.from_documents(documents=texts, embedding=embeddings, persist_directory=DB_DIR)

def get_chat_response(query, use_cloud=False):
    vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    llm = get_llm(use_cloud=use_cloud)
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())
    return qa_chain.invoke(query)["result"]
```

### 2. Update the API
Replace everything in `backend/main.py` with this:
```python
import os, shutil
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from backend.engine import ingest_pdf, get_chat_response

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    ingest_pdf(file_path)
    return {"message": f"Successfully indexed {file.filename}"}

@app.post("/chat")
async def chat(message: str = Form(...), use_cloud: bool = Form(False)):
    return {"response": get_chat_response(message, use_cloud)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 🛠️ Phase 2: The Agent (Autonomous Tools)

**Goal:** Give your AI "Hands" to search the web when the PDF doesn't have the answer.

### 1. Create the Agent
Open `backend/agent.py` and paste this:
```python
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import initialize_agent, AgentType
from backend.llm_config import get_llm

search_tool = DuckDuckGoSearchRun()

def get_agent_response(query, use_cloud=True):
    # Agents work best with Cloud Models (Gemma 9B)
    llm = get_llm(use_cloud=use_cloud)
    agent = initialize_agent(
        tools=[search_tool],
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
    return agent.run(query)
```

### 2. Add Agent to API
In `backend/main.py`, add this endpoint:
```python
from backend.agent import get_agent_response

@app.post("/agent-chat")
async def agent_chat(message: str = Form(...), use_cloud: bool = Form(True)):
    return {"response": get_agent_response(message, use_cloud)}
```

---

## 👥 Phase 3: The Crew (Multi-Agent Team)

**Goal:** Orchestrate a "Boardroom" of experts to handle complex tasks.

### 1. Build the Crew
Open `backend/crew.py` and paste this:
```python
from crewai import Agent, Task, Crew, Process
from langchain_community.tools import DuckDuckGoSearchRun
from backend.llm_config import get_llm

search_tool = DuckDuckGoSearchRun()

def run_crew_task(topic):
    # 1. Define Agents
    researcher = Agent(
        role='Researcher',
        goal=f'Find 3 groundbreaking facts about {topic}',
        backstory="You are an elite researcher who finds the truth no matter what.",
        tools=[search_tool],
        llm=get_llm(use_cloud=True)
    )

    writer = Agent(
        role='Content Creator',
        goal=f'Write a viral Gen-Z style LinkedIn post about {topic}',
        backstory="You turn boring data into viral content using emojis and slang.",
        llm=get_llm(use_cloud=True)
    )

    # 2. Define Tasks
    task1 = Task(description=f"Research {topic}", agent=researcher)
    task2 = Task(description=f"Write post about {topic}", agent=writer)

    # 3. Assemble the Crew
    crew = Crew(
        agents=[researcher, writer],
        tasks=[task1, task2],
        verbose=True,
        process=Process.sequential
    )

    return crew.kickoff()
```

### 2. Add Crew to API
In `backend/main.py`, add this endpoint:
```python
from backend.crew import run_crew_task

@app.post("/run-crew")
async def run_crew(topic: str = Form(...)):
    result = run_crew_task(topic)
    return {"response": str(result)}
```

---

## 🎨 Phase 4: Vibe-Coding (Your Turn!)

Your Copilot is functional. Now, make it unique:

1.  **Custom Personas:** Go to `backend/crew.py` and change the `backstory` and `goal` of your agents. Make them talk like pirates or detectives.
2.  **UI Polish:** Use Tailwind CSS in `App.jsx` to turn the "Crude UI" into a professional dashboard.
3.  **New Tools:** Try adding a tool that can write files or tell the current time!

---

## 🚀 Bonus: Deployment (Render + Firebase)
(Follow instructions in `tutorial_guide.md` for final hosting).
