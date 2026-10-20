"""Regression tests for Week 27 Day 5 module identity."""

from src.application.app import (
    AppDependencies as AppDependenciesFromApp,
)
from src.application.app_dependencies import (
    AppDependencies as SharedAppDependencies,
)
from src.application.local_dependencies import (
    default_local_dependency_loader,
)
from src.application.runtime_config import (
    DETERMINISTIC_ONLY,
    RAGRuntimeConfig,
)


def test_app_reexports_shared_dependency_contract():
    assert (
        AppDependenciesFromApp
        is SharedAppDependencies
    )


def test_default_loader_returns_shared_dependency_contract():
    config = RAGRuntimeConfig(
        execution_mode=(
            DETERMINISTIC_ONLY
        )
    )

    dependencies = (
        default_local_dependency_loader(
            config
        )
    )

    assert isinstance(
        dependencies,
        SharedAppDependencies,
    )

    assert isinstance(
        dependencies,
        AppDependenciesFromApp,
    )