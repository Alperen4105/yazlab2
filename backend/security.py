from werkzeug.security import check_password_hash, generate_password_hash


def hash_password(raw_password: str) -> str:
    return generate_password_hash(raw_password.strip())


def verify_password(stored_hash: str, candidate: str) -> bool:
    if not stored_hash or not candidate:
        return False
    return check_password_hash(stored_hash, candidate.strip())

