
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    send_from_directory,
)
from werkzeug.utils import secure_filename

from network.topology import (
    create_sample_network,
    create_star_topology,
    create_ring_topology,
    create_mesh_topology,
)
from network.routing import find_shortest_route
from network.failures import get_active_network

app = Flask(__name__)

# Limit individual uploads to 100 MB.
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024

# Store uploaded files in the Flask instance directory.
STORAGE_DIR = Path(app.instance_path) / "transfers"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

TOPOLOGIES = {
    "sample": create_sample_network,
    "star": create_star_topology,
    "ring": create_ring_topology,
    "mesh": create_mesh_topology,
}


def get_network(topology_name):
    """Create the requested network topology."""
    if topology_name not in TOPOLOGIES:
        raise ValueError("Unknown topology selected.")

    return TOPOLOGIES[topology_name]()


def get_file_metadata(file_id):
    """Read metadata for a valid uploaded file ID."""
    try:
        safe_id = uuid.UUID(file_id).hex
    except (ValueError, TypeError, AttributeError):
        return None

    metadata_path = STORAGE_DIR / f"{safe_id}.json"

    if not metadata_path.is_file():
        return None

    try:
        with metadata_path.open("r", encoding="utf-8") as file:
            metadata = json.load(file)
    except (OSError, json.JSONDecodeError):
        return None

    if metadata.get("id") != safe_id:
        return None

    return metadata


def list_uploaded_files():
    """Return metadata for all successfully registered files."""
    files = []

    for metadata_path in STORAGE_DIR.glob("*.json"):
        try:
            with metadata_path.open("r", encoding="utf-8") as file:
                metadata = json.load(file)

            if (
                metadata.get("id") == metadata_path.stem
                and (STORAGE_DIR / metadata.get("storage_name", "")).is_file()
            ):
                files.append({
                    "id": metadata["id"],
                    "filename": metadata["filename"],
                    "size": metadata["size"],
                    "uploaded_at": metadata["uploaded_at"],
                    "download_url": (
                        f"/api/files/{metadata['id']}/download"
                    ),
                })
        except (OSError, json.JSONDecodeError, TypeError):
            continue

    files.sort(
        key=lambda item: item["uploaded_at"],
        reverse=True,
    )
    return files


@app.route("/", methods=["GET", "POST"])
def index():
    selected_topology = "sample"
    source = "R1"
    destination = "R4"
    result = None
    error = None

    if request.method == "POST":
        selected_topology = request.form.get("topology", "sample")
        source = request.form.get("source", "R1")
        destination = request.form.get("destination", "R4")

    try:
        network = get_network(selected_topology)
    except ValueError as exc:
        network = get_network("sample")
        selected_topology = "sample"
        error = str(exc)

    routers = list(network.nodes())
    connections = list(network.edges(data=True))

    if source not in routers:
        source = routers[0]

    if destination not in routers:
        destination = routers[-1]

    if request.method == "POST" and error is None:
        try:
            result = find_shortest_route(
                network, source, destination
            )
        except ValueError as exc:
            error = str(exc)

    return render_template(
        "index.html",
        routers=routers,
        connections=connections,
        result=result,
        error=error,
        source=source,
        destination=destination,
        selected_topology=selected_topology,
    )


@app.route("/api/health", methods=["GET"])
def health():
    """Report backend status."""
    return jsonify({
        "status": "online",
        "application": "NetRoute",
        "file_transfer": "ready",
    })


