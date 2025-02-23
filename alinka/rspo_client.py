import inspect
import os
from typing import Annotated, Literal

from pydantic import TypeAdapter
from pydantic.fields import FieldInfo
from requests import request

from alinka.config import settings
from alinka.schemas.rspo_schema import (
    Commune,
    District,
    InstitutionDetails,
    InstitutionRequestBody,
    InstitutionResponse,
    InstitutionType,
    PaginationParams,
    Province,
)


def call(*, method: Literal["GET", "POST"], path: str):
    def inner(func):
        response_model = inspect.signature(func).return_annotation
        field_info = FieldInfo(annotation=response_model)
        type_adapter = TypeAdapter(Annotated[field_info.annotation, field_info])

        def wrapper(*args, **kwargs):
            body = kwargs.pop("body", {})
            params = kwargs.pop("params", PaginationParams())
            if body:
                body = body.model_dump(exclude_unset=True, by_alias=True)
            if params:
                params = params.model_dump(by_alias=True)
            formatted_path = path.format(**kwargs)
            url = os.path.join(settings.RSPO_DOMAIN, formatted_path)
            response = request(method=method, url=url, params=params, json=body)
            return type_adapter.validate_python(response.json())

        return wrapper

    return inner


# add connection, http error handling


@call(method="GET", path="api/Dictionary/Teryt/State")
def list_provinces() -> list[Province]:
    pass


@call(method="GET", path="api/Dictionary/Teryt/State/{province_id}/District")
def list_districts(*, province_id: int) -> list[District]:
    pass


@call(method="GET", path="api/Dictionary/Teryt/State/{province_id}/District/{district_id}/Commune")
def list_communes(*, province_id: id, district_id: id) -> list[Commune]:
    pass


@call(method="GET", path="api/Dictionary/InstitutionType")
def list_institution_types() -> list[InstitutionType]:
    pass


@call(method="POST", path="api/Institution")
def list_institutions(*, body: InstitutionRequestBody, params: PaginationParams) -> InstitutionResponse:
    pass


@call(method="GET", path="api/Institution/{rspo_id}")
def get_institution(*, rspo_id: int) -> InstitutionDetails:
    pass
