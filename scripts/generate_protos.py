import os
import sys
import subprocess
import requests

from pathlib import Path
from dotenv import load_dotenv
from typing import List, Optional, Tuple


load_dotenv()
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
DEFAULT_PROTO_DIR = PROJECT_ROOT / "tx_pipe_ingest" / "proto"
DEFAULT_GENERATED_DIR = PROJECT_ROOT / "tx_pipe_ingest" / "generated" / "proto"

SCHEMA_REGISTRY_URL = os.getenv("CONFLUENT_SR_URL")
SCHEMA_REGISTRY_USER = os.getenv("CONFLUENT_SR_API_KEY")
SCHEMA_REGISTRY_PASSWORD = os.getenv("CONFLUENT_SR_API_SECRET")
PROTO_SUBJECTS_STR = os.getenv("CONFLUENT_PROTO_SUBJECTS")

PROTO_DIR = Path(os.getenv("PROTO_DIR", DEFAULT_PROTO_DIR))
GENERATED_DIR = Path(os.getenv("GENERATED_DIR", DEFAULT_GENERATED_DIR))


def _get_auth_tuple() -> Optional[Tuple[str, str]]:
    if SCHEMA_REGISTRY_USER and SCHEMA_REGISTRY_PASSWORD:
        return SCHEMA_REGISTRY_USER, SCHEMA_REGISTRY_PASSWORD
    elif SCHEMA_REGISTRY_USER or SCHEMA_REGISTRY_PASSWORD:
        print("Warning: Schema registry user or password defined, but not both. Auth disabled.", file=sys.stderr)
    return None


def fetch_schema(
    schema_registry_url: str,
    subject: str,
    version: str = "latest",
    auth: Optional[Tuple[str, str]] = None,
) -> Optional[str]:
    """Fetches a schema definition from the Confluent Schema Registry."""
    url = f"{schema_registry_url}/subjects/{subject}/versions/{version}/schema"
    try:
        response = requests.get(url, auth=auth, timeout=15)
        response.raise_for_status()
        try:
            return response.text
        except Exception as e:
             print(f"Warning: Could not decode response text for {subject}: {e}", file=sys.stderr)
             return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching schema for subject '{subject}': {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"An unexpected error occurred fetching schema '{subject}': {e}", file=sys.stderr)
        return None


def save_proto_file(
    proto_content: str,
    proto_dir: Path,
    subject: str
) -> Optional[Path]:
    filename = f"{subject}.proto"
    filepath = proto_dir / filename
    try:
        proto_dir.mkdir(parents=True, exist_ok=True)
        filepath.write_text(proto_content, encoding="utf-8")
        print(f"Saved schema to {filepath}")
        return filepath
    except IOError as e:
        print(f"Error saving proto file {filepath}: {e}", file=sys.stderr)
        return None


def generate_python_code(
    proto_dir: Path,
    generated_dir: Path,
    proto_files: List[Path]
) -> bool:
    if not proto_files:
        print("No proto files found or fetched to generate code from.")
        return False

    try:
        generated_dir.mkdir(parents=True, exist_ok=True)
        (generated_dir.parent / "__init__.py").touch(exist_ok=True)
        (generated_dir / "__init__.py").touch(exist_ok=True)

        proto_paths_str = [str(p.relative_to(proto_dir)) for p in proto_files]
        command = [
            sys.executable, "-m", "grpc_tools.protoc",
            f"-I{proto_dir}",
            f"--python_out={generated_dir}",
            f"--pyi_out={generated_dir}", # Generate type hints
        ] + proto_paths_str

        print(f"Running protoc: {' '.join(map(str, command))}")
        result = subprocess.run(command, capture_output=True, text=True, check=False)

        if result.returncode != 0:
            print(f"Error running protoc:\n{result.stderr}", file=sys.stderr)
            return False
        else:
            print("Protoc execution successful.")
            if result.stdout: print(f"Protoc output:\n{result.stdout}")
            return True
    except Exception as e:
        print(f"An error occurred during code generation: {e}", file=sys.stderr)
        return False


def main():
    if not SCHEMA_REGISTRY_URL:
        print("Error: CONFLUENT_SR_URL environment variable not set.", file=sys.stderr)
        sys.exit(1)
    if not PROTO_SUBJECTS_STR:
        print("Error: CONFLUENT_PROTO_SUBJECTS environment variable not set.", file=sys.stderr)
        sys.exit(1)

    auth_tuple = _get_auth_tuple()
    subjects_list = [s.strip() for s in PROTO_SUBJECTS_STR.split(',') if s.strip()]
    fetched_proto_files: List[Path] = []

    print("--- Fetching Schemas ---")
    registry_url = SCHEMA_REGISTRY_URL.rstrip('/')
    for subject in subjects_list:
        schema_content = fetch_schema(registry_url, subject, auth=auth_tuple)
        if schema_content:
            proto_file_path = save_proto_file(schema_content, PROTO_DIR, subject)
            if proto_file_path:
                fetched_proto_files.append(proto_file_path)

    print("\n--- Generating Python Code ---")
    if fetched_proto_files:
        if not generate_python_code(PROTO_DIR, GENERATED_DIR, fetched_proto_files):
            sys.exit(1)
    else:
        print("No schemas were successfully fetched, skipping code generation.")

    print("\n--- Process Completed ---")


if __name__ == "__main__":
    main()
