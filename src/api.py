from typing import List, Literal
import requests
from os import environ

BASE_URL = 'https://assessment.silvernova.ai/'

# Get API_KEY from env
API_KEY = "b243befe-6a84-4198-be4c-3e4f3d1e31bd"

def execute_prompt(message: str):
  url = f'{BASE_URL}prompt'
  headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {API_KEY}'
  }
  response = requests.post(url, json={
    'message': message
  }, headers=headers)
  response.raise_for_status()
  return response.json()

def embed_texts(texts: List[str], input_type: Literal['document', 'query']) -> List[List[float]]:
  url = f'{BASE_URL}embed'
  headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {API_KEY}'
  }
  response = requests.post(url, json={
    'texts': texts,
    'input_type': input_type
  }, headers=headers)
  response.raise_for_status()
  result = response.json()
  return result['embeddings']