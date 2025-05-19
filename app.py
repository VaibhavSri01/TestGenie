from flask import Flask, render_template, request, session, redirect, url_for
import re, os, json
import google.generativeai as genai
from dotenv import load_dotenv

# Load API Key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize model
model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)
app.secret_key = 'testgeine-secret-key'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    topic = request.form['topic']
    num_questions = int(request.form['num_questions'])
    difficulty = request.form['difficulty']
    timer = int(request.form['timer'])

    # Create prompt
    if difficulty == "easy":
        prompt = f"""
            Act as a professional question setter. 
            Generate {num_questions} easy MCQ questions on the topic '{topic}'. 
            The difficulty of questions must range from basics to intermediate.
            
                Format:
                [
                    {{
                        "question",
                        "options": ["A", "B", "C", "D"],
                        "answer": "a/b/..."
                    }},
                    ...
                ]
                Only return a Python list of dictionaries, nothing else.
            """
        
    elif difficulty == "medium":
        prompt = f"""
            Act as a professional question setter. 
            Generate {num_questions} medium difficulty MCQ questions on '{topic}'. 
            The difficulty of questions must range from intermediate to advance. 
           
                Format:
                [
                    {{
                        "question",
                        "options": ["A", "B", "C", "D"],
                        "answer": "a/b/..."
                    }},
                    ...
                ]
                Only return a Python list of dictionaries, nothing else.
            """
    
    else:
        prompt = f"""
            Act as a professional question setter.
            Generate {num_questions} hard MCQ questions on '{topic}'.
            The difficulty of questions must be advance and extremely hard and language of question must be extremely confusing but correct. and
            Questions should be tricky and thought-provoking.\n
           
                Format:
                [
                    {{
                        "question",
                        "options": ["A", "B", "C", "D"],
                        "answer": "a/b/..."
                    }},
                    ...
                ]
                Only return a Python list of dictionaries, nothing else.
            """

    # Call Gemini API
    response = model.generate_content(prompt)

    raw_output = response.text.strip()
    if raw_output.startswith("```"):
        raw_output = re.sub(r"^```(?:python|json)?\s*", "", raw_output)  
        raw_output = re.sub(r"\s*```$", "", raw_output)

    # Attempt to parse the output as JSON instead of using eval
    try:
        questions = json.loads(raw_output)  # Use json.loads instead of eval
    except Exception as e:
        return f"<h3>Error parsing Gemini output:</h3><pre>{e}</pre><br><h4>Raw Response:</h4><pre>{raw_output}</pre>"

    

    # Store correct answers in session
    session['correct_answers'] = [q['answer'] for q in questions]

    return render_template("quiz.html", questions=questions, timer=timer)

@app.route('/submit', methods=['POST'])
def submit():
    correct_answers = session.get('correct_answers', [])
    user_answers = []

    score = 0
    for i in range(len(correct_answers)):
        selected = request.form.get(f'q{i}')
        user_answers.append(selected)
        if selected == correct_answers[i]:
            score += 1

    return render_template('result.html', score=score, total=len(correct_answers), user_answers=user_answers, correct_answers=correct_answers)

if __name__ == '__main__':
    app.run(debug=True)
