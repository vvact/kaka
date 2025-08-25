from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route("/deploy", methods=["POST"])
def deploy():
    # Run your deploy script
    subprocess.call(["/kaka/deploy.sh"])
    return "Deployment triggered!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
