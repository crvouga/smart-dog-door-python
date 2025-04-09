import os


def assets_dir(asset_path: str) -> str:
    asset_path = os.path.join("./assets", asset_path)

    if not os.path.exists(asset_path):
        raise FileNotFoundError(f"Asset not found: {asset_path}")

    return asset_path
