from flask import Flask, request, jsonify
from groq import Groq
import PyPDF2
import docx
import io

app = Flask(__name__)

# ⚠️ IMPORTANT: Replace with your Groq API key
GROQ_API_KEY = "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"

def extract_text_from_pdf(file):
    """Extract text from PDF file"""
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file):
    """Extract text from DOCX file"""
    doc = docx.Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_text_from_txt(file):
    """Extract text from TXT file"""
    return file.read().decode('utf-8')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Summarization & Note Making API',
        'version': '1.0'
    }), 200

@app.route('/summarize', methods=['POST'])
def summarize():
    """
    Summarize document or text
    
    Accepts:
    - file: PDF/DOCX/TXT file (optional)
    - text: Plain text (optional)
    - chapter: Chapter name/topic (optional)
    - word_count: Desired summary length (default: 300)
    
    Returns: Summary in specified word count
    """
    try:
        if GROQ_API_KEY == "your_groq_api_key_here":
            return jsonify({'error': 'API key not configured'}), 500
        
        # Get parameters
        chapter = request.form.get('chapter', '')
        word_count = int(request.form.get('word_count', 300))
        
        # Extract text from file or use provided text
        text = ""
        
        if 'file' in request.files:
            file = request.files['file']
            filename = file.filename.lower()
            
            print(f"\n{'='*50}")
            print(f"📄 Processing File: {file.filename}")
            print(f"{'='*50}\n")
            
            # Extract text based on file type
            if filename.endswith('.pdf'):
                text = extract_text_from_pdf(file)
            elif filename.endswith('.docx'):
                text = extract_text_from_docx(file)
            elif filename.endswith('.txt'):
                text = extract_text_from_txt(file)
            else:
                return jsonify({
                    'error': 'Unsupported file format',
                    'message': 'Please upload PDF, DOCX, or TXT file'
                }), 400
                
        elif 'text' in request.form:
            text = request.form.get('text')
        else:
            return jsonify({
                'error': 'No input provided',
                'message': 'Please provide either file or text'
            }), 400
        
        if not text.strip():
            return jsonify({
                'error': 'Empty content',
                'message': 'The file or text is empty'
            }), 400
        
        # Create prompt for summarization
        if chapter:
            prompt = f"""You are an expert at creating educational summaries.

Text to summarize:
{text}

Task: Create a summary of the chapter/topic: "{chapter}"

Requirements:
- Write a clear, concise summary in approximately {word_count} words
- Focus ONLY on the "{chapter}" section/chapter
- Cover key concepts, main ideas, and important points
- Use simple, easy-to-understand language
- Structure: Introduction → Main Points → Conclusion

Generate the summary now:"""
        else:
            prompt = f"""You are an expert at creating educational summaries.

Text to summarize:
{text}

Task: Create a comprehensive summary

Requirements:
- Write a clear, concise summary in approximately {word_count} words
- Cover all key concepts and main ideas
- Use simple, easy-to-understand language
- Structure: Introduction → Main Points → Conclusion

Generate the summary now:"""
        
        print(f"📝 Generating summary...")
        print(f"   Chapter: {chapter if chapter else 'Full document'}")
        print(f"   Word count: {word_count}")
        
        # Initialize Groq client
        client = Groq(api_key=GROQ_API_KEY)
        
        # Generate summary
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert educational content summarizer. Create clear, concise summaries that capture key information."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.1-70b-versatile",
            temperature=0.3,
            max_tokens=2000,
        )
        
        summary = response.choices[0].message.content.strip()
        
        print(f"✅ Summary generated successfully!\n")
        
        return jsonify({
            'success': True,
            'summary': summary,
            'chapter': chapter if chapter else 'Full document',
            'word_count': len(summary.split())
        }), 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/create-notes', methods=['POST'])
