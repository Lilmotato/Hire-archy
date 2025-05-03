import sys
import asyncio
import logging
from firebase_admin import auth, credentials, initialize_app

# Setup logger
logger = logging.getLogger("add_recruiter")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# ✅ Initialize Firebase app
try:
    # Load credentials from environment variable or local file path
    cred = credentials.Certificate("src\config\serviceAccountKey.json")
    initialize_app(cred)
except Exception as e:
    logger.error(f"🔥 Failed to initialize Firebase Admin SDK: {e}")
    sys.exit(1)

async def create_recruiter(email: str, password: str):
    try:
        user = auth.create_user(email=email, password=password)
        logger.info(f"✅ Firebase user created with UID: {user.uid}")

        auth.set_custom_user_claims(user.uid, {"role": "recruiter"})
        logger.info("✅ Custom claims set: recruiter")

        print(f"\nRecruiter created successfully ✅\nUID: {user.uid}")
        return user.uid
    except Exception as e:
        logger.error(f"🔥 Failed to create recruiter: {e}")
        print(f"\n❌ Failed to create recruiter: {e}")
        sys.exit(1)

if __name__ == "__main__":
    email = input("Enter recruiter email: ").strip()
    password = input("Enter recruiter password: ").strip()

    if not email or not password:
        print("❗ Email and password must not be empty.")
        sys.exit(1)

    asyncio.run(create_recruiter(email, password))
