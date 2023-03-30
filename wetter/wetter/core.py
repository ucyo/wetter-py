from .conn import get_db


def latest_datapoint():
    df = get_db()
    return df[df.index==df.index.max()]
