from fastapi import FastAPI, File, UploadFile
import boto3
import os

app = FastAPI()

# Initialize Rekognition client
rekognition = boto3.client(
    "rekognition",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
)

@app.post("/detect-faces/")
async def detect_faces(file: UploadFile = File(...)):
    image_bytes = await file.read()

    response = rekognition.detect_faces(
        Image={"Bytes": image_bytes},
        Attributes=["ALL"]
    )

    face_data = []
    for faceDetail in response.get("FaceDetails", []):
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

    return {"faces": face_data}
