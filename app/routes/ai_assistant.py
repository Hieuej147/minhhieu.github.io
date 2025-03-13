from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename
import os
from openai import OpenAI
import pdfplumber
import logging
import time

# Cấu hình logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

ai_assistant_bp = Blueprint('ai_assistant', __name__, url_prefix='/ai-assistant')

# Khởi tạo client OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

# Thư mục lưu tài liệu
BASE_UPLOAD_FOLDER = 'app/static/uploads/uploadss'

@ai_assistant_bp.route('/')
def ai_assistant():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    if 'chat_history' not in session:
        session['chat_history'] = []
    return render_template('chatbot.html', username=session['username'])

@ai_assistant_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        logger.error("No file part in request")
        return jsonify({'status': 'error', 'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        logger.error("No selected file")
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400
    if file and file.filename.endswith(('.pdf', '.txt', '.md')):
        username = session.get('username')
        if not username:
            logger.error("No username in session")
            return jsonify({'status': 'error', 'message': 'User not logged in'}), 401

        upload_folder = os.path.join(BASE_UPLOAD_FOLDER, username)
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder, exist_ok=True)

        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_folder, filename)
        try:
            file.save(file_path)
            logger.info(f"File saved successfully at: {file_path}")
            session['chat_history'].append({
                "role": "assistant",
                "content": f"Tôi đã nhận được file {filename}. Đang xử lý để tóm tắt..."
            })
            session.modified = True
            return jsonify({'status': 'success', 'filename': filename}), 200
        except PermissionError as e:
            logger.error(f"Permission denied saving file {file_path}: {e}")
            return jsonify({'status': 'error', 'message': 'Permission denied when saving file'}), 500
        except Exception as e:
            logger.error(f"Error saving file {file_path}: {e}")
            return jsonify({'status': 'error', 'message': f'Failed to save file: {str(e)}'}), 500
    logger.error(f"Unsupported file type: {file.filename}")
    return jsonify({'status': 'error', 'message': 'Unsupported file type'}), 400

@ai_assistant_bp.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    filename = data.get('filename')
    message = data.get('message')

    if 'chat_history' not in session:
        session['chat_history'] = []

    if filename:
        username = session.get('username')
        if not username:
            logger.error("No username in session")
            return jsonify({'status': 'error', 'message': 'User not logged in'}), 401

        file_path = os.path.join(BASE_UPLOAD_FOLDER, username, filename)
        if os.path.exists(file_path) and filename.endswith('.pdf'):
            try:
                # Trích xuất nội dung PDF (chỉ một lần tại đây)
                text = extract_text_from_pdf(file_path)
                if text:
                    max_length = 3000
                    if len(text) > max_length:
                        text = text[:max_length] + "... (đã cắt bớt nội dung để xử lý)"
                        logger.warning(f"Text truncated to {max_length} characters for {filename}")
                    logger.info(f"Extracted text from {filename}: {text[:100]}...")

                    session['chat_history'].append({
                        "role": "user",
                        "content": f"Tóm tắt nội dung tài liệu sau bằng tiếng Việt: {text}"
                    })
                    messages = session['chat_history']

                    summary = None
                    for attempt in range(3):
                        try:
                            response = client.chat.completions.create(
                                extra_headers={
                                    "HTTP-Referer": "http://127.0.0.1:5000/ai-assistant/",
                                    "X-Title": "DocFlow_NHT",
                                },
                                extra_body={},
                                model="qwen/qwq-32b:free",
                                messages=messages,
                                max_tokens=1000
                            )
                            summary = response.choices[0].message.content if response.choices else None
                            if summary:
                                break
                            logger.warning(f"Attempt {attempt + 1} failed: Summary is None or empty")
                            time.sleep(1)
                        except Exception as e:
                            logger.error(f"Attempt {attempt + 1} API error for {filename}: {e}")
                            time.sleep(1)

                    if not summary:
                        logger.error(f"Failed to get summary for {filename} after retries")
                        return jsonify({
                            'status': 'error',
                            'message': 'Không thể tóm tắt PDF. Bạn có thể copy nội dung từ PDF và gửi lại để tôi tóm tắt!'
                        }), 500

                    logger.info(f"Summary generated for {filename}: {summary[:100]}...")
                    session['chat_history'].append({"role": "assistant", "content": summary})
                    session.modified = True
                    return jsonify({'status': 'success', 'summary': summary}), 200
                else:
                    logger.error(f"No text extracted from {filename}")
                    session['chat_history'].append({
                        "role": "assistant",
                        "content": f"Tôi không thể trích xuất nội dung từ file {filename}. Bạn có thể copy nội dung từ file và gửi lại để tôi tóm tắt nhé!"
                    })
                    session.modified = True
                    return jsonify({
                        'status': 'error',
                        'message': 'Không thể trích xuất nội dung từ PDF. Bạn có thể copy nội dung và gửi lại để tôi tóm tắt!'
                    }), 400
            except Exception as e:
                logger.error(f"Error processing {filename}: {str(e)}")
                return jsonify({'status': 'error', 'message': f'Error processing PDF: {str(e)}'}), 500
        else:
            logger.error(f"File not found or not a PDF: {file_path}")
            return jsonify({'status': 'error', 'message': 'File not found or not a PDF'}), 400

    elif message:
        try:
            session['chat_history'].append({"role": "user", "content": message})
            if "file" in message.lower() or "tài liệu" in message.lower():
                prompt = f"Bạn vừa hỏi về file/tài liệu. Tôi không nhận file trực tiếp, nhưng nếu bạn đã upload, hãy click vào nguồn trong danh sách để tôi tóm tắt. Nếu chưa, hãy upload tài liệu và thử lại. Bạn cần giúp gì thêm không?"
            else:
                prompt = message

            messages = session['chat_history']

            summary = None
            for attempt in range(3):
                try:
                    response = client.chat.completions.create(
                        extra_headers={
                            "HTTP-Referer": "http://127.0.0.1:5000",
                            "X-Title": "DocFlow_NHT",
                        },
                        extra_body={},
                        model="qwen/qwq-32b:free",
                        messages=messages,
                        max_tokens=1000
                    )
                    summary = response.choices[0].message.content if response.choices else None
                    if summary:
                        break
                    logger.warning(f"Attempt {attempt + 1} failed: Summary is None or empty")
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Attempt {attempt + 1} API error: {e}")
                    time.sleep(1)

            if not summary:
                logger.error("Failed to get response after retries")
                return jsonify({'status': 'error', 'message': 'Failed to get response from API'}), 500

            logger.info(f"Response generated: {summary[:100]}...")
            session['chat_history'].append({"role": "assistant", "content": summary})
            session.modified = True
            return jsonify({'status': 'success', 'summary': summary}), 200
        except Exception as e:
            logger.error(f"API error: {e}")
            return jsonify({'status': 'error', 'message': f'API error: {e}'}), 500

    logger.error("No filename or message provided")
    return jsonify({'status': 'error', 'message': 'No filename or message provided'}), 400

def extract_text_from_pdf(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text(x_tolerance=2) or ""
                if page_text:
                    text += page_text + "\n"
                else:
                    logger.warning(f"No text extracted from page {page.page_number} in {file_path}")
            return text.strip() if text.strip() else None
    except pdfplumber.PageSizeError as e:
        logger.error(f"PDF page size error in {file_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {e}")
        return None