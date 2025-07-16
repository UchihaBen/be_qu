from fastapi import FastAPI, Query, HTTPException, Header, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from fastapi.middleware.cors import CORSMiddleware
import json
from pydantic import BaseModel

import os
import re
from google import genai
app = FastAPI()
GENMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyAk6nXa0WJpsSTKjYCf4-7Gzm4AJtinamc')
client = genai.Client(api_key=GENMINI_API_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class generateQuestionBy9Anh(BaseModel):
    amount: int
    documentID: Optional[str] = None
    gptModel: Optional[str] = ""
    grade: int
    note: Optional[str] = ""
    questionType: Optional[Dict[str, int]] = {}
    subject: str
    topic: Optional[List[str]] = []   

class generateQuestionBy9AnhWithTopic1(BaseModel):
    amount: int
    document: str
    grade: int
    questionType: Optional[Dict[str, int]] = {}
    subject: str
def load_books_from_json():
    try:
        with open('data/processed/data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get("books", [])
    except:
        return []

def find_content_by_topic(grade, subject, topics):
    try:
        # Đọc dữ liệu từ JSON
        all_books = load_books_from_json()
        
        # Tìm sách theo grade và subject
        target_book = None
        for book in all_books:
            if book.get("gradeId") == f"Lớp {grade}" and book.get("subjectId") == subject:
                target_book = book
                break
        
        if not target_book:
            print(f"Không tìm thấy sách cho Lớp {grade} - {subject}")
            return ""
        
        print(f"Tìm thấy sách: {target_book.get('name')}")
        
        found_contents = []
        
        for topic in topics:
            print(f"topic: {topic}")
            
            if " - " in topic:
                unit_part, lesson_name = topic.split(" - ", 1)
                print(f"   Unit: {unit_part}")
                print(f"   Lesson: {lesson_name}")
                
                target_chapter = None
                for chapter in target_book.get("chapters", []):
                    if chapter.get("name") == unit_part:
                        target_chapter = chapter
                        break
                
                if not target_chapter:
                    print(f" Không tìm thấy chapter: {unit_part}")
                    continue
                
                print(f"Tìm thấy chapter: {target_chapter.get('name')}")
                
                target_lesson = None
                for lesson in target_chapter.get("lessons", []):
                    if lesson.get("name") == lesson_name:
                        target_lesson = lesson
                        break
                
                if not target_lesson:
                    print(f"Không tìm thấy lesson: {lesson_name}")
                    continue
                
                print(f"Tìm thấy lesson: {target_lesson.get('name')}")
                
                content = target_lesson.get("content", "")
                if content:
                    formatted_content = f"{unit_part}\n{lesson_name}\n{content}\n\n"
                    found_contents.append(formatted_content)
                    print(f"Đã lấy content: {len(content)} ký tự")
                else:
                    print(f" Lesson không có content")
            else:
                print(f" Topic không đúng format: {topic}")
        
        final_content = "".join(found_contents)
        print(f"Tổng cộng tìm được: {len(found_contents)} lessons, {len(final_content)} ký tự")
        
        return final_content
        
    except Exception as e:
        print(f"Lỗi khi tìm content: {e}")
        return ""

@app.get("/book-lesson")
def get_book_lesson(
    gradeId: str = Query(...),
    subjectId: str = Query(...),
    allBook: Optional[bool] = Query(False),
    allowedBook: Optional[bool] = Query(False)
):
    gradeId = "Lớp 6"
    subjectId = "Tiếng Anh"
    
    print(f"API Request - Lớp: {gradeId}, Môn: {subjectId}")
    print(f"Parameters - allBook: {allBook}, allowedBook: {allowedBook}")
    
    all_books = load_books_from_json()
    
    # print(f"Tổng số sách đọc được: {len(all_books)}")
    # if all_books:
    #     print(f"Sách đầu tiên: {all_books[0].get('name', 'N/A')}")
    #     print(f"Lớp: {all_books[0].get('gradeId', 'N/A')}")
    #     print(f"Môn: {all_books[0].get('subjectId', 'N/A')}")
    # else:
    #     print("Không đọc được dữ liệu từ JSON!")

    filtered_books = []
    for book in all_books:
        book_grade = book.get("gradeId")
        book_subject = book.get("subjectId")
        
        # Debug từng cuốn sách
        # print(f"Kiểm tra sách: {book.get('name', 'N/A')}")
        # print(f"   - Lớp sách: '{book_grade}' vs Tìm kiếm: '{gradeId}'")
        # print(f"   - Môn sách: '{book_subject}' vs Tìm kiếm: '{subjectId}'")
        # print(f"   - Khớp lớp: {book_grade == gradeId}")
        # print(f"   - Khớp môn: {book_subject == subjectId}")
        
        if book_grade == gradeId and book_subject == subjectId:
            # print(f"Tìm thấy sách phù hợp: {book.get('name')}")
            result_book = {
                "id": book.get("id"),
                "name": book.get("name"),
                "bookDataToGenerateQuestionUrl": book.get("bookDataToGenerateQuestionUrl", ""),
                "chapters": []
            }
            
            for chapter in book.get("chapters", []):
                result_chapter = {
                    "id": chapter.get("id"),
                    "name": chapter.get("name"),
                    "lessons": []
                }
                
                # Thêm lessons với content
                for lesson in chapter.get("lessons", []):
                    result_lesson = {
                        "id": lesson.get("id"),
                        "name": lesson.get("name"),
                        "content": lesson.get("content", "")
                    }
                    result_chapter["lessons"].append(result_lesson)
                
                result_book["chapters"].append(result_chapter)
            
            filtered_books.append(result_book)
        else:
            print(f"Sách không khớp: {book.get('name')}")
    
    # print(f"Kết quả cuối cùng: {len(filtered_books)} sách được tìm thấy")
    return filtered_books
    # Get API key from environment variable

def genqa(amount, grade, note, questionType, subject, topic, content):
    # print(f"📊 Generating {amount} questions for {subject} - Grade {grade} with topics: {topic}")

    
    # Create prompt that specifically requests JSON format
    prompt = f"""
Vai trò: bạn là một AI gia sư {subject} cho học sinh lớp {grade}.

Chú thích của người dùng: {note} "có thể có hoặc không"

NỘI DUNG SÁCH GIÁO KHOA: {content}

YÊU CẦU: Tạo câu hỏi với số lượng:
- Multiple Choice: {questionType['multiple-choice']} câu
- Fill-in: {questionType['fill-in']} câu  
- Open-ended: {questionType['open']} câu

Chủ đề: {', '.join(topic)}

QUAN TRỌNG: Trả về kết quả CHÍNH XÁC theo định dạng JSON sau đây, không thêm text nào khác:

[
  {{
    "question": "Câu hỏi cụ thể ở đây",
    "type": "multiple-choice",
    "correct_answers": ["đáp án đúng"],
    "incorrect_answers": ["đáp án sai 1", "đáp án sai 2", "đáp án sai 3"],
    "explanation": "Giải thích chi tiết",
    "level": "intermediate"
  }},
  {{
    "question": "Câu hỏi fill-in ở đây với _____ chỗ trống",
    "type": "fill-in", 
    "correct_answers": ["từ điền vào"],
    "incorrect_answers": [],
    "explanation": "Giải thích ngữ pháp",
    "level": "intermediate"
  }},
  {{
    "question": "Câu hỏi mở ở đây",
    "type": "open",
    "correct_answers": ["Gợi ý đáp án mẫu"],
    "incorrect_answers": [],
    "explanation": "Hướng dẫn trả lời", 
    "level": "intermediate"
  }}
]

Chỉ trả về JSON array, không có text giải thích thêm.
"""

    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"Attempt {retry_count + 1}/{max_retries}")
            
            # Call Gemini API
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[prompt]
            )
            # print((f"Response: {response.text}"))
            if response and hasattr(response, 'text'):
                response_text = response.text.strip()
                
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    json_str = response_text
                
                questions = json.loads(json_str)

                # print(f"Successfully generated {len(questions)} questions")
                return questions
                
            else:
                print("API không trả về response")
                retry_count += 1
                
        except json.JSONDecodeError as e:
            print(f"Lỗi parse JSON (Attempt {retry_count + 1}): {e}")
            if retry_count < max_retries - 1:
                print(f"Retrying... ({retry_count + 2}/{max_retries})")
            retry_count += 1
            
        except Exception as e:
            print(f"Lỗi khi gọi API GenMini (Attempt {retry_count + 1}): {e}")
            if retry_count < max_retries - 1:
                print(f"Retrying... ({retry_count + 2}/{max_retries})")
            retry_count += 1
    
    # If all retries failed
    print(f"Failed to generate questions after {max_retries} attempts")
    return []
