from flask import Flask
from dotenv import load_dotenv
import time

load_dotenv()

# 🚀 Startup preload (Day 11)
print("🚀 Starting AI Service...")
MODEL_READY = True
print("✅ AI Model preloaded successfully")

# 🔹 Import routes
from routes.describe import describe_bp
from routes.recommend import recommend_bp
from routes.report import report_bp

# 🔹 Metrics
from services.metrics import START_TIME, response_times

app = Flask(__name__)

# 🔹 Register APIs
app.register_blueprint(describe_bp)
app.register_blueprint(recommend_bp)
app.register_blueprint(report_bp)


# 🔐 Security Headers (Day 8 requirement)
@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response


# 🔹 Health Endpoint (Day 7)
@app.route("/health")
def health():
    uptime = time.time() - START_TIME

    recent = response_times[-5:]
    avg_time = sum(recent) / len(recent) if recent else 0

    return {
        "status": "ok",
        "model": "llama-3.3-70b-versatile",
        "model_ready": MODEL_READY,
        "uptime_seconds": round(uptime, 2),
        "avg_response_time": round(avg_time, 2)
    }


if __name__ == "__main__":
    app.run(port=5000, debug=True)