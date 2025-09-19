import boto3
import json
import os
from PIL import Image
import io

class AWSMCPService:
    """Serviço MCP simplificado para integração com AWS"""
    
    def __init__(self):
        try:
            self.rekognition = boto3.client('rekognition', region_name='us-east-1')
            self.s3 = boto3.client('s3', region_name='us-east-1')
            self.aws_available = True
        except Exception as e:
            print(f"AWS não configurado: {e}")
            self.aws_available = False
    
    def detect_runner_numbers(self, image_path):
        """Detecta números de peito usando AWS Rekognition"""
        if not self.aws_available:
            return {"error": "AWS não configurado", "numbers": []}
        
        try:
            with open(image_path, 'rb') as image_file:
                image_bytes = image_file.read()
            
            response = self.rekognition.detect_text(
                Image={'Bytes': image_bytes}
            )
            
            numbers = []
            for text in response['TextDetections']:
                if text['Type'] == 'LINE' and text['DetectedText'].isdigit():
                    if text['Confidence'] > 80:  # Confiança mínima
                        numbers.append({
                            'number': text['DetectedText'],
                            'confidence': round(text['Confidence'], 2)
                        })
            
            return {"success": True, "numbers": numbers}
            
        except Exception as e:
            return {"error": str(e), "numbers": []}
    
    def analyze_photo_quality(self, image_path):
        """Analisa qualidade da foto"""
        if not self.aws_available:
            return {"error": "AWS não configurado", "quality_score": 0}
        
        try:
            with open(image_path, 'rb') as image_file:
                image_bytes = image_file.read()
            
            response = self.rekognition.detect_faces(
                Image={'Bytes': image_bytes},
                Attributes=['ALL']
            )
            
            quality_score = 50  # Score padrão
            if response['FaceDetails']:
                face = response['FaceDetails'][0]
                sharpness = face.get('Quality', {}).get('Sharpness', 50)
                brightness = face.get('Quality', {}).get('Brightness', 50)
                quality_score = (sharpness + brightness) / 2
            
            return {
                "success": True, 
                "quality_score": round(quality_score, 2),
                "recommendation": "Boa qualidade" if quality_score > 70 else "Qualidade baixa"
            }
            
        except Exception as e:
            return {"error": str(e), "quality_score": 0}
    
    def upload_to_s3(self, file_path, bucket_name, key=None):
        """Faz upload para S3"""
        if not self.aws_available:
            return {"error": "AWS não configurado", "url": None}
        
        try:
            if not key:
                key = f"photos/{os.path.basename(file_path)}"
            
            self.s3.upload_file(file_path, bucket_name, key)
            url = f"https://{bucket_name}.s3.amazonaws.com/{key}"
            
            return {"success": True, "url": url, "key": key}
            
        except Exception as e:
            return {"error": str(e), "url": None}
    
    def get_basic_image_info(self, image_path):
        """Análise básica da imagem sem AWS"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                format_type = img.format
                file_size = os.path.getsize(image_path)
                
                # Score básico baseado em resolução
                basic_score = min(100, (width * height) / 10000)
                
                return {
                    "success": True,
                    "width": width,
                    "height": height,
                    "format": format_type,
                    "file_size": file_size,
                    "basic_quality_score": round(basic_score, 2)
                }
        except Exception as e:
            return {"error": str(e)}

# Instância global do serviço
aws_mcp = AWSMCPService()