"""Defines the dependency injection structure

@author Rory Byrne <rory@rory.bio>
"""
from dependency_injector import providers, containers
from watchdog.observers.polling import PollingObserver

from codeline.oracle.handler.project import ProjectEventHandler
from codeline.oracle.handler.registry import RegistryEventHandler
from codeline.oracle.oracle import Oracle
from codeline.service.command import CommandService
from codeline.service.file import FileService
from codeline.service.plugin import PluginService
from codeline.service.registry import RegistryService


class Services(containers.DeclarativeContainer):
    """Dependency structure for services"""

    config = providers.Configuration()

    registry_service = providers.Singleton(
        RegistryService, projects_file=config.core.projects_file
    )

    file_service = providers.Singleton(
        FileService
    )

    plugin_service = providers.Singleton(
        PluginService, plugin_directory=config.core.plugin_directory
    )

    command_service = providers.Singleton(
        CommandService,
        plugin_service=plugin_service,
        file_service=file_service
    )


class Observer(containers.DeclarativeContainer):
    """Dependency structure for observer"""

    config = providers.Configuration()
    services = providers.DependenciesContainer()

    # Event Handlers
    registry_event_handler = providers.Singleton(
        RegistryEventHandler, registry_service=services.registry_service
    )

    project_event_handler = providers.Singleton(
        ProjectEventHandler,
        command_service=services.command_service,
        file_service=services.file_service
    )

    # Third-Party Dependencies
    observer = providers.Singleton(PollingObserver)


class Codeline(containers.DeclarativeContainer):
    """Top-level container for the application"""

    config = providers.Configuration()

    services = providers.Container(
        Services,
        config=config,
    )

    observer = providers.Container(Observer, config=config, services=services)

    oracle = providers.Singleton(
        Oracle,
        registry_service=services.registry_service,
        observer=observer.observer,
        registry_event_handler=observer.registry_event_handler,
        project_event_handler=observer.project_event_handler,
    )
