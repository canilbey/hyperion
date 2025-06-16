from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.file_parsing.parser import FileParsingService
from typing import List

router = APIRouter()
file_parser = FileParsingService()

@router.post("/parse", response_model=List[str])
def parse_file(file: UploadFile = File(...)):
    try:
        # Dosyayı geçici olarak kaydet
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(file.file.read())
        elements = file_parser.parse(temp_path)
        # Sadece text döndür (örnek)
        texts = [getattr(el, 'text', None) or el.get('text', None) for el in elements]
        return texts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 