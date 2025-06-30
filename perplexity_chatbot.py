import requests

class PerplexityChatbot:
    def __init__(self, api_key, content_file_path="inforens_scraped_data.txt"):
        self.api_key = api_key
        self.content_file_path = content_file_path
        self.full_text = self._load_content()

    def _load_content(self):
        try:
            with open(self.content_file_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            print("Content file not found.")
            return ""

    def ask_question(self, user_question):
        if not self.full_text:
            return "No content loaded. Please check the .txt file."

        prompt = (
            "You are a helpful assistant representing Inforens, an organization dedicated to supporting international students.  "
            "You are part of the Inforens team, so refer to it as 'our website' or 'our services' — not as a third party. "

            "Answer the question strictly using the context provided below, which has been sourced directly from the Inforens website.  "
            "Use reasoning based only on this context—do not use any external knowledge.  "
            "Your response should be concise and informative. If relevant information is found, include a polite redirect to the specific URL where the content appears."
            "Your goal is to help students navigate the Inforens website and discover the right resources.\n\n"

            f"Content:\n{self.full_text}\n\n"
            f"Question: {user_question}\n"
            "Answer:"
        )



        payload = {
            "model": "sonar",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500
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
    # Replace this with your actual Perplexity API key
    api_key = "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"

    bot = PerplexityChatbot(api_key)

    print("Ask me anything about Inforens (type 'exit' to quit):")
    while True:
        question = input("You: ").strip()
        if question.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        answer = bot.ask_question(question)
        print(f"Inforens Bot: {answer}\n")
