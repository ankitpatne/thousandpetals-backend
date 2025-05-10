from django.db import models
import os
import uuid
from google import genai
from dotenv import load_dotenv
load_dotenv()

def upload_to_news_images(instance, filename):
    # Generate a unique UUID for the file name
    ext = filename.split('.')[-1]  # Get the file extension
    unique_filename = f"{uuid.uuid4()}.{ext}"  # Create a unique file name
    return os.path.join("news_images/", unique_filename)


class News(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=upload_to_news_images, blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True, null=True)  # Comma-separated tags
    category = models.CharField(max_length=100, blank=True, null=True)
    ai_generated_summary = models.TextField(blank=True, null=True)
    ai_generated_tags = models.CharField(max_length=255, blank=True, null=True)  # Comma-separated tags
    public_s3_image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title
    
    # @property
    # def image_url(self):
    #     if self.image:
    #         return f"https://{os.getenv('AWS_STORAGE_BUCKET_NAME')}.s3.{os.getenv('AWS_S3_REGION_NAME')}.amazonaws.com/news_images/{self.image.name}"
    #     return None
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            self.public_s3_image_url = f"https://{os.getenv('AWS_STORAGE_BUCKET_NAME')}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{self.image.name}"
            super().save(update_fields=['public_s3_image_url'])

        if self.content and not self.ai_generated_summary and not self.ai_generated_tags:
            try:
                client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))
                
                # Generate AI summary
                response_summary = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents="Generate a summary of the following content, give directly the summary without any explanation and without any bold text: " + self.content,
                )
                self.ai_generated_summary = response_summary.text

                # Generate AI tags
                response_tags = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents="Generate comma-separated tags for the following content, give directly the tags without any explanation: " + self.content,
                )
                self.ai_generated_tags = response_tags.text

                # Save the updated fields
                super().save(update_fields=['ai_generated_summary', 'ai_generated_tags'])

            except Exception as e:
                print(f"Error generating AI summary or tags: {e}")