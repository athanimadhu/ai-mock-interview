import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Request
from functools import wraps
import os

# Initialize Firebase Admin with service account
cred = credentials.Certificate(os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH'))
firebase_admin.initialize_app(cred)

async def verify_token(request: Request):
    """Verify Firebase authentication token from request headers."""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='No authentication token provided')
    
    token = auth_header.split(' ')[1]
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail=f'Invalid authentication token: {str(e)}')

def require_auth(func):
    """Decorator to require Firebase authentication for routes."""
    @wraps(func)
    async def wrapper(*args, request: Request, **kwargs):
        decoded_token = await verify_token(request)
        # Add the user_id to the request state
        request.state.user_id = decoded_token['uid']
        return await func(*args, request=request, **kwargs)
    return wrapper 