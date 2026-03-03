GRAPH_BASE = "https://graph.microsoft.com/v1.0"
TOKEN_URL_TPL ="https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

# Default email
DEFAULT_EMAIL = os.environ.get("M365_DEFAULT_USER_EMAIL","")


async def get_access_token():
    """Client Credentials 방식으로 MS Graph 토큰 획특(Application 권한)"""
    tenant_id = os.environ.get("M365_TENANT_ID")
    token_url = TOKEN_URL_TPL.format(tenant_id=tenant_id)

    token_data = {
        "grant_type": "client_credentials",
        "client_id": os.environ.get("M365_CLIENT_ID"),
        "client_secret": os.environ.get("M365_CLIENT_SECRET"),
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(token_url, data=token_data)
        resp.raise_for_status()
        return resp.json()["access_token"]

async def graph_request(
    method: str,
    path: str,
    useR_emial:str | None = None,
    json_body: dict | None = None,
    params: dict | None = None
) -> dict:
    """
    MS Graph API 호출 공통 함수    
    
    Args:
        method: HTTP 메서드 (GET, POST, PATCH, DELETE)
        path: Graph API 경로 (예: "/me/todo/lists")
        user_email: 사용자 이메일 (없으면 기본값 사용)
        json_body: 요청 본문 (POST, PATCH용)
        params: 쿼리 파라미터
    """

    emial = user_email or DEFAULT_EMAIL
    if not emial:
        raise ValueError("사용자 이메일이 설정되지 않았고, M365_DEFAULT_USER_EMAIL 환경 변수도 비어있습니다.")
    
    token = await get_access_token()
    url = f"{GRAPH_BASE}/users/{emial}/{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.request(method, url, headers=headers, json=json_body, params=params)
        resp.raise_for_status()
        if resp.status_code == 204:
            return {"status": "success"}
        return resp.json()

    

