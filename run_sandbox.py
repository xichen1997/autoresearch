import modal
import os

app = modal.App("autoresearch-sandbox")

image = (
    modal.Image.debian_slim(python_version="3.10")
    # Install dependencies as listed in pyproject.toml
    .pip_install(
        "kernels>=0.11.7",
        "matplotlib>=3.10.8",
        "numpy>=2.2.6",
        "pandas>=2.3.3",
        "pyarrow>=21.0.0",
        "requests>=2.32.0",
        "rustbpe>=0.1.0",
        "tiktoken>=0.11.0",
        "uv",
    )
    .pip_install("torch==2.9.1", index_url="https://download.pytorch.org/whl/cu128")
    # add other necessary tools
    .apt_install("git", "curl", "vim", "nano")
    # Add our local directory
    .add_local_dir(".", remote_path="/root/autoresearch")
)

volume = modal.Volume.from_name("autoresearch-data", create_if_missing=True)

@app.local_entrypoint()
def main():
    print("Starting autoresearch Sandbox on Modal...")
    
    # We create a Sandbox that runs a sleep command, keeping it alive for 24 hours.
    # The user can then connect to it.
    sandbox = modal.Sandbox.create(
        "sleep", "86400",
        app=app,
        image=image,
        volumes={"/root/.cache/autoresearch": volume},
        gpu="H100", # Specific hardware requirement
        timeout=86400, # Keep it alive for up to 24 hours
        workdir="/root/autoresearch"
    )
    
    print(f"Sandbox created with ID: {sandbox.object_id}")
    print("To connect to the sandbox and start experimenting, run:")
    print(f"  modal proxy {sandbox.object_id} --port 22")
    print("Or to execute commands directly:")
    print(f"  modal exec {sandbox.object_id} bash")
    print("Keeping the app alive. Press Ctrl+C to terminate the Sandbox.")
    
    sandbox.wait()
