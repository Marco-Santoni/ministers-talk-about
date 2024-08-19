from openai import OpenAI
import dotenv

dotenv.load_dotenv(".env")

import os

client = OpenAI(
  organization='org-ax4JqIkt2hzZ2jbuXPdlYLtQ',
  project='proj_vFrisMCv1olxft7dYzGi8dXB',
  api_key=os.getenv("OPEN_AI_API_KEY")
)

text = """
Consider the following Tweet posted by a Minister of Foreign Affairs in Italy.
"Voglio esprimere solidarietà a @paola_egonu e lo sdegno più totale per questo grave gesto di becero razzismo. Il mio impegno contro ogni forma di discriminazione è massimo, soprattutto per sensibilizzare i più giovani su episodi come questo. Forza Paola sei il nostro orgoglio 🇮🇹"

Is the content of the Tweet relevant and pertaining to his role of a Minister of Foreign Affairs?
Answer only with Yes or No or Not Sure
"""

completion = client.chat.completions.create(
  model="gpt-4o",
  messages=[
    {"role": "system", "content": text}
  ]
)

print(completion.choices[0].message)
