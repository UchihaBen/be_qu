
## Cài đặt

### 1. Clone repository
```bash
git clone <repository-url>
cd api_genqa
```

### 2. Cấu hình environment
Tạo file `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Chạy với Docker (Khuyến nghị)

#### Sử dụng Docker Compose:
```bash
docker-compose up -d --build
```

### 4. Chạy local (không dùng Docker)
```bash
pip install -r requirements.txt

# Chạy server
python main_module.py
```

## 📚 API Endpoints

### 1. Tạo câu hỏi từ nội dung sách giáo khoa
```
POST /api/v1/book-embedding/generate-question
```
### 2. Tạo câu hỏi từ document tùy chỉnh
```
POST /api/v1/marker/generate-question
```

### 3. Lấy danh sách sách và bài học
```
GET /book-lesson?gradeId=Lớp 6&subjectId=Tiếng Anh
```


