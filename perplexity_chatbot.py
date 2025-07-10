import requests

class PerplexityChatbot:
    def __init__(self, api_key, content_file_path="inforens_scraped_data.txt"):
        self.api_key = api_key
        self.content_file_path = content_file_path
        self.full_text = self._load_content()

    def _load_content(self): #function to open and read the notepad
        try:
            with open(self.content_file_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            print("Content file not found.")
            return ""

    def ask_question(self, user_question): 
        if not self.full_text:
            return "No content loaded. Please check the .txt file."
#we give this prompt to the LLM. These are instructions provided by the developer that is usually provided by an user in Perplexity
        prompt = (
            "You are an assistant representing Inforens, an organization helping international students. "
            "Your main job is to redirect students to the most relevant page on our website based on their question. "

            "Only use the content provided below — do not use external knowledge or speculation."
            "If relevant information is found, give a short sentence and add a clear redirect URL. DO NOT INCLUDE ANY CITATION NUMBERS LIKE [1][2] etc. "#because perplexity usually provides citations, we need to exclude it
            "If nothing is relevant, say 'Please ask me something relevant to Inforens or reach out to contact@inforens.com'\n\n"

            f"Content:\n{self.full_text}\n\n"
            f"Question: {user_question}\n"
            "Answer:"
        )
#model loading, sonar is lightweight
        payload = {
            "model": "sonar",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500 #number of tokens used
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post("https://api.perplexity.ai/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"API request failed: {str(e)}"

if __name__ == "__main__":
    api_key = "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"#need to insert key here

    bot = PerplexityChatbot(api_key)

    print("Ask me anything about Inforens:")
    while True:
        question = input("You: ").strip()
        if question.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        answer = bot.ask_question(question)
        print(f"Norry: {answer}\n")
