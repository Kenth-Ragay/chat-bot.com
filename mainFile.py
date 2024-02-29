import json
# this will allow us to match the best response from our inputs
from difflib import get_close_matches
import os
from flask import Flask, request, render_template, jsonify


# Running the web app
app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/process', methods=['POST'])
def application():
    file_path = os.path.abspath('data.json')
    # this code block will load all the data from the database.json file

    def load_knowledge_base(file_path: str) -> dict:
        with open(file_path, 'r') as file:
            data: dict = json.load(file)
        return data

    def save_knowledge_base(file_path: str, data: dict):
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)

    def find_best_match(user_question: str, questions: list[str]) -> str | None:
        matches: list = get_close_matches(
            user_question, questions, n=1, cutoff=0.6)
        return matches[0] if matches else None

    def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
        for q in knowledge_base["questions"]:
            if q["question"] == question:
                return q["answer"]
        return None

    def chat_bot():
        knowledge_base: dict = load_knowledge_base('data.json')

        while True:
            user_input: str = request.form['inputData']

            if user_input.lower() == 'quit':
                break

            best_match: str | None = find_best_match(
                user_input, [q["question"] for q in knowledge_base["questions"]])

            if best_match:
                answer: str = get_answer_for_question(
                    best_match, knowledge_base)
                return jsonify(answer)

            else:
                answer = "Sorry, I don\'t know the answer. Can you teach me?"
                new_answer: str = request.form['inputData']

                if new_answer.lower() != 'skip':
                    knowledge_base["questions"].append(
                        {"question": user_input, "answer": new_answer})
                    save_knowledge_base('data.json', knowledge_base)
                    answered = "Thank you! I learned a new response!"
                return jsonify(answered)

    return chat_bot()


if __name__ == '__main__':
    app.run(debug=True)
