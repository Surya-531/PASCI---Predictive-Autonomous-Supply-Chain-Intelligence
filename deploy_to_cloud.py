#!/usr/bin/env python
"""
PASCI – Google Cloud Run Deployment Script
Simplifies deployment to Google Cloud Run with a single command.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """Run a shell command and return success status."""
    if description:
        print(f"\n📦 {description}")
    print(f"   $ {cmd}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0


def check_gcloud():
    """Check if gcloud CLI is installed."""
    print("🔍 Checking gcloud CLI...")
    result = subprocess.run("gcloud --version", shell=True, capture_output=True)
    if result.returncode == 0:
        print("   ✓ gcloud CLI is installed")
        return True
    else:
        print("   ✗ gcloud CLI not found")
        print("   Install from: https://cloud.google.com/sdk/docs/install")
        return False


def check_docker():
    """Check if Docker is installed."""
    print("🔍 Checking Docker...")
    result = subprocess.run("docker --version", shell=True, capture_output=True)
    if result.returncode == 0:
        print("   ✓ Docker is installed")
        return True
    else:
        print("   ℹ️  Docker not found (Cloud Run can build from source)")
        return True  # Don't fail, Cloud Run can build


def check_authentication():
    """Check if user is authenticated with gcloud."""
    print("🔍 Checking Google Cloud authentication...")
    result = subprocess.run(
        "gcloud auth list", shell=True, capture_output=True, text=True
    )
    if "*" in result.stdout:
        print("   ✓ Authenticated with Google Cloud")
        return True
    else:
        print("   ✗ Not authenticated with Google Cloud")
        print("   Run: gcloud auth login")
        return False


def get_project_id():
    """Get Google Cloud project ID."""
    result = subprocess.run(
        "gcloud config get-value project",
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def deploy_backend(project_id, gemini_key, maps_key=""):
    """Deploy backend to Cloud Run."""
    print("\n" + "=" * 60)
    print("DEPLOYING BACKEND")
    print("=" * 60)

    env_vars = f"GEMINI_API_KEY={gemini_key}"
    if maps_key:
        env_vars += f",GOOGLE_MAPS_API_KEY={maps_key}"

    cmd = f"""
gcloud run deploy pasci-api \\
  --source . \\
  --platform managed \\
  --region us-central1 \\
  --allow-unauthenticated \\
  --memory 512Mi \\
  --timeout 3600 \\
  --set-env-vars {env_vars}
"""

    if run_command(cmd.strip()):
        print("   ✓ Backend deployed successfully!")
        return True
    else:
        print("   ✗ Backend deployment failed")
        return False


def deploy_frontend(project_id, backend_url):
    """Deploy frontend to Cloud Run."""
    print("\n" + "=" * 60)
    print("DEPLOYING FRONTEND")
    print("=" * 60)

    cmd = f"""
gcloud run deploy pasci-frontend \\
  --source . \\
  --dockerfile Dockerfile.frontend \\
  --platform managed \\
  --region us-central1 \\
  --allow-unauthenticated \\
  --memory 512Mi \\
  --set-env-vars PASCI_API_URL={backend_url}
"""

    if run_command(cmd.strip()):
        print("   ✓ Frontend deployed successfully!")
        return True
    else:
        print("   ✗ Frontend deployment failed")
        return False


def get_service_url(service_name):
    """Get the URL of a Cloud Run service."""
    result = subprocess.run(
        f"gcloud run services describe {service_name} --region us-central1 --format='value(status.url)'",
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def main():
    """Main deployment function."""
    print("=" * 60)
    print("PASCI – Google Cloud Run Deployment")
    print("=" * 60)

    parser = argparse.ArgumentParser(description="Deploy PASCI to Google Cloud Run")
    parser.add_argument(
        "--backend-only", action="store_true", help="Deploy backend only"
    )
    parser.add_argument(
        "--frontend-only", action="store_true", help="Deploy frontend only"
    )
    parser.add_argument(
        "--gemini-key", required=True, help="Gemini API key (required)"
    )
    parser.add_argument("--maps-key", default="", help="Google Maps API key (optional)")
    parser.add_argument(
        "--skip-checks", action="store_true", help="Skip prerequisite checks"
    )

    args = parser.parse_args()

    # Check prerequisites
    if not args.skip_checks:
        print("\n🔎 Checking prerequisites...")
        if not check_gcloud():
            return 1
        if not check_authentication():
            return 1
        check_docker()

    # Get project ID
    project_id = get_project_id()
    print(f"   Using project: {project_id}")

    # Deploy backend
    if not args.frontend_only:
        if not deploy_backend(project_id, args.gemini_key, args.maps_key):
            return 1
        backend_url = get_service_url("pasci-api")
        print(f"   Backend URL: {backend_url}")
    else:
        # Get backend URL from user
        print("\nℹ️  Frontend-only deployment")
        backend_url = input("Enter backend API URL: ").strip()

    # Deploy frontend
    if not args.backend_only:
        if not deploy_frontend(project_id, backend_url):
            return 1
        frontend_url = get_service_url("pasci-frontend")
        print(f"   Frontend URL: {frontend_url}")

    # Print summary
    print("\n" + "=" * 60)
    print("DEPLOYMENT COMPLETE")
    print("=" * 60)

    if not args.frontend_only:
        backend_url = get_service_url("pasci-api")
        print(f"📍 Backend API: {backend_url}")

    if not args.backend_only:
        frontend_url = get_service_url("pasci-frontend")
        print(f"📍 Frontend Dashboard: {frontend_url}")

    print("\n✅ PASCI is now live on Google Cloud Run!")
    print("\nNext steps:")
    print("  1. Visit your frontend URL to access the dashboard")
    print("  2. Test predictions with different scenarios")
    print("  3. Share your deployment URL with others")
    print("  4. Monitor costs in Google Cloud Console")

    return 0


if __name__ == "__main__":
    sys.exit(main())
