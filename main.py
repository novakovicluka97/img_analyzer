from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import boto3
import os
import requests
from botocore.exceptions import BotoCoreError, ClientError
from uuid import uuid4

app = FastAPI()

# Initialize S3 and Rekognition clients
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name="eu-north-1"
)

rekognition = boto3.client(
    "rekognition",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "eu-north-1")
)

BUCKET_NAME = "bucketforn8nimagesr8me"

class ImageUrlRequest(BaseModel):
    image_url: str

@app.post("/detect-faces/")
async def detect_faces(request: ImageUrlRequest):
    # Download the image from the provided URL
    try:
        response = requests.get(request.image_url)
        response.raise_for_status()
        image_bytes = response.content
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to download image: {e}")

    # Generate a unique filename
    filename = f"uploaded_{uuid4().hex}.jpg"

    # Upload the image to S3
    try:
        s3.put_object(Bucket=BUCKET_NAME, Key=filename, Body=image_bytes)
    except (BotoCoreError, ClientError) as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload to S3: {e}")

    # Call Rekognition on the image in S3
    try:
        rekog_response = rekognition.detect_faces(
            Image={"S3Object": {"Bucket": BUCKET_NAME, "Name": filename}},
            Attributes=["ALL"]
        )
    except (BotoCoreError, ClientError) as e:
        raise HTTPException(status_code=500, detail=f"Rekognition failed: {e}")

    face_data = []
    for faceDetail in rekog_response.get("FaceDetails", []):
        face_data.append({
            "gender": faceDetail["Gender"]["Value"],
            "age_range": {
                "low": faceDetail["AgeRange"]["Low"],
                "high": faceDetail["AgeRange"]["High"]
            },
            "emotions": sorted(
                [
                    {"type": e["Type"], "confidence": e["Confidence"]}
                    for e in faceDetail["Emotions"]
                ],
                key=lambda x: x["confidence"],
                reverse=True
            )
        })

    return {"faces": face_data, "s3_key": filename}
