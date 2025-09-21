from flask import Blueprint, render_template, current_app
from utils.health_checks import HealthChecker

# Create blueprint for main routes
main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def index():
    """Render the main application page."""
    return render_template("index.html")

@main_bp.route("/health")
def health_check():
    """Health check endpoint."""
    try:
        config = current_app.config.get('AI_CONFIG', {})
        checker = HealthChecker(config)
        return checker.quick_health_check()
    except Exception as e:
        return {
            "status": "error", 
            "service": "AI Agent",
            "error": str(e)
        }, 500

@main_bp.route("/health/detailed")
def detailed_health_check():
    """Detailed health check endpoint."""
    try:
        config = current_app.config.get('AI_CONFIG', {})
        checker = HealthChecker(config)
        return checker.comprehensive_health_check()
    except Exception as e:
        return {
            "status": "error", 
            "service": "AI Agent",
            "error": str(e)
        }, 500