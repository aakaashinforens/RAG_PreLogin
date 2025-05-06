#import all libraries
from langchain_ollama import OllamaEmbeddings, OllamaLLM #convert text to vectors for FAISS, LLM
from langchain_community.vectorstores.faiss import FAISS #store text chunks as vectors, and compares similarity to retrieve most relevant chunk
from langchain_core.documents import Document #represent chunk in a doc
from langchain_community.docstore.in_memory import InMemoryDocstore #temp storage of docs
from langchain.chains import RetrievalQA #chain that retrieves docs, passes to LLm and format answer
from langchain_core.prompts import PromptTemplate #to give instruction to LLM 
from langchain.text_splitter import RecursiveCharacterTextSplitter #splits large website into small chunks
import faiss #search large collection of vectors
import numpy as np 
#webscraping libraries
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import os

class RAGChatbot:
    def __init__(self, ollama_model="mistral"): #mistral is the ollama LLM model
        self.ollama_model = ollama_model
        self.vectorstore = None
        self.retriever = None
        self.chain = None #for QA chain

        self.embeddings = OllamaEmbeddings(model=self.ollama_model, temperature=0.3) #embedding model to convert text to vectors
        self.llm = OllamaLLM(model=self.ollama_model, temperature=0.3, top_k=30, top_p=0.9) #llm model
        self.text_splitter = RecursiveCharacterTextSplitter( #text splitter
            chunk_size=800,
            chunk_overlap=150,
            separators=["\n\n", "\n", ". ", " ", ""] #split para, then lines, then sentences, then spaces, then anywhere.
        )

    def extract_text_from_url(self, url): #extracting data from a url
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            driver.get(url)
            time.sleep(3)

            try:
                body = driver.find_element(By.TAG_NAME, 'body') #identify a place to click as a popup shows in inforens page 
                ActionChains(driver).move_to_element(body).click().perform() #click anywhere on the body except the popup to close the popup
                time.sleep(2) #delay
            except Exception:
                print(f"No popup to close for {url}")
            #extract content
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            text_content = soup.get_text(separator=' ', strip=True)
            driver.quit()

            print(f"Scraped content from: {url}")
            return text_content
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None

    def scrape_and_cache(self, filepath="inforens_scraped_data.txt", force_scrape=False): #check if website is scraped already. If scraped then does not perform scrape.
        if not force_scrape and os.path.exists(filepath):
            print("Using cached data from local file.")
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()

        print("Scraping fresh content from Inforens") #scrape if not scraped already
        urls = [
            "https://www.inforens.com/",
            "https://www.inforens.com/plans",
            "https://www.inforens.com/membership",
            "https://www.inforens.com/faq",
            "https://www.inforens.com/guides",
            "https://www.inforens.com/blogs"
        ]

        all_text = ""
        for url in urls:
            content = self.extract_text_from_url(url)
            if content:
                all_text += content + "\n\n"

        with open(filepath, "w", encoding="utf-8") as f: #save the scraped content
            f.write(all_text)
        print("Scraped content saved locally!")

        return all_text

    def process_text_for_retrieval(self, combined_text):
        if not combined_text: #check if text is available
            print("Error: No combined text to process.")
            return

        chunks = self.text_splitter.split_text(combined_text) #split large text into smaller chunks
        embeddings = [self.embeddings.embed_documents([chunk]) for chunk in chunks] #create embeddings
        embeddings = np.vstack([np.array(embed) for embed in embeddings])

        dimension = embeddings.shape[1]
        faiss_index = faiss.IndexFlatL2(dimension) #create FAISS to find similarity
        faiss_index.add(embeddings.astype(np.float32))

        documents = {str(i): Document(page_content=chunk) for i, chunk in enumerate(chunks)} #each chunk stored as doc
        docstore = InMemoryDocstore(documents) #docs stored in memory, not locally.
        index_to_docstore_id = {i: str(i) for i in range(len(chunks))} #mapping index number for each doc.

        self.vectorstore = FAISS(
            index=faiss_index,
            docstore=docstore,
            index_to_docstore_id=index_to_docstore_id,
            embedding_function=self.embeddings
        )

    def answer_question(self, question):
        if not self.vectorstore: #check if website scraped and built FAISS index.
            raise ValueError("Vector store not initialized. Run 'process_text_for_retrieval' first.")

        self.retriever = self.vectorstore.as_retriever() #to search most relevant link

        #Prompt to guide the LLM, so it does not blabber.
        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=(
                "You are a helpful assistant representing Inforens, an organization that supports international students. "
                "Answer ONLY using the context below, which is scraped directly from the Inforens website. "
                "Use your reasoning, but DO NOT answer from outside knowledge. "
                "If the user's question indicates they may benefit from a service, provide a brief answer and redirect "
                "Keep the answer short and sweet, redirect the user to the website by providing URL. "
                "As an assistant, you are supposed to help students navigate the site. "
                "Redirect them politely to the relevant webpage mentioned in the context.\n\n"
                "Context:\n{context}\n\n"
                "Question: {question}\n"
                "Answer:"
            )
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.retriever,
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt}
        )

        return qa_chain.run(question)



if __name__ == "__main__":
    chatbot = RAGChatbot()

    #load cached data or scrape if not found
    combined_text = chatbot.scrape_and_cache()

    #process the text for retrieval
    chatbot.process_text_for_retrieval(combined_text)

    #interactive Q&A loop
    print("Ask me anything about Inforens (type 'exit' or 'quit' to stop):\n")
    while True:
        user_question = input("You: ").strip()
        if user_question.lower() in ["exit", "quit"]:
            print("Exiting.")
            break

        try:
            response = chatbot.answer_question(user_question)
            print(f"Inforens Bot: {response}\n")
        except Exception as e:
            print(f"Error answering question: {str(e)}\n")
