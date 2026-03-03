from dotenv import load_dotenv
load_dotenv()

from cmp.server.fastmcp import fastMcp
from fstapi  import FastAPI
from src.tools import create_calendar_event, list_calendar_events


# MCP SERVER
mcp = FastMCP("mcp-todo-sample",hosts="0.0.0.0", port=8002, instractions="M365 할일과 일정을 관리하는 MCP 서버입니다.")

# MCP TOOLS
mcp.add_tool(list_calendar_events)
mcp.add_tool(create_calendar_event)

app.mount("/", mcp.streamable_http_app())

# health check
@app.get("/health")
async def health(request:Request):
    return JSONResponse({"status":"ok"})

# FASTAPI APP
app = FastAPI(title="MCP Todo Sample", version="0.1.0")
app.include_router(mcp.router)