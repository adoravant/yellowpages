from flask import Flask, request, jsonify
import subprocess

DEVICE_ID = "5eba6c4010bc490b953192877e48e263"

app = Flask(__name__)

@app.route("/call", methods=["POST"])
def call():
    data = request.get_json()
    phone = data.get("phone")
    if not phone:
        return jsonify({"error": "No phone provided"}), 400

    try:
        subprocess.run(
            ["kdeconnect-cli", "--device", DEVICE_ID, "--share", f"tel:{phone}"],
            check=True
        )
        return jsonify({"status": "ok"})
    except subprocess.CalledProcessError as e:
        return jsonify({
            "error": "Error ejecutando KDE Connect",
            "details": str(e)
        }), 500

if __name__ == "__main__":
    app.run(port=5000)
