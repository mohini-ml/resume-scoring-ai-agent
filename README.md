# Resume Scoring Agent

An AI-powered agent that analyzes resumes and provides a structured 
score (0-100) along with strengths, weaknesses, and improvement 
suggestions — powered by Google's Gemini API.

## Purpose

This project automates resume evaluation. It extracts text from 
resume files (PDF/DOCX), sends it to Gemini AI for analysis, and 
returns a structured JSON output with:
- Overall score (0-100)
- Strengths
- Weaknesses
- Suggestions for improvement

## Architecture

The project follows this pipeline:
Additionally, `parallel_score.py` uses `ThreadPoolExecutor` to score 
multiple resumes simultaneously (scalability feature).

## Setup Instructions

1. Clone the repository
2. Create a `.env` file in the root folder with your Gemini API key:
3. Install dependencies:
(or install individually: `google-generativeai`, `python-dotenv`, 
`flask`, `schedule`, `pdfplumber`, `python-docx`)
4. Run the scorer on a single resume:
5. Run the Flask API:
6. Run the scheduler (batch processing):
## Example Output

```json
{
"score": 78,
"strengths": [
 "Clear structure and formatting",
 "Relevant technical skills listed",
 "Quantified achievements in past roles"
],
"weaknesses": [
 "Missing summary/objective section",
 "No links to portfolio or GitHub"
],
"suggestions": [
 "Add a brief professional summary at the top",
 "Include links to relevant projects or portfolio"
]
}