from sqlalchemy import MetaData

metadata = MetaData()


class Base:
    metadata = metadata
