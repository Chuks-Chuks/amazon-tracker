# 🛒 Amazon Price Checker 

This is a parameterized QA Automation test project built with:
- Selenium WebDriver
- pytest
- PostgreSQL (via psycopg2)
- Custom logging and dynamic user-agent

It searches multiple products on Amazon, extracts details (title, price, rating, URL) and saves them into a database.

---

## 📦 Project structure

amazon-price-checker/
├── database/
│ ├── init.py
│ └── db.py
├── pages/
│ └── amazon.py
├── tests/
│ ├── conftest.py
│ └── test_amazon.py
├── utils/
│ └── logger.py
├── screenshots/
├── requirements.txt
├── .env.example
└── README.md

## 📦 Installation

```bash
pip install -r requirements.txt
