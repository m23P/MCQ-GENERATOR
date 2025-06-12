from flask import Flask, render_template, request, jsonify 
import os
import PyPDF2
import random
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk import pos_tag
from nltk.corpus import wordnet
import spacy

# Initialize Flask appG
app = Flask(__name__)

# Download NLTK resources
nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")
nltk.download("wordnet")    # to find synonyms/distractors.

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + " "
    return text.strip()

# Function to extract nouns
def extract_nouns(text):
    words = word_tokenize(text)
    tagged_words = pos_tag(words)
    nouns = [word for word, pos in tagged_words if pos in ["NN", "NNS", "NNP", "NNPS"]]
    return list(set(nouns))

# Function to get similar words (distractors) using WordNet
def get_distractors(word):
    distractors = set()
    synsets = wordnet.synsets(word, pos=wordnet.NOUN)
    for syn in synsets:
        for lemma in syn.lemmas():
            name = lemma.name().replace("_", " ")
            if name.lower() != word.lower():
                distractors.add(name)
            if len(distractors) >= 3:
                break
        if len(distractors) >= 3:
            break
    return list(distractors)[:3]


# Function to generate MCQs
def generate_mcqs(text, num_questions):
    sentences = sent_tokenize(text)
    nouns = extract_nouns(text)
    random.shuffle(sentences)
    random.shuffle(nouns)


    mcqs = []
    used_sentences = set()
    used_nouns = set()

    for sentence in sentences:
        if len(mcqs) >= num_questions:
            break

        for noun in nouns:
            if noun in sentence and sentence not in used_sentences and noun not in used_nouns:
                question = sentence.replace(noun, "____", 1)
                distractors = get_distractors(noun)

                if len(distractors) < 3:
                    continue

                options = [noun] + distractors
                options = list(set(options))  # Remove any duplicates
                if len(options) < 4:
                    continue
                random.shuffle(options)

                mcqs.append({
                    "question": question,
                    "options": options,
                    "answer": noun
                })

                used_sentences.add(sentence)
                used_nouns.add(noun)
                break

    return mcqs

# Flask route for homepage
@app.route("/")
def index():
    return render_template("index.html")

# Flask route to handle file upload and MCQ generation
@app.route("/generate", methods=["POST"])
def generate():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    num_questions = int(request.form.get("num_questions", 5))

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filepath = os.path.join("uploads", file.filename)
    file.save(filepath)

    text = extract_text_from_pdf(filepath)
    mcqs = generate_mcqs(text, num_questions)

    return jsonify(mcqs)

if __name__ == "__main__":
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    app.run(debug=True)
    

   