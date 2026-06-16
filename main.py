import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC_DIR = ROOT / "src"
SRC_MAIN = SRC_DIR / "main.py"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def main() -> None:
    spec = spec_from_file_location("routestack_main", SRC_MAIN)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load RouteStack main module")

    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()


if __name__ == "__main__":
    main()
