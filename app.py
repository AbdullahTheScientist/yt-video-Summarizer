# from flask import Flask, render_template, request
# from dotenv import load_dotenv
# import os
# import google.generativeai as genai
# from youtube_transcript_api import YouTubeTranscriptApi

# # Load environment variables
# load_dotenv()

# # Configure Gemini API
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# app = Flask(__name__)

# # Function to extract transcript from YouTube video
# def extract_transcript_details(youtube_video_url):
#     try:
#         video_id = youtube_video_url.split("v=")[1].split("&")[0]
#         transcript_text = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'hi'])  # Fetch English or Hindi
        
#         transcript = " ".join([i["text"] for i in transcript_text])
#         return transcript, video_id
#     except Exception as e:
#         return str(e), None

# # Function to generate summary using Gemini AI
# def generate_gemini_content(transcript_text, words):
#     prompt = f"""
#     You are a YouTube video summarizer. You will summarize the transcript
#     and provide the key points within {words} words. Here is the transcript:
#     """
    
#     model = genai.GenerativeModel("gemini-pro")
#     response = model.generate_content(prompt + transcript_text)
#     return response.text if response else "No summary generated."

# @app.route("/", methods=["GET", "POST"])
# def index():
#     summary = None
#     error = None
#     video_id = None

#     if request.method == "POST":
#         youtube_link = request.form.get("youtube_link")
#         words = int(request.form.get("words", 100))

#         if youtube_link:
#             transcript_text, video_id = extract_transcript_details(youtube_link)
#             if video_id:
#                 summary = generate_gemini_content(transcript_text, words)
#             else:
#                 error = transcript_text

#     return render_template("index.html", summary=summary, video_id=video_id, error=error)

# if __name__ == "__main__":
#     app.run(debug=True)




from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = Flask(__name__)

# Function to extract transcript from YouTube video
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("v=")[1].split("&")[0]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'hi'])  # Fetch English or Hindi
        
        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript, video_id
    except Exception as e:
        return str(e), None

# Function to generate summary using Gemini AI
def generate_gemini_content(transcript_text, words):
    prompt = f"""
    You are a YouTube video summarizer. You will summarize the transcript
    and provide the key points within {words} words. Here is the transcript:
    """

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text if response else "No summary generated."

# Root Route
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to the YouTube Summarizer API! Use /summarize to summarize a video."})

# Summarization API
@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    youtube_link = data.get("youtube_link")
    words = int(data.get("words", 100))  # Default 100 words

    if not youtube_link:
        return jsonify({"error": "YouTube link is required"}), 400

    transcript_text, video_id = extract_transcript_details(youtube_link)

    if not video_id:
        return jsonify({"error": transcript_text}), 400

    summary = generate_gemini_content(transcript_text, words)

    return jsonify({
        "video_id": video_id,
        "summary": summary
    })

if __name__ == "__main__":
    app.run(debug=True)
