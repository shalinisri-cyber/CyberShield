from flask import Flask, render_template, request, jsonify
from password_checker import analyze_password
from integrity import calculate_sha512
from crypto_utils import encrypt_file, decrypt_file
import os

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze-password", methods=["POST"])
def password_analysis():
    data = request.get_json()

    password = data.get("password", "")

    result = analyze_password(password)

    return jsonify(result)


@app.route("/hash-file", methods=["POST"])
def hash_file():
    if "file" not in request.files:
        return jsonify({"error": "No file selected."}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    temp_path = "temp_" + file.filename
    file.save(temp_path)

    try:
        file_hash = calculate_sha512(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return jsonify({
        "filename": file.filename,
        "sha512": file_hash
    })


@app.route("/encrypt", methods=["POST"])
def encrypt():
    if "file" not in request.files:
        return jsonify({"error": "No file selected."}), 400

    file = request.files["file"]
    password = request.form.get("password", "")

    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not password:
        return jsonify({"error": "Password is required."}), 400

    temp_path = "temp_" + file.filename
    file.save(temp_path)

    try:
        encrypted_path = encrypt_file(temp_path, password)

        with open(encrypted_path, "rb") as encrypted_file:
            encrypted_data = encrypted_file.read()

    finally:
        for path in [temp_path, temp_path + ".encrypted"]:
            if os.path.exists(path):
                os.remove(path)

    from flask import Response

    response = Response(
        encrypted_data,
        mimetype="application/octet-stream"
    )

    response.headers["Content-Disposition"] = (
        f'attachment; filename="{file.filename}.encrypted"'
    )

    return response


@app.route("/decrypt", methods=["POST"])
def decrypt():
    if "file" not in request.files:
        return jsonify({"error": "No encrypted file selected."}), 400

    file = request.files["file"]
    password = request.form.get("password", "")

    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not password:
        return jsonify({"error": "Password is required."}), 400

    temp_path = "temp_" + file.filename
    file.save(temp_path)

    try:
        decrypted_path = decrypt_file(temp_path, password)

        with open(decrypted_path, "rb") as decrypted_file:
            decrypted_data = decrypted_file.read()

    except Exception:
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return jsonify({
            "error": "Decryption failed. Check the password or encrypted file."
        }), 400

    finally:
        for path in [temp_path, temp_path[:-10] if temp_path.endswith(".encrypted") else temp_path + ".decrypted"]:
            if os.path.exists(path):
                os.remove(path)

    original_filename = file.filename

    if original_filename.endswith(".encrypted"):
        original_filename = original_filename[:-10]

    from flask import Response

    response = Response(
        decrypted_data,
        mimetype="application/octet-stream"
    )

    response.headers["Content-Disposition"] = (
        f'attachment; filename="{original_filename}"'
    )

    return response


if __name__ == "__main__":
    app.run(debug=True)