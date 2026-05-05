from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("qlint")
except PackageNotFoundError:
    __version__ = "unknown"