def genqa_with_doc(amount, grade, questionType, subject, document):
    print(f"📊 Generating {amount} questions for {subject} - Grade {grade} ")

    # Create prompt that specifically requests JSON format
    prompt = f"""
Vai trò: bạn là một AI gia sư {subject} cho học sinh lớp {grade}.

NỘI DUNG YÊU CẦU GEN THEO: {document}

YÊU CẦU: Tạo câu hỏi với số lượng:
- Multiple Choice: {questionType['multiple-choice']} câu
- Fill-in: {questionType['fill-in']} câu  
- Open-ended: {questionType['open']} câu


QUAN TRỌNG: Trả về kết quả CHÍNH XÁC theo định dạng JSON sau đây, không thêm text nào khác:

[
  {{
    "question": "Câu hỏi cụ thể ở đây",
    "type": "multiple-choice",
    "correct_answers": ["đáp án đúng"],
    "incorrect_answers": ["đáp án sai 1", "đáp án sai 2", "đáp án sai 3"],
    "explanation": "Giải thích chi tiết",
    "level": "intermediate"
  }},
  {{
    "question": "Câu hỏi fill-in ở đây với _____ chỗ trống",
    "type": "fill-in", 
    "correct_answers": ["từ điền vào"],
    "incorrect_answers": [],
    "explanation": "Giải thích ngữ pháp",
    "level": "intermediate"
  }},
  {{
    "question": "Câu hỏi mở ở đây",
    "type": "open",
    "correct_answers": ["Gợi ý đáp án mẫu"],
    "incorrect_answers": [],
    "explanation": "Hướng dẫn trả lời", 
    "level": "intermediate"
  }}
]

Chỉ trả về JSON array, không có text giải thích thêm.
"""

    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"Attempt {retry_count + 1}/{max_retries}")
            
            # Call Gemini API
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[prompt]
            )
            # print((f"Response: {response.text}"))
            if response and hasattr(response, 'text'):
                response_text = response.text.strip()
                
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    json_str = response_text
                
                questions = json.loads(json_str)

                # print(f"Successfully generated {len(questions)} questions")
                return questions
                
            else:
                print("API không trả về response")
                retry_count += 1
                
        except json.JSONDecodeError as e:
            print(f"Lỗi parse JSON (Attempt {retry_count + 1}): {e}")
            if retry_count < max_retries - 1:
                print(f"Retrying... ({retry_count + 2}/{max_retries})")
            retry_count += 1
            
        except Exception as e:
            print(f"Lỗi khi gọi API GenMini (Attempt {retry_count + 1}): {e}")
            if retry_count < max_retries - 1:
                print(f"Retrying... ({retry_count + 2}/{max_retries})")
            retry_count += 1
    
    # If all retries failed
    print(f"Failed to generate questions after {max_retries} attempts")
    return []

