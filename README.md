# RAG_PreLogin

# Inforens RAG Chatbot

This is a Retrieval-Augmented Generation (RAG) chatbot built using `LangChain`, `Ollama`, and `FAISS` to assist users with information from the [Inforens](https://www.inforens.com) website. The chatbot scrapes key pages of the website, embeds the content, and uses a local language model (like Mistral) to answer user questions **strictly based on the website content**.

---

##  Features

- Web scraping of multiple Inforens pages
- Text chunking and embedding using LangChain
- FAISS-based vector similarity search
- Query answering via LangChain's RetrievalQA chain
- Uses local Ollama LLM (e.g., Mistral)
- Caches scraped data to avoid unnecessary re-scraping


## Installation

1. **Clone this repo:**
   ```bash
   git clone https://github.com/your-username/inforens-rag-chatbot.git
   cd inforens-rag-chatbot
   run python prelogin.py in terminal
