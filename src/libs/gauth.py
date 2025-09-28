import httpx
import env
from models.user_model import User, Subscriber
from google.auth import jwt
from dto.user_dto import GoogleAuthDto
from fastapi import HTTPException, BackgroundTasks
from google.oauth2 import id_token
from services.auth_service import JwtService
from .email_service.email import EmailService
from .email_service.templates import signup_message


email_service = EmailService()


class HTTPXTransport:
    async def request(self, method, url, **kwargs):
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, **kwargs)
            return response

import httpx
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

async def verify_google_token(token: str):
    try:
        request = google_requests.Request()
        idinfo = id_token.verify_oauth2_token(
            token,
            request,
            audience=env.CLIENT_ID
        )
        
        if not idinfo.get("email_verified"):
            raise HTTPException(status_code=400, detail="Email not verified by Google")
            
        return idinfo
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid Google token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying token: {str(e)}")

class OAuthService:
    @staticmethod
    async def google_auth(data: GoogleAuthDto, task: BackgroundTasks):
        if not data.access_token:
            raise HTTPException(status_code=400, detail="Access token is required")
        
        try:
            idinfo = await verify_google_token(data.access_token)
            email = idinfo.get("email")
            first_name = idinfo.get("given_name")
            last_name = idinfo.get("family_name")
            username = idinfo.get("name") or data.username
            if not email:
                raise HTTPException(status_code=400, detail="Email not found in token")
            user = await User.get_or_none(email=email)
            if user and not user.password:
                data = str(user.id)
                tokens = await JwtService.generate_tokens(data)
                return {
                    "access_token": tokens["access_token"],
                    "refresh_token": tokens["refresh_token"],
                    "user_info": {
                        "email": user.email,
                        "username": user.username
                    }
                }

            user = await User.create(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password="",
                is_verified=True
            )
            

            await user.save()

            await Subscriber.get_or_create(email=user.email)
            data = {"id": str(user.id)}
            tokens = await JwtService.generate_tokens(data)
            content = signup_message(username=user.username)
            task.add_task(
                email_service.send_email,
                to_emails=[user.email],
                subject="Welcome!",
                body=content
            )
            return {
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "user_info": {
                    "email": user.email,
                    "username": user.username
                }
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )