from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
import logging
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# A random secret key, replace in production
SECRET_KEY = "your-256-bit-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthToken:
    """Represents an authentication token structure"""
    
    def __init__(self, token: str, model: Optional[Dict] = None):
        self.token = token
        self.model = model or {}

class SecurityService:
    """Security service handles authentication and authorization"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a stored hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate a password hash"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Generate access token with expiration"""
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> AuthToken:
        """Decode and validate the access token"""
        try:
            decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            logger.info("Access token is valid")
            return AuthToken(token, decoded_data)
        except JWTError as e:
            logger.warning(f"Invalid access token: {str(e)}")
            return AuthToken(token, None)

    @staticmethod
    def authenticate_user(username: str, password: str, users_db: Dict[str, Dict]) -> bool:
        """Authenticate a user against the users DB"""
        if username in users_db:
            user = users_db[username]
            if SecurityService.verify_password(password, user["password"]):
                logger.info(f"User {username} authenticated successfully")
                return True
            else:
                logger.warning(f"Password mismatch for user {username}")
        else:
            logger.warning(f"User {username} not found in the database")
        return False
