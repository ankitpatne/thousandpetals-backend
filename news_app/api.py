from ninja import Router, File
from .models import News
from typing import List, Optional
from pydantic import BaseModel
from google import genai
import os
from ninja.files import UploadedFile
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# load the environment variables
from dotenv import load_dotenv
load_dotenv()

router = Router()

class NewsSchema(BaseModel):
    title: str
    content: str
    tags: Optional[str] = None
    category: Optional[str] = None
    ai_generated_summary: Optional[str] = None
    ai_generated_tags: Optional[str] = None

@router.get("/")
def list_news(request):
    news_list = News.objects.all()
    return [
        {
            "id": news.id, # type: ignore
            "title": news.title,
            "content": news.content,
            "tags": news.tags,
            "category": news.category,
            "ai_generated_summary": news.ai_generated_summary,
            "ai_generated_tags": news.ai_generated_tags,
            "public_s3_image_url": news.public_s3_image_url,
            "published_date": news.published_date,
        }
        for news in news_list
    ]

@router.get("/{news_id}")
def get_news(request, news_id: int):
    try:
        news = News.objects.get(id=news_id)
        return {
            "id": news.id, # type: ignore
            "title": news.title,
            "content": news.content,
            "tags": news.tags,
            "category": news.category,
            "ai_generated_summary": news.ai_generated_summary,
            "ai_generated_tags": news.ai_generated_tags,
            "public_s3_image_url": news.public_s3_image_url,
            "published_date": news.published_date,
        }
    except News.DoesNotExist:
        return {"error": "News not found"}, 404

@router.post("/")
def create_news(request, news: NewsSchema, image: UploadedFile):
    news_obj = News.objects.create(
        title=news.title,
        content=news.content,
        tags=news.tags,
        category=news.category,
    )
    if image:
        news_obj.image.save(image.name, image)
    # Generate AI summary and tags
    if news_obj.content:
        try:
            client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))
            response_summary = client.models.generate_content(
                model="gemini-2.0-flash",
                contents="Generate a summary of the following content: " + news_obj.content,
            )
            news_obj.ai_generated_summary = response_summary.text
            response_tags = client.models.generate_content(
                model="gemini-2.0-flash",
                contents="Generate comma-separated tags for the following content, give directly the tags without any explanation: " + news_obj.content,
            )
            news_obj.ai_generated_tags = response_tags.text
            news_obj.save()

        except Exception as e:
            print(f"Error generating summary: {e}")
    return {
        "id": news_obj.id, # type: ignore
        "title": news_obj.title,
        "content": news_obj.content,
        "tags": news_obj.tags,
        "category": news_obj.category,
        "ai_generated_summary": news_obj.ai_generated_summary,
        "ai_generated_tags": news_obj.ai_generated_tags,
    }


@csrf_exempt
def contact_form(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get("name")
            email = data.get("email")
            subject = data.get("subject")
            message = data.get("message")

            # Compose the email
            email_subject = f"New Contact Form Submission: {subject}"
            email_message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

            # Send the email
            send_mail(
                email_subject,
                email_message,
                os.getenv("EMAIL_HOST_USER"),
                [os.getenv("EMAIL_HOST_USER") or ""],
                fail_silently=False,
            )

            return JsonResponse({"message": "Email sent successfully!"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=400)