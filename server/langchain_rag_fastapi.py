from fastapi import FastAPI,Body
from rag_with_async_table import main
app = FastAPI()
app.add_middleware()