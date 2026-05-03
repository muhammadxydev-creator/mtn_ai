# MTN Nigeria AI Chatbot Simulation

A web-based AI-powered support chatbot running in a simulated myMTN NG environment.

## Tech Stack

- **Frontend**: React 19 + TypeScript + Vite + Tailwind CSS (TGO template)
- **Backend**: Python FastAPI with integrated NLP
- **Database**: Supabase (PostgreSQL)
- **NLP**: AfroXLMR for intent classification, FastText for language detection, spaCy for NER

## Project Structure

```
/workspace
├── tgo-web/          # Frontend (React)
└── tgo-api/          # Backend (FastAPI + NLP)
```

## Features

- 24/7 web-based access via browser
- Multilingual NLP (English + Nigerian Pidgin)
- 23-intent ML classification
- Transparent escalation to simulated human agent
- Mock APIs for billing, catalogue, network, account