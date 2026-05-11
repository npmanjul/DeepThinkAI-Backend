python -m uvicorn main:app --reload

ai_blog_writer/
│
├── app/
│   │
│   ├── main.py
│   │
│   ├── graph/
│   │   ├── builder.py
│   │   ├── state.py
│   │   └── nodes.py
│   │
│   ├── schemas/
│   │   └── blog_schema.py
│   │
│   ├── services/
│   │   ├── llm_service.py
│   │   ├── search_service.py
│   │   └── image_service.py
│   │
│   ├── prompts/
│   │   └── prompts.py
│   │
│   ├── api/
│   │   └── routes.py
│   │
│   └── utils/
│       └── helpers.py
│
├── images/
│
├── outputs/
│
├── .env
├── requirements.txt
└── run.py