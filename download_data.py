"""
Download METR-LA and PEMS-BAY traffic datasets
"""
import requests
import os
import zipfile

def download_file(url, output_path):
    """Download a file from URL"""
    print(f"Downloading to {output_path}...")
    
    try:
        # Use headers to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        
        # Get file size
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # Show progress
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\rProgress: {percent:.1f}%", end='', flush=True)
        
        print(f"\n✅ Downloaded: {output_path}")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def main():
    """Download datasets"""
    
    os.makedirs('data/raw', exist_ok=True)
    
    print("=" * 60)
    print("DOWNLOADING TRAFFIC DATASETS")
    print("=" * 60)
    
    # Alternative download links
    datasets = {
        'metr-la.h5': 'https://drive.google.com/uc?export=download&id=1pAGRfzMx6K9WWsfDcD1NMbIif0T0saFC',
        'pems-bay.h5': 'https://drive.google.com/uc?export=download&id=1wD-mHlqAb2mtHOe_68fZvDh1LpDegMMq'
    }
    
    for filename, url in datasets.items():
        output_path = f"data/raw/{filename}"
        
        if os.path.exists(output_path):
            print(f"\n✓ {output_path} already exists")
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"  Size: {size_mb:.2f} MB")
        else:
            print(f"\nDownloading {filename}...")
            download_file(url, output_path)
    
    print("\n" + "=" * 60)
    print("✅ DOWNLOAD COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    main()