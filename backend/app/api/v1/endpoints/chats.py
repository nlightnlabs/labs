"""Chat endpoints for AI conversation."""

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.dependencies import get_current_user, CurrentUser
from app.utilities.claude import ask, GeneralQueryModel
from app.utilities.postgres_db import insert_records, update_records, delete_records, DbQueryModel
from app.config import get_tenant_state

router = APIRouter()

# In-memory storage for sessions and messages (replace with database in production)
chat_sessions: dict = {}
chat_messages: dict = {}


async def generate_topic_title(content: str) -> str:
    """Generate a topic title from the first user message using LLM."""
    try:
        prompt = f"""Based on the following message, generate a concise topic title in less than 10 words.
Only respond with the title, nothing else. No quotes, no explanation.

Message: {content}"""

        query = GeneralQueryModel(
            prompt=prompt,
            model="sonnet_3_5_v2",
            temperature=0.3,
            max_tokens=50
        )

        title = ask(query)
        # Clean up and truncate if needed
        title = title.strip().strip('"\'')
        words = title.split()
        if len(words) > 10:
            title = ' '.join(words[:10])
        return title
    except Exception as e:
        print(f"Error generating topic title: {e}")
        return content[:50] + ('...' if len(content) > 50 else '')


async def save_chat_to_database(
    session_id: str,
    username: str,
    user_first_name: str,
    user_last_name: str,
    topic: str,
    messages: list,
    is_new: bool = False
):
    """Save or update chat in the PostgreSQL database."""
    try:
        # Get tenant database name directly from tenant state
        state = get_tenant_state()
        db_name = state.DEFAULTDB
        db_host = state.DBHOST

        # Debug: Print full tenant state
        print(f"[CHAT DEBUG] Tenant state initialized: {state.is_initialized}")
        print(f"[CHAT DEBUG] Tenant name: {state.TENANT_NAME}")
        print(f"[CHAT DEBUG] db_name (DEFAULTDB): {db_name}")
        print(f"[CHAT DEBUG] db_host: {db_host}")
        print(f"[CHAT DEBUG] Full config: {state.config.to_dict()}")

        # Validate that tenant is properly configured
        if not state.is_initialized:
            print(f"[CHAT WARNING] Tenant not initialized! Using default config.")
        if db_name == "base":
            print(f"[CHAT WARNING] db_name is 'base' - this might indicate tenant config issue!")

        if is_new:
            # Insert new record
            record = {
                "id": session_id,
                "username": username,
                "user_first_name": user_first_name,
                "user_last_name": user_last_name,
                "topic": topic,
                "messages": messages,
                "status": "active",
                "stage": "in_progress"
            }
            request = DbQueryModel(
                db_name=db_name,
                db_schema="data",
                table_name="chats",
                records=[record]
            )
            result = await insert_records(request)
            print(f"[CHAT] Chat saved: {result}")
        else:
            # Update existing record
            record = {
                "id": session_id,
                "username": username,
                "user_first_name": user_first_name,
                "user_last_name": user_last_name,
                "topic": topic,
                "messages": messages,
                "status": "active",
                "stage": "in_progress"
            }
            request = DbQueryModel(
                db_name=db_name,
                db_schema="data",
                table_name="chats",
                records=[record]
            )
            result = await update_records(request)
            print(f"[CHAT] Chat updated: {result}")

        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[CHAT] Error saving chat: {e}")
        return None


async def delete_chat_from_database(session_id: str):
    """Delete a chat from the PostgreSQL database."""
    try:
        # Get tenant database name directly from tenant state
        state = get_tenant_state()
        db_name = state.DEFAULTDB
        print(f"[CHAT] Deleting from database: {db_name}")

        request = DbQueryModel(
            db_name=db_name,
            db_schema="data",
            table_name="chats",
            records=[{"id": session_id}]
        )
        result = await delete_records(request)
        print(f"[CHAT] Chat deleted: {result}")
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[CHAT] Error deleting chat: {e}")
        return None


class CreateSessionRequest(BaseModel):
    title: Optional[str] = None


class UpdateSessionRequest(BaseModel):
    title: Optional[str] = None


class SendMessageRequest(BaseModel):
    content: str


class ChatSession(BaseModel):
    id: str
    title: str
    user_id: str
    created_at: str
    updated_at: str


class ChatMessage(BaseModel):
    id: str
    session_id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str


class SendMessageResponse(BaseModel):
    id: str
    user_message_id: str
    content: str
    timestamp: str


def api_response(data, success=True, error=None):
    """Standard API response format."""
    return {
        "success": success,
        "data": data,
        "error": error,
    }


@router.get("/sessions")
async def get_sessions(current_user: CurrentUser = Depends(get_current_user)):
    """Get all chat sessions for the current user."""
    user_id = current_user.id

    user_sessions = [
        session for session in chat_sessions.values()
        if session["user_id"] == user_id
    ]

    # Sort by updated_at descending
    user_sessions.sort(key=lambda x: x["updated_at"], reverse=True)

    return api_response(user_sessions)


