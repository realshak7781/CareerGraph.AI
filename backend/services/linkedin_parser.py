import zipfile
import io
import csv

def _get_reader_skipping_notes(text_stream):
    """
    LinkedIn CSV exports often start with 3 lines of notes before the actual header.
    This helper skips lines until it finds a valid header row.
    """
    # Read lines until we find the actual headers (which usually contain 'First Name' or similar)
    lines = []
    for line in text_stream:
        lines.append(line)
        if "First Name" in line or "Company" in line or "Title" in line or "Position" in line:
            break
            
    # Now create a DictReader from the rest of the stream, prepending the found header
    if lines:
        header_line = lines[-1]
        # Yield the header line then the rest of the stream
        def stream_generator():
            yield header_line
            for r in text_stream:
                yield r
        return csv.DictReader(stream_generator())
    return csv.DictReader([])

def parse_linkedin_zip(zip_bytes: bytes) -> dict:
    result = {
        "connections": [],
        "positions": [],
        "profile": [],
        "education": []
    }
    
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        file_list = archive.namelist()
        
        if "Connections.csv" in file_list:
            with archive.open("Connections.csv") as f:
                text_stream = io.TextIOWrapper(f, encoding='utf-8-sig', newline='')
                reader = _get_reader_skipping_notes(text_stream)
                for row in reader:
                    if any(row.values()):
                        result["connections"].append(row)
                        
        if "Positions.csv" in file_list:
            with archive.open("Positions.csv") as f:
                text_stream = io.TextIOWrapper(f, encoding='utf-8-sig', newline='')
                reader = _get_reader_skipping_notes(text_stream)
                for row in reader:
                    if any(row.values()):
                        result["positions"].append(row)

        if "Profile.csv" in file_list:
            with archive.open("Profile.csv") as f:
                text_stream = io.TextIOWrapper(f, encoding='utf-8-sig', newline='')
                reader = _get_reader_skipping_notes(text_stream)
                for row in reader:
                    if any(row.values()):
                        result["profile"].append(row)

        if "Education.csv" in file_list:
            with archive.open("Education.csv") as f:
                text_stream = io.TextIOWrapper(f, encoding='utf-8-sig', newline='')
                reader = _get_reader_skipping_notes(text_stream)
                for row in reader:
                    if any(row.values()):
                        result["education"].append(row)
                        
    return result
