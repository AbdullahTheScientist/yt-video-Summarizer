import os
from flask import Flask, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = Flask(__name__)

def extract_transcript(youtube_video_url):
    """Extracts transcript from a given YouTube URL."""
    try:
        video_id = youtube_video_url.split("=")[-1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript
    except Exception as e:
        return f"Error: {str(e)}"

def generate_summary(transcript_text, words):
    """Generates a summary based on the transcript and word limit."""
    prompt = f"""
    Summarize the following transcript into {words} words, highlighting key points:
    {transcript_text}
    """
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text if response else "Error generating summary."

@app.route('/transcript', methods=['POST'])
def get_transcript():
    """API endpoint to fetch YouTube video transcript."""
    data = request.get_json()
    youtube_link = data.get("youtube_link")
    
    if not youtube_link:
        return jsonify({"error": "YouTube video link is required"}), 400
    
    transcript = extract_transcript(youtube_link)
    if transcript.startswith("Error"):
        return jsonify({"error": transcript}), 500
    
    return jsonify({"transcript": transcript}), 200

@app.route('/summarize', methods=['POST'])
def summarize_video():
    """API endpoint to summarize a YouTube video."""
    data = request.get_json()
    youtube_link = data.get("youtube_link")
    word_count = data.get("word_count", 100)  # Default to 100 words
    
    if not youtube_link:
        return jsonify({"error": "YouTube video link is required"}), 400
    
    transcript_text = extract_transcript(youtube_link)
    if transcript_text.startswith("Error"):
        return jsonify({"error": transcript_text}), 500
    
    summary = generate_summary(transcript_text, word_count)
    return jsonify({"summary": summary}), 200

@app.route('/ask', methods=['POST'])
def ask_question():
    """API endpoint to ask a question about the summary."""
    data = request.get_json()
    user_input = data.get("user_input")
    summary = data.get("summary")
    
    if not user_input or not summary:
        return jsonify({"error": "Both user input and summary are required"}), 400
    
    response = genai.GenerativeModel("gemini-pro").generate_content(
        f"""
        You are a helpful assistant. Provide a well-structured response based on the summary below.
        Summary:
        {summary}
        
        User: {user_input}
        """
    )
    
    return jsonify({"response": response.text if response else "Error generating response."}), 200

if __name__ == "__main__":
    app.run(debug=True)
