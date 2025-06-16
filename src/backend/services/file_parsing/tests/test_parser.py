from src.backend.services.file_parsing.parser import FileParsingService

def test_detect_file_type():
    service = FileParsingService()
    assert service.detect_file_type('example.pdf') == 'pdf'

def test_parse_empty():
    service = FileParsingService()
    assert service.parse('nonexistent.pdf') == [] 