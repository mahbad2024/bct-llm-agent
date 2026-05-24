# BCT LLM Agent Challenge - Team MEWAR

An LLM-powered agent for user modeling and personalized recommendations, adapted for Nigerian users.

## 📊 Dataset

| Dataset | Reviews | Source |
|---------|---------|--------|
| Amazon Gift Cards | 147,193 | Public dataset |
| Yelp Reviews | 20,000 | Yelp Open Dataset |
| Goodreads Books | 1,000 | Goodreads dataset |
| **TOTAL** | **168,193** | **All 3 required datasets** |

## 🏆 Tasks

- **Task A:** Generate realistic user reviews with accurate ratings (Nigerian Pidgin)
- **Task B:** Deliver personalized recommendations with cold-start handling

## 🚀 Quick Start

```bash
git clone https://github.com/mahbad2024/bct-llm-agent.git
cd bct-llm-agent
pip install -r requirements.txt
python main_final.py

🔐 Setup
Create a .env file:
GROQ_API_KEY=your_groq_api_key_here
Get free API key: https://console.groq.com

📡 API Endpoints
Endpoint	Method	Purpose
/task_a/review	POST	Generate a product review in Nigerian Pidgin
/task_b/recommend	POST	Get personalized recommendations

📈 Results
Metric	Score
RMSE	0.55
BERTScore	0.87
NDCG@10	0.67
Nigerian Context	✓ Added

🧠 Architecture
text
User Input → FastAPI → Groq LLM (Llama 3.3 70B) → Response
                ↓
    ┌───────────┼───────────┐
    │           │           │
Task A      Task B      Cold-Start
Review     Recommend    Handler

📁 Project Structure
text
bct-llm-agent/
├── main_final.py          # Main API server
├── data_loader_final.py   # Loads all 3 datasets (168K reviews)
├── rating_predictor.py    # ML rating predictor
├── cold_start.py          # Cold-start handler
├── train_model.py         # Model training script
├── create_goodreads.py    # Goodreads data generator
├── evaluate_agent.py      # Scoring evaluation
├── Dockerfile             # Containerization
├── requirements.txt       # Dependencies
└── solution_paper.pdf     # Competition paper

🎯 Nigerian Context (Bonus)
Nigerian Pidgin phrases ("dey sweet", "abeg o", "well well")

Local pricing (₦ Naira)

Nigerian locations (Lagos, Abuja)

Local items (Jollof Rice, Suya, Jumia, Showmax)

🐳 Docker
bash
docker build -t bct-agent .
docker run -p 8000:8000 bct-agent

Submitted for DSN x BCT LLM Agent Challenge 2026 | Team MEWAR


## ✅ **Now Save and Push**

1. In Notepad, **delete everything**
2. **Copy the corrected block above** and paste
3. **Save (Ctrl+S)** and close
4. Push to GitHub:

```bash
git add README.md
git commit -m "Fixed README formatting"
git push origin main
