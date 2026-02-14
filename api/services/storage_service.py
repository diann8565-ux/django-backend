
import base64
import hashlib
import hmac
import time
import requests
from urllib.parse import urlparse

class StorageService:
    """
    Service to handle interactions with external storage providers.
    Currently a stub as actual upload logic happens on client-side (signed URLs)
    or via direct upload, but this service can generate signatures.
    """
    
    @staticmethod
    def get_upload_signature(credential, file_name, file_type):
        """
        Generates a signed upload URL or signature for the provider.
        """
        if credential.provider == 'imagekit':
            return StorageService._generate_imagekit_signature(credential)
        elif credential.provider == 'cloudinary':
            return StorageService._generate_cloudinary_signature(credential)
        return None

    @staticmethod
    def _generate_imagekit_signature(credential):
        return {"token": "not_required", "expire": int(time.time()) + 600, "signature": "not_required"}

    @staticmethod
    def _generate_cloudinary_signature(credential):
        ts = int(time.time())
        to_sign = f"timestamp={ts}"
        signature = hashlib.sha1((to_sign + credential.private_key_encrypted).encode()).hexdigest()
        return {"signature": signature, "timestamp": ts}

    @staticmethod
    def upload_imagekit(credential, file_bytes, file_name):
        auth = base64.b64encode((credential.private_key_encrypted + ":").encode()).decode()
        headers = {"Authorization": f"Basic {auth}"}
        files = {
            "file": (file_name, file_bytes),
            "fileName": (None, file_name),
        }
        url = "https://upload.imagekit.io/api/v1/files/upload"
        resp = requests.post(url, files=files, headers=headers, timeout=60)
        if resp.status_code == 200:
            data = resp.json()
            return {"url": data.get("url"), "file_id": data.get("fileId")}
        raise requests.RequestException(f"ImageKit upload failed: {resp.status_code} {resp.text}")

    @staticmethod
    def upload_cloudinary(credential, file_bytes, file_name):
        parsed = urlparse(credential.url_endpoint or "")
        path = parsed.path.strip("/")
        cloud_name = ""
        # Support both api and res endpoints
        # api.cloudinary.com/v1_1/<cloud_name>/...
        if path.startswith("v1_1/"):
            segs = path.split("/")
            if len(segs) >= 2:
                cloud_name = segs[1]
        # res.cloudinary.com/<cloud_name>/...
        if not cloud_name:
            segs = path.split("/")
            if len(segs) >= 1 and segs[0] and segs[0] != "v1_1":
                cloud_name = segs[0]
        # Fallback to bucket_name as cloud_name
        if not cloud_name:
            cloud_name = credential.bucket_name or ""
        if not cloud_name:
            raise requests.RequestException("Cloudinary upload failed: missing cloud_name in url_endpoint or bucket_name")
        ts = int(time.time())
        to_sign = f"public_id={file_name}&timestamp={ts}"
        signature = hashlib.sha1((to_sign + credential.private_key_encrypted).encode()).hexdigest()
        url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"
        data = {
            "api_key": credential.public_key,
            "timestamp": ts,
            "signature": signature,
            "public_id": file_name,
        }
        files = {"file": (file_name, file_bytes)}
        resp = requests.post(url, data=data, files=files, timeout=60)
        if resp.status_code == 200:
            j = resp.json()
            return {"url": j.get("secure_url") or j.get("url"), "file_id": j.get("public_id")}
        raise requests.RequestException(f"Cloudinary upload failed: {resp.status_code} {resp.text}")