def create_notes():
    """
    Create topic-wise notes from document
    
    Accepts:
    - file: PDF/DOCX/TXT file (optional)
    - text: Plain text (optional)
    - chapter: Chapter name (optional)
    
    Returns: Structured notes organized by topics
    """
    try:
        if GROQ_API_KEY == "your_groq_api_key_here":
            return jsonify({'error': 'API key not configured'}), 500
        
        chapter = request.form.get('chapter', '')
        
        # Extract text
        text = ""
        
        if 'file' in request.files:
            file = request.files['file']
            filename = file.filename.lower()
            
            print(f"\n{'='*50}")
            print(f"📝 Creating Notes: {file.filename}")
            print(f"{'='*50}\n")
            
            if filename.endswith('.pdf'):
                text = extract_text_from_pdf(file)
            elif filename.endswith('.docx'):
                text = extract_text_from_docx(file)
            elif filename.endswith('.txt'):
                text = extract_text_from_txt(file)
            else:
                return jsonify({'error': 'Unsupported file format'}), 400
                
        elif 'text' in request.form:
            text = request.form.get('text')
        else:
            return jsonify({'error': 'No input provided'}), 400
        
        if not text.strip():
            return jsonify({'error': 'Empty content'}), 400
        
        # Create prompt for note-making
        if chapter:
            prompt = f"""You are an expert note-maker for students.

Text:
{text}

Task: Create detailed, topic-wise notes for the chapter: "{chapter}"

Requirements:
1. Identify all major topics/concepts in this chapter
2. For each topic, provide:
   - Clear heading
   - Key points (bullet points)
   - Important definitions
   - Examples if available
3. Format as structured notes
4. Use markdown formatting
5. Make it student-friendly

Generate topic-wise notes now:"""
        else:
            prompt = f"""You are an expert note-maker for students.

Text:
{text}

Task: Create detailed, topic-wise notes from this content

Requirements:
1. Identify all major topics/concepts
2. For each topic, provide:
   - Clear heading
   - Key points (bullet points)
   - Important definitions
   - Examples if available
3. Format as structured notes
4. Use markdown formatting
5. Make it student-friendly

Generate topic-wise notes now:"""
        
        print(f"📚 Creating topic-wise notes...")
        print(f"   Chapter: {chapter if chapter else 'Full document'}")
        
        # Initialize Groq client
        client = Groq(api_key=GROQ_API_KEY)
        
        # Generate notes
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at creating organized, topic-wise educational notes. Make them clear, structured, and easy to study from."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.1-70b-versatile",
            temperature=0.3,
            max_tokens=3000,
        )
        
        notes = response.choices[0].message.content.strip()
        
        print(f"✅ Notes created successfully!\n")
        
        return jsonify({
            'success': True,
            'notes': notes,
            'chapter': chapter if chapter else 'Full document'
        }), 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/summarize-and-notes', methods=['POST'])
def summarize_and_notes():
    """
    Generate both summary AND notes in one request
    
    Accepts:
    - file: PDF/DOCX/TXT file
    - chapter: Chapter name (optional)
    - word_count: Summary word count (default: 300)
    
    Returns: Both summary and topic-wise notes
    """
    try:
        if GROQ_API_KEY == "your_groq_api_key_here":
            return jsonify({'error': 'API key not configured'}), 500
        
        chapter = request.form.get('chapter', '')
        word_count = int(request.form.get('word_count', 300))
        
        # Extract text
        text = ""
        
        if 'file' in request.files:
            file = request.files['file']
            filename = file.filename.lower()
            
            print(f"\n{'='*50}")
            print(f"📚 Processing: {file.filename}")
            print(f"{'='*50}\n")
            
            if filename.endswith('.pdf'):
                text = extract_text_from_pdf(file)
            elif filename.endswith('.docx'):
                text = extract_text_from_docx(file)
            elif filename.endswith('.txt'):
                text = extract_text_from_txt(file)
            else:
                return jsonify({'error': 'Unsupported file format'}), 400
        elif 'text' in request.form:
            text = request.form.get('text')
        else:
            return jsonify({'error': 'No input provided'}), 400
        
        if not text.strip():
            return jsonify({'error': 'Empty content'}), 400
        
        client = Groq(api_key=GROQ_API_KEY)
        
        # Generate Summary
        print(f"📝 Generating summary ({word_count} words)...")
        
        summary_prompt = f"""Text: {text}

Create a {word_count}-word summary{"of chapter: " + chapter if chapter else ""}. 
Cover key concepts clearly and concisely."""
        
        summary_response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert summarizer."},
                {"role": "user", "content": summary_prompt}
            ],
            model="llama-3.1-70b-versatile",
            temperature=0.3,
            max_tokens=2000,
        )
        
        summary = summary_response.choices[0].message.content.strip()
        
        # Generate Notes
        print(f"📚 Creating topic-wise notes...")
        
        notes_prompt = f"""Text: {text}

Create detailed topic-wise notes{"for chapter: " + chapter if chapter else ""}.
Format: Topics with bullet points, definitions, and key concepts."""
        
        notes_response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert note-maker."},
                {"role": "user", "content": notes_prompt}
            ],
            model="llama-3.1-70b-versatile",
            temperature=0.3,
            max_tokens=3000,
        )
        
        notes = notes_response.choices[0].message.content.strip()
        
        print(f"✅ Summary and Notes generated!\n")
        
        return jsonify({
            'success': True,
            'summary': summary,
            'notes': notes,
            'chapter': chapter if chapter else 'Full document',
            'summary_word_count': len(summary.split())
        }), 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("📚 SUMMARIZATION & NOTE MAKING API SERVER")
    print("="*60)
    
    if GROQ_API_KEY == "your_groq_api_key_here":
        print("⚠️  WARNING: Please add your Groq API key!")
        print("   Edit summarization_api.py line 9")
    else:
        print("✅ API Key: Configured")
    
    print("\n📡 API ENDPOINTS:")
    print("   GET  /health")
    print("        → Health check")
    print("\n   POST /summarize")
    print("        → Generate summary (300 words)")
    print("        → Body: file (PDF/DOCX/TXT), chapter (optional), word_count (optional)")
    print("\n   POST /create-notes")
    print("        → Create topic-wise notes")
    print("        → Body: file (PDF/DOCX/TXT), chapter (optional)")
    print("\n   POST /summarize-and-notes")
    print("        → Generate both summary AND notes")
    print("        → Body: file (PDF/DOCX/TXT), chapter (optional)")
    print("\n🌐 Server: http://127.0.0.1:5002")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5002, host='0.0.0.0')