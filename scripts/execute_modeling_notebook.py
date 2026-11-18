"""Execute privately with this interpreter; never overwrite the clean public notebook."""

import asyncio
import json
import os
import sys
from pathlib import Path

import nbformat
from jupyter_client.kernelspec import KernelSpecManager
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Validate a public notebook and save executed outputs only under artifacts/."""
    path = ROOT / "notebooks/16_samsung_health_modeling.ipynb"
    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    for cell in notebook.cells:
        if cell.cell_type == "code" and (cell.outputs or cell.execution_count is not None):
            raise ValueError("Public notebook must have no executed health outputs")
    output = ROOT / "artifacts/task16"
    os.environ["IPYTHONDIR"] = str(output / "ipython")
    os.environ["JUPYTER_RUNTIME_DIR"] = str(output / "jupyter-runtime")
    os.environ["MPLCONFIGDIR"] = str(ROOT / "artifacts/mpl-cache")
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    kernel = output / "kernels/python3"
    kernel.mkdir(parents=True, exist_ok=True)
    (kernel / "kernel.json").write_text(json.dumps({
        "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
        "display_name": "TASK 16 private local", "language": "python",
    }), encoding="utf-8")
    client = NotebookClient(
        notebook, timeout=180, kernel_name="python3",
        resources={"metadata": {"path": str(ROOT)}},
    )
    client.create_kernel_manager()
    client.km.kernel_spec_manager = KernelSpecManager(kernel_dirs=[str(kernel.parent)])
    client.execute()
    nbformat.write(notebook, output / "16_samsung_health_modeling.executed.ipynb")
    print("Notebook executed locally; private output saved under ignored artifacts/.")


if __name__ == "__main__":
    main()
