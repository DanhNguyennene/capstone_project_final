#!/usr/bin/env python3
import importlib


def main() -> None:
    for name in ["torch", "transformers", "datasets", "peft", "bitsandbytes"]:
        try:
            module = importlib.import_module(name)
            version = getattr(module, "__version__", "")
            print(f"{name}: OK {version}".strip())
        except Exception as exc:
            print(f"{name}: MISSING_OR_ERROR {exc.__class__.__name__}: {exc}")

    try:
        import torch

        print(f"cuda_available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"cuda_device: {torch.cuda.get_device_name(0)}")
            print(f"bf16_supported: {torch.cuda.is_bf16_supported()}")
    except Exception as exc:
        print(f"torch_cuda_check_error: {exc}")


if __name__ == "__main__":
    main()