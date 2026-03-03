from src.graph_client import graph_request, EFAULT_USER_EMAIL

async def create_calender_envet(
    subject:str,
    start_time:str,
    end_time:str,
    body:str | None = None,
    user_email:str | None = None,
    location:str | None = None,
    is_online:bool = False,
    attendees:list[str] | None = None
) -> dict:
    """
    M365 캘린더에 새 일정(이벤트)을 생성합니다.
    
    Args:
        subject: 일정 제목
        start_time: 시작 시간 (ISO 8601 포맷, 예: "2024-01-15T10:00:00")
        end_time: 종료 시간 (ISO 8601 포맷)
        body: 일정 내용
        user_email: 사용자 이메일 (없으면 기본값 사용)
        location: 장소
        is_online: 온라인 모임 여부
        attendees: 참석자 이메일 리스트
    Returns:
        생성된 이벤트 정보(id,weblin 등)    
    """
    event_body: dict = {
        "subject": subject,
        "start": {"dateTime": start_time, "timeZone": "Asia/Seoul"},
        "end": {"dateTime": end_time, "timeZone": "Asia/Seoul"},
        "isOnlineMeeting": is_online,
    }
    if body:
        event_body["body"] = {"contentType": "Text", "content": body}
    if attendees:
        event_body["attendees"] = [
            {"emailAddress": {"address": email}, "type": "required"} for email in attendees]
    if location:
        event_body["location"] = {"displayName": location}
    if is_online:
        event_body["isOnlineMeeting"] = True
        event_body["onlineMeetingProvider"] = "teams"

    result = await graph_request(
        method="POST",
        path="/events",
        user_email=user_email,
        json_body=event_body
    )

    return {
        "id": result.get("id"),
        "subject": result.get("subject"),
        "start": result.get("start"),
        "end": result.get("end"),
        "webLink": result.get("webLink"),
        "onlineMeetingURL": result.get("onlineMeeting",{}).get("joinUrl") if is_online else None,
    }

async def list_calendar_events(
    start_time:str,
    end_time:str,
    user_email:str | None = None,
    top:int = 50
) -> dict:
    """
    M365 캘린더에서 일정(이벤트) 목록을 조회합니다.
    
    Args:
        start_time: 시작 시간 (ISO 8601 포맷, 예: "2024-01-15T10:00:00")
        end_time: 종료 시간 (ISO 8601 포맷)
        user_email: 사용자 이메일 (없으면 기본값 사용)
        top: 조회할 최대 이벤트 수
    Returns:
        조회된 이벤트 목록    
    """
    path =(
        f"/calendarView"
        f"?startDateTime={start_time}"
        f"&endDateTime={end_time}"
        f"&$top={top}"
        f"&orderby=start/dateTime"
        f"&select=id,subject,start,end,location,organizerwebLink,onlineMeeting"
    )
    
    result = await graph_request(
        method="GET",
        path=path,
        user_email=user_email,
    )
    return [
        {
            "id": event.get("id"),
            "subject": event.get("subject"),
            "start": event.get("start"),
            "end": event.get("end"),
            "location": event.get("location"),
            "webLink": event.get("webLink"),
            "onlineMeetingURL": event.get("onlineMeeting",{}).get("joinUrl") if event.get("isOnlineMeeting") else None,
        }
        for event in result.get("value",[])
    ]