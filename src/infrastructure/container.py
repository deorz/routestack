from dependency_injector import containers, providers

from application.settings import AppSettings


class Container(containers.DeclarativeContainer):
    """Application composition root."""

    settings = providers.Singleton(AppSettings)


def create_container() -> Container:
    return Container()
