
## Быстрый старт
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r python/requirements.txt

# (опционально) 
brew install ollama && brew services start ollama
# выберите модель:
ollama run qwen2.5:7b-instruct "ok?"

# env
cp .env.example .env   # заполните ключи и логины (2GIS/Instagram/LLM)
make all               # или: python3 -m python.collect_all && (cd go && go run main.go)
