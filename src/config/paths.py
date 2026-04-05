from pathlib import Path

# directories
ROOT_DIR = Path(__file__).parent.parent.parent
ALEMBIC_DIR = ROOT_DIR / "alembic"

# paths
ALEMBIC_INI_PATH = Path(ROOT_DIR / "alembic.ini").absolute()
