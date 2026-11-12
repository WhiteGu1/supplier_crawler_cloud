# -*- coding: utf-8 -*-
"""
scripts/auth_gdrive_oauth.py
Interactive local helper to obtain Google Drive API OAuth2 Refresh Token (free, no credit card needed).

Prerequisites (one-time in Google Cloud Console):
1. Open https://console.cloud.google.com/apis/library/drive.googleapis.com and enable Google Drive API.
2. Open OAuth consent screen -> External -> Add your Google email to "Test users" -> Save.
   (Wait: keep app status as Testing, or publish, and note Testing tokens expire in 7 days UNLESS published as Production / In-production Web/Desktop app; recommend clicking "PUBLISH APP" under Audience -> Publishing status so refresh_token never expires in 7 days!)
3. Credentials -> Create Credentials -> OAuth client ID -> Application type: "Desktop app" -> Download JSON.
4. Run:
     pip install google-auth-oauthlib
     python scripts/auth_gdrive_oauth.py --client-secret path\\to\\client_secret.json
"""
import argparse
import glob
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCOPES = ["https://www.googleapis.com/auth/drive"]


def find_client_secret(explicit_path: str = "") -> str:
    if explicit_path:
        if not os.path.isfile(explicit_path):
            raise FileNotFoundError(f"Client secret JSON not found: {explicit_path}")
        return explicit_path

    candidates = []
    for folder in (".", os.path.expanduser("~/Downloads")):
        candidates.extend(glob.glob(os.path.join(folder, "client_secret*.json")))
    if not candidates:
        raise FileNotFoundError(
            "No client_secret*.json found. Pass --client-secret path\\to\\client_secret.json"
        )
    candidates.sort(key=os.path.getmtime, reverse=True)
    return candidates[0]


def main():
    parser = argparse.ArgumentParser(description="Generate GDRIVE_REFRESH_TOKEN for GitHub Actions")
    parser.add_argument("--client-secret", default="", help="Path to Google OAuth client_secret_*.json")
    parser.add_argument("--write-env", action="store_true", help="Write credentials into local .env file")
    args = parser.parse_args()

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("Missing package: google-auth-oauthlib")
        print("Install with: pip install google-auth-oauthlib google-api-python-client")
        sys.exit(1)

    secret_file = find_client_secret(args.client_secret)
    print(f"[OAuth] Using client secret: {secret_file}")

    flow = InstalledAppFlow.from_client_secrets_file(secret_file, SCOPES)
    creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

    if not creds.refresh_token:
        print("[ERROR] Google did not return a refresh_token. Revoke app access at https://myaccount.google.com/permissions and retry with prompt='consent'.")
        sys.exit(1)

    print("\n=== Copy these 3 secrets to GitHub Repository Secrets ===")
    print(f"GDRIVE_CLIENT_ID={creds.client_id}")
    print(f"GDRIVE_CLIENT_SECRET={creds.client_secret}")
    print(f"GDRIVE_REFRESH_TOKEN={creds.refresh_token}")

    if args.write_env:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env_path = os.path.join(root_dir, ".env")
        existing = {}
        if os.path.isfile(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line and not line.strip().startswith("#"):
                        k, v = line.strip().split("=", 1)
                        existing[k.strip()] = v.strip()
        existing["GDRIVE_CLIENT_ID"] = creds.client_id
        existing["GDRIVE_CLIENT_SECRET"] = creds.client_secret
        existing["GDRIVE_REFRESH_TOKEN"] = creds.refresh_token
        with open(env_path, "w", encoding="utf-8") as f:
            for k, v in existing.items():
                f.write(f"{k}={v}\n")
        print(f"\n[OK] Saved to {env_path} (ignored by .gitignore)")


if __name__ == "__main__":
    main()
