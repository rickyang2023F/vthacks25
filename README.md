# vthacks25

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.sample .env # then edit GEMINI_API_KEY
streamlit run streamlit_app.py