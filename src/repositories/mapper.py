from dataclasses import fields
from typing import TypeVar, Type, get_origin, NamedTuple, Any

from sqlalchemy import inspect as sql_inspect
from sqlalchemy.orm import LoaderCallableStatus

T_Entity = TypeVar("T_Entity")
T_Model = TypeVar("T_Model")


class MappingRule(NamedTuple):
    field_name: str
    entity: Any
    model: Any


class DynamicMapper:
    """
    Дженерик маппер, который преобразует ORM-модели в доменные модели
    """

    def __init__(
        self,
        model_type: Type[T_Model],
        entity_type: Type[T_Entity],
        mapping_rules: dict = None,
    ):
        self.model_type = model_type
        self.entity_type = entity_type
        self.entity_fields = fields(self.entity_type)
        self.mapping_rules = mapping_rules or {}

    def map_to_model(self, model: T_Model, include_relations: bool = False) -> T_Entity:
        if model is None:
            return None

        # Получаем атрибуты ORM-модели
        model_dict = {}
        model_inspect = sql_inspect(model)
        for key in model_inspect.attrs.keys():
            attr_state = model_inspect.attrs[key]
            # Проверяем, загружено ли значение (не lazy loading связь)
            if attr_state.loaded_value != LoaderCallableStatus.NO_VALUE:
                model_dict[key] = getattr(model, key)
            else:
                model_dict[key] = None

        result = {}

        for field in self.entity_fields:
            field_name = field.name
            field_type = field.type
            value = model_dict[field_name]
            if include_relations and field_name in self.mapping_rules:
                relation_info = self.mapping_rules[field_name]
                relation_model_type, relation_mapper = relation_info
                if get_origin(field_type) is list:
                    items = []
                    for item in value:
                        mapped_item = relation_mapper.map_to_model(
                            item, include_relations=False
                        )
                        items.append(mapped_item)
                    result[field_name] = items
                else:
                    result[field_name] = relation_mapper.map_to_model(
                        value, include_relations=False
                    )
            else:
                result[field_name] = value

        return self.entity_type(**result)


class MapperFactory:
    _mappers: dict[tuple[Any, Any], DynamicMapper] = {}

    @classmethod
    def register(
        cls,
        entity_type: Type[T_Entity],
        model_type: Type[T_Model],
        rules: list[tuple[str, Any, Any]],
    ):
        resolved_rules = {}
        for field, rel_entity, rel_model in rules:
            rel_mapper = cls._get_or_create_mapper(rel_entity, rel_model)
            resolved_rules[field] = (rel_entity, rel_mapper)

        mapper = DynamicMapper(model_type, entity_type, resolved_rules)
        cls._mappers[(entity_type, model_type)] = mapper
        return mapper

    @classmethod
    def _get_or_create_mapper(
        cls, entity_type: Type[T_Entity], model_type: Type[T_Model]
    ):
        key = (entity_type, model_type)
        if key not in cls._mappers:
            # Если маппер не зарегистрирован, создаём пустой (без связей)
            cls._mappers[key] = DynamicMapper(model_type, entity_type, {})
        return cls._mappers[key]

    @classmethod
    def get_mapper(cls, entity_type: Type[T_Entity], model_type: Type[T_Model]):
        return cls._mappers.get((entity_type, model_type))
