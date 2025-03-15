from dotenv import load_dotenv
load_dotenv(override=True)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from foodfusionai.utils import project_config
from foodfusionai.routers.users import user_router
from foodfusionai.routers.storage import storage_router
from foodfusionai.routers.llm import chats_router, llm_router
from foodfusionai.redis_rate_limiting import get_rate_limit_rules, RedisRateLimitMiddleware

# TODO local frontend testing not possible if ALLOW ORIGINS in Azure was added, remove DEVELOPMENT.md then

api_version = project_config['api']['version']
app = FastAPI(title=project_config['app']['title'], version=api_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # origins set in Azure Web App
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"]
)

rules, default_rule = get_rate_limit_rules()

# TODO add router for chats -> v1/chats/... --> separate from llm router
# add less strict rate limit rule for chats path because if the same as for llm calls, user cant see chats after limit exceeded
app.add_middleware(
    RedisRateLimitMiddleware,
    rate_limit_rules=rules,
    default_rule=default_rule,
    prefix="foodfusionai:ratelimit:"
)

app.include_router(user_router, prefix=f"/{api_version}/users", tags=["Users"])
app.include_router(storage_router, prefix=f"/{api_version}/items", tags=["Storage Management"])
app.include_router(chats_router, prefix=f"/{api_version}/chats", tags=["Chats"])
app.include_router(llm_router, prefix=f"/{api_version}/llm", tags=["LLM Requests"])

@app.get("/")
async def read_root():
    return {
        "API version": project_config['api']['version'],
        "description": project_config['api']['description']
    }

if __name__ == "__main__":
    if project_config['app']['status'] == "dev":
        uvicorn.run(app, host=project_config['api']['local']['host'], port=project_config['api']['local']['port'])