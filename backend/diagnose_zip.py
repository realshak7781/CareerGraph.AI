import zipfile
import io
import sys

def analyze_archive(file_path: str):
    """
    Secure diagnostic function to analyze the ZIP archive in-memory
    and list its internal contents.
    """
    try:
        with open(file_path, 'rb') as f:
            zip_bytes = f.read()
        
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
            file_list = archive.namelist()
            print(f"Archive '{file_path}' successfully loaded in-memory.")
            print(f"Total files: {len(file_list)}")
            print("Files:")
            for name in file_list:
                print(f"  - {name}")
            
            # Check for expected files
            expected = ["Connections.csv", "Positions.csv", "Profile.csv", "Education.csv"]
            print("\nChecking expected files:")
            for exp in expected:
                if exp in file_list:
                    print(f"  [+] Found: {exp}")
                else:
                    print(f"  [-] Missing: {exp}")
    except Exception as e:
        print(f"Error analyzing archive: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        analyze_archive(sys.argv[1])
    else:
        print("Please provide a file path.")
