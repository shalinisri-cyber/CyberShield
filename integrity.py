import hashlib


def calculate_sha512(file_path):
    sha512_hash = hashlib.sha512()

    with open(file_path, "rb") as file:
        while chunk := file.read(4096):
            sha512_hash.update(chunk)

    return sha512_hash.hexdigest()


def verify_integrity(file_path, original_hash):
    current_hash = calculate_sha512(file_path)

    if current_hash == original_hash:
        return True, "File integrity verified. The file has not been modified."
    else:
        return False, "WARNING: File has been modified!"