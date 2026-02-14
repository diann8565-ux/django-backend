import os
import sys
import requests

API_URL = "https://django-backend-theta.vercel.app/api/external/upload"
TOKEN = os.getenv("EXTERNAL_UPLOAD_API_KEY") or "873YWEHFG478348HDS77478WDBS"

def upload(file_path: str, provider: str | None):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    files = {"file": open(file_path, "rb")}
    data = {}
    if provider:
        data["provider"] = provider
    resp = requests.post(API_URL, headers=headers, files=files, data=data, timeout=60)
    try:
        return resp.status_code, resp.json()
    except Exception:
        return resp.status_code, {"raw": resp.text}

def main():
    file_path = sys.argv[1] if len(sys.argv) > 1 else r"c:\Users\eka\Documents\GitHub\penyimpanan\gambar\1.png"
    if not os.path.isfile(file_path):
        print(f"File tidak ditemukan: {file_path}")
        sys.exit(1)

    print("=== Upload via ImageKit ===")
    code_ik, res_ik = upload(file_path, "imagekit")
    print(f"Status: {code_ik}")
    print(res_ik)

    print("\n=== Upload via Cloudinary ===")
    code_cl, res_cl = upload(file_path, "cloudinary")
    print(f"Status: {code_cl}")
    print(res_cl)

if __name__ == "__main__":
    main()