@app.route("/api/topology-data", methods=["GET"])
def topology_data():
    """Return router and connection information."""
    topology_name = request.args.get("topology", "sample")

    try:
        network = get_network(topology_name)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    disabled_links = []

    for item in request.args.getlist("disabled"):
        parts = item.split(",", 1)
        if len(parts) == 2:
            disabled_links.append(parts)

    routers = [
        {"id": router, "label": router, "type": "router"}
        for router in network.nodes()
    ]

    connections = []

    for router1, router2, data in network.edges(data=True):
        is_disabled = (
            [router1, router2] in disabled_links
            or [router2, router1] in disabled_links
        )
        cost = data.get("cost", 1)

        connections.append({
            "source": router1,
            "target": router2,
            "cost": cost,
            "bandwidth_mbps": max(10, 100 // max(1, cost)),
            "latency_ms": cost * 5,
            "active": not is_disabled,
        })

    return jsonify({
        "topology": topology_name,
        "routers": routers,
        "connections": connections,
    })


@app.route("/api/route", methods=["POST"])
def calculate_route():
    """Calculate a route while excluding disabled links."""
    payload = request.get_json(silent=True) or {}

    try:
        network = get_network(payload.get("topology", "sample"))
        source = payload.get("source", "R1")
        destination = payload.get("destination", "R4")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    disabled_links = payload.get("disabled_links", [])

    active_network = get_active_network(network)

    if not isinstance(disabled_links, list):
        return jsonify({"error": "disabled_links must be a list."}), 400

    for link in disabled_links:
        if not isinstance(link, list) or len(link) != 2:
            continue

        router1, router2 = link

        if active_network.has_edge(router1, router2):
            active_network.remove_edge(router1, router2)

    try:
        result = find_shortest_route(
            active_network, source, destination
        )
        return jsonify(result)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/files", methods=["GET"])
def get_files():
    """List files uploaded by connected clients."""
    return jsonify({"files": list_uploaded_files()})


@app.route("/api/files", methods=["POST"])
def upload_file():
    """Receive and store a real file uploaded by a client."""
    uploaded = request.files.get("file")

    if uploaded is None:
        return jsonify({
            "error": "No file was provided. Use the form field 'file'."
        }), 400

    if not uploaded.filename:
        return jsonify({"error": "Please select a file."}), 400

    filename = secure_filename(uploaded.filename)

    if not filename:
        filename = "uploaded_file"

    file_id = uuid.uuid4().hex
    storage_name = f"{file_id}.data"

    data_path = STORAGE_DIR / storage_name
    metadata_path = STORAGE_DIR / f"{file_id}.json"

    try:
        uploaded.save(data_path)
        file_size = data_path.stat().st_size

        metadata = {
            "id": file_id,
            "filename": filename,
            "storage_name": storage_name,
            "size": file_size,
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
        }

        with metadata_path.open("w", encoding="utf-8") as file:
            json.dump(metadata, file)

    except OSError:
        data_path.unlink(missing_ok=True)
        metadata_path.unlink(missing_ok=True)

        app.logger.exception("Could not store uploaded file.")
        return jsonify({"error": "The server could not store the file."}), 500

    return jsonify({
        "message": "File uploaded successfully.",
        "file": {
            "id": file_id,
            "filename": filename,
            "size": file_size,
            "uploaded_at": metadata["uploaded_at"],
            "download_url": f"/api/files/{file_id}/download",
        },
    }), 201


@app.route("/api/files/<file_id>/download", methods=["GET"])
def download_file(file_id):
    """Send the actual stored file contents to a receiving client."""
    metadata = get_file_metadata(file_id)

    if metadata is None:
        return jsonify({"error": "File not found."}), 404

    storage_name = metadata.get("storage_name", "")

    # Only serve generated storage names, never arbitrary filesystem paths.
    if storage_name != f"{metadata['id']}.data":
        return jsonify({"error": "Invalid file metadata."}), 500

    if not (STORAGE_DIR / storage_name).is_file():
        return jsonify({"error": "Stored file is missing."}), 404

    return send_from_directory(
        str(STORAGE_DIR),
        storage_name,
        as_attachment=True,
        download_name=metadata["filename"],
    )


@app.errorhandler(413)
def file_too_large(_error):
    """Return a readable response for oversized uploads."""
    return jsonify({
        "error": "File is too large. The current limit is 100 MB."
    }), 413


if __name__ == "__main__":
    # Keep this development server on your own machine for now.
    app.run(debug=True)