@router.post("/sessions")
async def create_session(
    request: CreateSessionRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Create a new chat session."""
    user_id = current_user.id

    session_id = str(uuid4())
    now = datetime.utcnow().isoformat()

    session = {
        "id": session_id,
        "title": request.title or "New Chat",
        "user_id": user_id,
        "created_at": now,
        "updated_at": now,
    }

    chat_sessions[session_id] = session
    chat_messages[session_id] = []

    return api_response(session)


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get a specific chat session."""
    user_id = current_user.id

    session = chat_sessions.get(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if session["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this session"
        )

    return api_response(session)


@router.put("/sessions/{session_id}")
async def update_session(
    session_id: str,
    request: UpdateSessionRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Update a chat session (e.g., rename)."""
    user_id = current_user.id

    session = chat_sessions.get(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if session["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this session"
        )

    if request.title:
        session["title"] = request.title

    session["updated_at"] = datetime.utcnow().isoformat()
    chat_sessions[session_id] = session

    return api_response(session)


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Delete a chat session."""
    user_id = current_user.id

    session = chat_sessions.get(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if session["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this session"
        )

    # Delete from in-memory storage
    del chat_sessions[session_id]
    if session_id in chat_messages:
        del chat_messages[session_id]

    # Delete from database
    await delete_chat_from_database(session_id)

    return api_response({"message": "Session deleted successfully"})


@router.get("/sessions/{session_id}/messages")
async def get_messages(
    session_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get all messages for a chat session."""
    user_id = current_user.id

    session = chat_sessions.get(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if session["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this session"
        )

    messages = chat_messages.get(session_id, [])

    return api_response(messages)


@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: str,
    request: SendMessageRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Send a message and get AI response."""
    user_id = current_user.id

    session = chat_sessions.get(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if session["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this session"
        )

    now = datetime.utcnow().isoformat()

    # Check if this is the first message in the session
    is_first_message = session_id not in chat_messages or len(chat_messages.get(session_id, [])) == 0

    # Create user message
    user_message_id = str(uuid4())
    user_message = {
        "id": user_message_id,
        "session_id": session_id,
        "role": "user",
        "content": request.content,
        "timestamp": now,
    }

    if session_id not in chat_messages:
        chat_messages[session_id] = []

    chat_messages[session_id].append(user_message)

    # Build conversation history for context
    conversation_history = []
    for msg in chat_messages[session_id]:
        conversation_history.append(f"{msg['role'].capitalize()}: {msg['content']}")

    # Create prompt with conversation history
    system_prompt = """You are a helpful AI assistant. Be concise, informative, and friendly in your responses.
If you don't know something, say so. Always aim to be helpful while being honest about limitations."""

    full_prompt = f"""{system_prompt}

Conversation history:
{chr(10).join(conversation_history)}

Please respond to the user's latest message."""

    try:
        # Call Claude API
        query = GeneralQueryModel(
            prompt=full_prompt,
            model="sonnet_3_5_v2",
            temperature=0.7,
            max_tokens=2000
        )

        ai_response = ask(query)

        # Create assistant message
        assistant_message_id = str(uuid4())
        assistant_timestamp = datetime.utcnow().isoformat()
        assistant_message = {
            "id": assistant_message_id,
            "session_id": session_id,
            "role": "assistant",
            "content": ai_response,
            "timestamp": assistant_timestamp,
        }

        chat_messages[session_id].append(assistant_message)

        # Update session timestamp
        session["updated_at"] = assistant_timestamp
        chat_sessions[session_id] = session

        # Get user info for database storage
        username = getattr(current_user, 'username', current_user.email)
        user_first_name = getattr(current_user, 'first_name', '')
        user_last_name = getattr(current_user, 'last_name', '')

        # Generate topic title for first message, otherwise use existing session title
        if is_first_message:
            topic = await generate_topic_title(request.content)
            # Update session title with generated topic
            session["title"] = topic
            chat_sessions[session_id] = session
        else:
            topic = session.get("title", "Untitled Chat")

        # Prepare messages for database storage (JSONB format)
        messages_for_db = [
            {
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": msg["timestamp"]
            }
            for msg in chat_messages[session_id]
        ]

        # Save to database
        await save_chat_to_database(
            session_id=session_id,
            username=username,
            user_first_name=user_first_name,
            user_last_name=user_last_name,
            topic=topic,
            messages=messages_for_db,
            is_new=is_first_message
        )

        return api_response({
            "id": assistant_message_id,
            "user_message_id": user_message_id,
            "content": ai_response,
            "timestamp": assistant_timestamp,
            "topic": topic,
            "is_first_message": is_first_message,
        })

    except Exception as e:
        print(f"Error calling Claude API: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get AI response: {str(e)}"
        )
