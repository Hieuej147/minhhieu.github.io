# app/routes/chat.py
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime
from openai import OpenAI

chat = Blueprint('chat', __name__, url_prefix='/chat')

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

@chat.route('/')
def chat_room():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    print(f"Accessing chat room for user: {session['username']}")
    return render_template('chat.html', username=session['username'])

@chat.route('/send_message', methods=['POST'])
def send_message():
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'Not logged in'}), 401
    print(f"Sending message from user: {session['username']}")
    data = request.get_json()
    message_content = data.get('message')
    if message_content:
        try:
            completion = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "http://127.0.0.1:5000",
                    "X-Title": "DocFlow_NHT",
                },
                extra_body={},
                model="deepseek/deepseek-chat::free",
                messages=[
                    {
                        "role": "user",
                        "content": message_content
                    }
                ]
            )
            bot_response = completion.choices[0].message.content

            bot_message = {
                'username': 'jasmine',
                'content': bot_response,
                'timestamp': datetime.now().strftime('%H:%M'),
                'is_bot': True
            }

            return jsonify({'status': 'success', 'messages': [bot_message]})
        except Exception as e:
            print(f"Error with OpenRouter API: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    return jsonify({'status': 'error', 'message': 'No message provided'}), 400