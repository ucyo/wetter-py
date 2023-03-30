def get_version():
    try:
        # try new metadata package
        from importlib import metadata

        return metadata.version("wetter")
    except ImportError:
        # backup routine if Python version <= 3.7
        import pkg_resources

        return pkg_resources.get_distribution("wetter").version


__version__ = get_version()