@app.post("/api/v1/book-embedding/generate-question")
def generateQuestionBy9Anh(request: generateQuestionBy9Anh):
    
    content = find_content_by_topic(request.grade, request.subject, request.topic)
    response_data = {
        "name": f"{request.subject} - Grade {request.grade} - {', '.join(request.topic) if request.topic else 'General'}",
        "questions": []
    }
    
    questions = genqa(
        amount=request.amount,
        grade=request.grade,
        note=request.note,
        questionType=request.questionType,
        subject=request.subject,
        topic=request.topic,
        content=content
    )
    
    response_data["questions"] = questions
    
    return response_data

@app.post("/api/v1/marker/generate-question")
def generateQuestionBy9AnhWithTopic(request: generateQuestionBy9AnhWithTopic1):

    print(f"Received request: {request}")
    response_data = {
        "name": f"{request.subject} - Grade {request.grade}",
        "questions": []
    }
    
    print(f"Request details: amount={request.amount}, grade={request.grade}, document={request.document},questionType={request.questionType}, subject={request.subject}")
    # print(f"Note: {request.note if request.note else 'No note provided'}")
    questions = genqa_with_doc(
        amount=request.amount,
        grade=request.grade,
        questionType=request.questionType,
        subject=request.subject,
        document = request.document
    )
    
    response_data["questions"] = questions
    
    return response_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)