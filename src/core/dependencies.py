from typing import Callable, Type
from functools import cache
from fastapi import FastAPI
from src.handlers.recommend import *
import logging

dependencies_container: dict[Type | Callable, Callable] = {}


def add_factory_to_mapper(cls: Type | Callable):
    def _add_factory_to_mapper(func: Callable):
        dependencies_container[cls] = func
        return func
    return _add_factory_to_mapper


class InMemoryrecommendRepository:
    def __init__(self):
        self.recommend = []

    async def add_recommend(self, recommend):
        self.recommend.append(recommend)
        return recommend

    async def get_all_recommend(self):
        return self.recommend

    async def get_recommend_by_id(self, recommend_id):
        for recommend in self.recommend:
            if recommend["id"] == recommend_id:
                return recommend
        return None


@add_factory_to_mapper(recommendHandlerABC)
@cache
def create_recommend_service() -> recommendHandlerABC:
    repository = InMemoryrecommendRepository()
    return recommendHandler(repository)


def setup_dependencies(app: FastAPI, mapper: dict[Type | Callable, Callable] | None = None) -> None:
    if mapper is None:
        mapper = dependencies_container
    for interface, dependency in mapper.items():
        app.dependency_overrides[interface] = dependency
    logging.info("Dependencies mapping: %s", app.dependency_overrides)

