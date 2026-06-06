import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

for service_name in (
    "auth_api",
    "core_api",
    "eventing_api",
    "observability_api",
    "notification_api",
):
    service_src = ROOT_DIR / "apps" / service_name / "src"
    sys.path.insert(0, str(service_src))

sys.path.insert(0, str(ROOT_DIR / "packages" / "shared_kernel" / "src"))
