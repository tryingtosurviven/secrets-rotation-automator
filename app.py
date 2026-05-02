"""
Secrets Rotation Automator - Flask App with Debug Home Route
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from secret_detector import detect_secrets, find_secret_usages, classify_secret_type

DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
PORT = 5000
HOST = "0.0.0.0"
VERSION = "1.0.0"
APP_NAME = "Secrets Rotation Automator"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

app.config["JSON_SORT_KEYS"] = False
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True

def _validate_repo_path(path: str) -> bool:
    return bool(path and os.path.exists(path) and os.path.isdir(path))

def _validate_secret_value(value: str) -> bool:
    return bool(value and value.strip())

def _format_response(data: Any, status: int = 200) -> Tuple[Dict, int]:
    return data, status

def _format_error_response(error: str, message: str, status: int = 500) -> Tuple[Dict, int]:
    return {
        "error": error,
        "message": message,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }, status

def _extract_affected_services(files: List[Dict]) -> List[str]:
    services = set()

    for file_info in files:
        file_path = file_info.get("file_path", "") or file_info.get("file", "")
        lower_path = file_path.lower()

        if "auth" in lower_path:
            services.add("Authentication")
        if "payment" in lower_path:
            services.add("Payment")
        if "api" in lower_path:
            services.add("API")
        if "database" in lower_path or "db" in lower_path:
            services.add("Database")
        if "config" in lower_path:
            services.add("Configuration")
        if "k8s" in lower_path or "kubernetes" in lower_path:
            services.add("Kubernetes")
        if "docker" in lower_path:
            services.add("Docker")
        if ".github" in lower_path or "workflow" in lower_path:
            services.add("CI/CD")

    return sorted(list(services)) if services else ["Unknown"]

def _estimate_time_to_fix(locations_count: int, affected_services: List[str]) -> str:
    base_time = locations_count * 5
    service_time = len(affected_services) * 10
    total_minutes = base_time + service_time

    if total_minutes < 60:
        return f"{total_minutes} minutes"

    hours = total_minutes // 60
    minutes = total_minutes % 60
    if minutes > 0:
        return f"{hours} hour{'s' if hours > 1 else ''} {minutes} minutes"
    return f"{hours} hour{'s' if hours > 1 else ''}"

def _generate_rotation_plan_data(secret_name: str, affected_services: List[str], files: List[str]) -> Dict:
    return {
        "step_by_step_plan": [
            "Backup current configuration and affected files",
            f"Generate a new value for {secret_name}",
            "Update secret management or environment configuration",
            f"Update {len(files)} affected file(s)",
            "Deploy changes to staging and run tests",
            "Deploy safely to production",
            "Verify all affected services are healthy",
            "Revoke the old secret after verification"
        ],
        "rollback_plan": [
            "Restore previous configuration",
            "Redeploy previous known-good version",
            "Verify service recovery",
            "Investigate and retry rotation safely"
        ],
        "verification_checks": [
            "Check service health endpoints",
            "Review application logs for errors",
            "Verify integrations still work",
            "Run automated tests"
        ],
        "estimated_time": _estimate_time_to_fix(len(files), affected_services)
    }

# ----------------------------
# Home Route
# ----------------------------

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html", version=VERSION, app_name=APP_NAME)



# ----------------------------
# Web UI Routes
# ----------------------------

@app.route("/analyze-ui", methods=["POST"])
def analyze_ui():
    repo_path = request.form.get("repo_path", "").strip()
    secret_name = request.form.get("secret_name", "").strip()

    if not _validate_repo_path(repo_path):
        return render_template("results.html", error="Invalid repository path.", result=None)

    if not secret_name:
        return render_template("results.html", error="Secret name is required.", result=None)

    all_secrets = detect_secrets(repo_path)

    matching_secrets = [
        s for s in all_secrets
        if secret_name.lower() in s.get("file_path", "").lower()
        or secret_name.lower() in s.get("context", "").lower()
    ]

    files = [
        {
            "file": secret["file_path"],
            "line": secret["line_number"],
            "context": secret["context"],
            "secret_type": secret["secret_type"]
        }
        for secret in matching_secrets
    ]

    affected_services = _extract_affected_services(matching_secrets)
    time_estimate = _estimate_time_to_fix(len(matching_secrets), affected_services)
    plan_data = _generate_rotation_plan_data(secret_name, affected_services, [f["file"] for f in files])

    result = {
        "secret_name": secret_name,
        "locations_found": len(matching_secrets),
        "files": files,
        "affected_services": affected_services,
        "time_to_fix_estimate": time_estimate,
        "rotation_plan": plan_data
    }

    return render_template("results.html", error=None, result=result)

@app.route("/usages", methods=["GET", "POST"])
def usages_ui():
    if request.method == "GET":
        return render_template("usages.html", error=None, usages=None)

    repo_path = request.form.get("repo_path", "").strip()
    secret_value = request.form.get("secret_value", "").strip()

    if not _validate_repo_path(repo_path):
        return render_template("usages.html", error="Invalid repository path.", usages=None)

    if not _validate_secret_value(secret_value):
        return render_template("usages.html", error="Secret value is required.", usages=None)

    usages = find_secret_usages(repo_path, secret_value)
    return render_template("usages.html", error=None, usages=usages, secret_value=secret_value)

# ----------------------------
# API Routes
# ----------------------------

@app.route("/api/health", methods=["GET"])
def health_check():
    return _format_response({
        "status": "healthy",
        "version": VERSION,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

@app.route("/api/version", methods=["GET"])
def get_version():
    return _format_response({
        "version": VERSION,
        "name": APP_NAME,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

@app.route("/api/analyze", methods=["POST"])
def analyze_secrets():
    try:
        data = request.get_json()
        if not data:
            return _format_error_response("Bad Request", "Request body must be valid JSON", 400)

        repo_path = data.get("repo_path", ".")
        secret_name = data.get("secret_name", "")

        if not _validate_repo_path(repo_path):
            return _format_error_response("Invalid Repository Path", f"Invalid path: {repo_path}", 400)

        if not secret_name:
            return _format_error_response("Missing Secret Name", "secret_name is required", 400)

        all_secrets = detect_secrets(repo_path)

        matching_secrets = [
            s for s in all_secrets
            if secret_name.lower() in s.get("file_path", "").lower()
            or secret_name.lower() in s.get("context", "").lower()
        ]

        files = [
            {
                "file": secret["file_path"],
                "line": secret["line_number"],
                "context": secret["context"],
                "secret_type": secret["secret_type"]
            }
            for secret in matching_secrets
        ]

        affected_services = _extract_affected_services(matching_secrets)
        time_estimate = _estimate_time_to_fix(len(matching_secrets), affected_services)

        response = {
            "secret_name": secret_name,
            "locations_found": len(matching_secrets),
            "files": files,
            "affected_services": affected_services,
            "time_to_fix_estimate": time_estimate,
            "rotation_plan": _generate_rotation_plan_data(secret_name, affected_services, [f["file"] for f in files]),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        return _format_response(response)

    except Exception as e:
        logger.error(f"Error analyzing secrets: {e}", exc_info=True)
        return _format_error_response("Internal Server Error", str(e), 500)

@app.route("/api/find-secret-usages", methods=["POST"])
def find_usages_api():
    try:
        data = request.get_json()
        if not data:
            return _format_error_response("Bad Request", "Request body must be valid JSON", 400)

        repo_path = data.get("repo_path", ".")
        secret_value = data.get("secret_value", "")

        if not _validate_repo_path(repo_path):
            return _format_error_response("Invalid Repository Path", f"Invalid path: {repo_path}", 400)

        if not _validate_secret_value(secret_value):
            return _format_error_response("Invalid Secret Value", "secret_value cannot be empty", 400)

        usages = find_secret_usages(repo_path, secret_value)

        response = {
            "secret_value": secret_value,
            "locations_found": len(usages),
            "locations": usages,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        return _format_response(response)

    except Exception as e:
        logger.error(f"Error finding secret usages: {e}", exc_info=True)
        return _format_error_response("Internal Server Error", str(e), 500)

@app.route("/api/classify-secret", methods=["POST"])
def classify_secret_api():
    try:
        data = request.get_json()
        if not data:
            return _format_error_response("Bad Request", "Request body must be valid JSON", 400)

        secret_value = data.get("secret_value", "")
        if not _validate_secret_value(secret_value):
            return _format_error_response("Invalid Secret Value", "secret_value cannot be empty", 400)

        secret_type = classify_secret_type(secret_value)

        return _format_response({
            "secret_type": secret_type,
            "confidence": "HIGH" if secret_type != "UNKNOWN" else "LOW",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

    except Exception as e:
        logger.error(f"Error classifying secret: {e}", exc_info=True)
        return _format_error_response("Internal Server Error", str(e), 500)

@app.route("/api/generate-rotation-plan", methods=["POST"])
def generate_rotation_plan():
    try:
        data = request.get_json()
        if not data:
            return _format_error_response("Bad Request", "Request body must be valid JSON", 400)

        secret_name = data.get("secret_name", "")
        affected_services = data.get("affected_services", [])
        files = data.get("files", [])

        if not secret_name:
            return _format_error_response("Missing Secret Name", "secret_name is required", 400)

        plan_data = _generate_rotation_plan_data(secret_name, affected_services or ["Unknown"], files or [])

        return _format_response({
            "secret_name": secret_name,
            "affected_services": affected_services,
            "affected_files": files,
            **plan_data,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

    except Exception as e:
        logger.error(f"Error generating rotation plan: {e}", exc_info=True)
        return _format_error_response("Internal Server Error", str(e), 500)

@app.errorhandler(404)
def not_found(error):
    return _format_error_response("Not Found", f"The requested endpoint {request.path} does not exist", 404)

if __name__ == "__main__":
    logger.info(f"Starting {APP_NAME} v{VERSION}")
    app.run(host=HOST, port=PORT, debug=DEBUG)
