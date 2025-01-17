from fastapi import FastAPI, Request
from fastapi_utils.tasks import repeat_every
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json 
from datetime import datetime
from constants import CORS_URLS
from bitcoin_timestamp import BitcoinTimestamp
from custom_util import get_live_bitcoin_price, convert_date_to_text
from database_connection import DatabaseConnection
from sqlalchemy.orm import Session
import openai
from fastapi_utils.session import FastAPISessionMaker
from fastapi_utils.tasks import repeat_every


# # /////question/////// iS THE URI OKAY? 
# # OR SHOULD WE CHANGE THE URI TO SOMETHING ELSE?
database_uri = f"sqlite:///./test.db?check_same_thread=False"
sessionmaker = FastAPISessionMaker(database_uri)

# TODO (3.1): define FastAPI app
app = FastAPI() 

# # TODO (5.4.1): define database connection
dBConnection = DatabaseConnection()

CORS_URLS = [
    "http://localhost",
    "http://localhost:3000"
]

# TODO (3.2): add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_URLS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# TODO (3.1)
"""
a index function to test if server is running
"""
@app.get("/")
async def root():
    content = {"message": "Hello World! This is a bitcoin monitoring service!"}
    return json.dumps(content)


# TODO (5.4.2)
"""
repeated task to update bitcoin prices periodically
"""
@app.on_event("startup")
@repeat_every(seconds=300000)  # 5 minutes
def update_bitcoin_price_task() -> None:
    with sessionmaker.context_session() as db:
        update_bitcoin_price(db=db)


def update_bitcoin_price(db:Session) -> None:

    print("Line 55")
    # instanceDBC = DatabaseConnection()
    if (get_live_bitcoin_price() > 0):

        instanceBT = BitcoinTimestamp(convert_date_to_text(datetime.now()), get_live_bitcoin_price() )
        print("Line 64")
        print("Price: ", instanceBT.price)
        print("Timestamp: ", instanceBT.timestamp)
        print("Line 68: ", type(instanceBT))
        dBConnection.insert_timestamp(instanceBT)

    else:
        print("API call failed and get_live_bitcoin_price() function returned 0.0")
    print("Line 65")
    print("Line 65")
    print("Line 65")
    print("Line 65")


# TODO (5.4.3)
"""
API endpoint to get bitcoin prices

:return:
    a list of bitcoinstamps
:rtype:
    json
"""

@app.get("/get_bitcoin_prices")
async def get_bitcoin_prices():
    dictList = []
    print("Line 95")
    for BTObj in dBConnection.get_all_timestampes():
        dictList.append(vars(BTObj))
        # print(BTObj)
    return json.dumps(dictList)

openai.api_key = "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"
messages = [{"role": "system", "content": "Hello World"}]

def CustomChatGPT(user_input):
    messages.append({"role": "user", "content": user_input})
    response = openai.Completion.create(
        engine="davinci-codex",
        prompt_messages=messages,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7,
    )
    ChatGPT_reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": ChatGPT_reply})
    return ChatGPT_reply

app.add_api_route("/api/chatgpt", CustomChatGPT)

# main function to run the server
if __name__ == '__main__':
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)