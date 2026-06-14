import ast
from pathlib import Path

FORBIDDEN_PREFIXES = (
    "fastapi",
    "sqlalchemy",
    "dependency_injector",
    "pydantic",
    "os",
    "pathlib",
    "http",
    "urllib",
    "socket",
    "subprocess",
    "dotenv",
)


def test_domain_package_stays_pure() -> None:
    domain_root = Path(__file__).resolve().parents[3] / "src" / "domain"

    for path in domain_root.rglob("*.py"):
        tree = ast.parse(path.read_text())

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                modules = [node.module] if node.module else []
            else:
                continue

            for module in modules:
                assert module is not None
                assert not module.startswith(FORBIDDEN_PREFIXES), f"{path}: {module}"
