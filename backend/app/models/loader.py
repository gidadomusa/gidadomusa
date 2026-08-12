from pathlib import Path
from typing import Any, Dict

MODEL_DIR = Path(__file__).resolve().parents[2] / "trained_models"
MODEL_REGISTRY: Dict[str, Dict[str, Any]] = {}


def scan_models() -> Dict[str, Dict[str, Any]]:
    out = {}
    if not MODEL_DIR.exists():
        return out
    for p in MODEL_DIR.iterdir():
        if p.is_file() and p.suffix.lower() in (".pt", ".pth"):
            name = p.stem
            out[name] = {"path": p, "ext": p.suffix.lower(), "type": "pytorch"}
    return out


def load_model(name: str, device: str = "cpu") -> Dict[str, Any]:
    if name in MODEL_REGISTRY and "obj" in MODEL_REGISTRY[name]:
        return MODEL_REGISTRY[name]

    models = scan_models()
    if name not in models:
        raise KeyError(f"Model {name} not found in {MODEL_DIR}")

    meta = models[name]
    p = meta["path"]
    # Lazy import torch
    import torch

    # Load model object. Expect the file to contain a serialized model (scripted or state dict).
    try:
        obj = torch.load(str(p), map_location=device)
    except Exception:
        # Try loading as TorchScript
        obj = torch.jit.load(str(p), map_location=device)

    # If we got a state_dict, user needs to provide model class; keep raw object anyway.
    try:
        obj.eval()
    except Exception:
        pass

    MODEL_REGISTRY[name] = {"path": p, "type": "pytorch", "obj": obj}
    return MODEL_REGISTRY[name]


def predict_pytorch(name: str, inputs, device: str = "cpu"):
    info = load_model(name, device=device)
    if info["type"] != "pytorch":
        raise RuntimeError("Not a pytorch model")
    model = info["obj"]
    import torch
    import numpy as np

    # Convert inputs (list) to tensor
    if isinstance(inputs, (list, tuple)):
        tensor = torch.tensor(inputs)
    elif isinstance(inputs, (int, float)):
        tensor = torch.tensor([inputs])
    else:
        # try numpy
        tensor = torch.as_tensor(inputs)

    tensor = tensor.to(device)
    model = model.to(device)
    with torch.no_grad():
        out = model(tensor)

    # Convert torch output to python types
    try:
        if isinstance(out, (list, tuple)):
            results = [o.detach().cpu().numpy().tolist() for o in out]
        else:
            results = out.detach().cpu().numpy().tolist()
    except Exception:
        # fallback: try converting to list
        try:
            results = list(out)
        except Exception:
            results = str(out)
    return {"result": results}
