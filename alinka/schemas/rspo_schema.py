from pydantic import AliasPath, BaseModel, ConfigDict, Field, computed_field


class PaginationParams(BaseModel):
    page_offset: int = Field(0, serialization_alias="PageOffset")
    page_size: int = Field(100, serialization_alias="PageSize")


class BaseRSPO(BaseModel):
    model_config = ConfigDict(extra="ignore")


class BaseEntity(BaseRSPO):
    id: int
    name: str


class Province(BaseEntity):
    pass


class District(BaseEntity):
    pass


class Commune(BaseEntity):
    pass


class InstitutionType(BaseEntity):
    is_lead_authority: bool = Field(..., validation_alias="isLeadAuthority")
    is_transferring_rspo_authority: bool = Field(..., validation_alias="isTransferringRSPOAuthority")
    is_rspo_institution: bool = Field(..., validation_alias="isRSPOInstitution")
    is_art_school: bool = Field(..., validation_alias="isArtSchool")
    is_school: bool = Field(..., validation_alias="isSchool")
    is_primary_school: bool = Field(..., validation_alias="isPrimarySchool")
    is_secondary_school: bool = Field(..., validation_alias="isSecondarySchool")


class Institution(BaseEntity):
    rspo_id: int = Field(..., validation_alias="rspo")
    type: BaseEntity | None
    postal_code: str = Field(..., validation_alias="hqAddressZipCode")
    post: str = Field(..., validation_alias="hqAddressPostal")
    town: str = Field(..., validation_alias=AliasPath("hqAddressLocality", "name"))
    street: str = Field(..., validation_alias="hqAddressStreet")
    building_no: str = Field(..., validation_alias="hqAddressBuildingNr")

    @computed_field
    @property
    def address(self) -> str:
        return f"{self.street} {self.building_no}"


class InstitutionRequestBody(BaseModel):
    district_id: int = Field(None, serialization_alias="districtId")
    province_id: int = Field(None, serialization_alias="stateId")
    commune_id: int = Field(None, serialization_alias="communeId")
    institution_type_ids: list[int] | None = Field(None, serialization_alias="institutionTypeIdList")
    rspo: int | None = None


class InstitutionResponse(BaseModel):
    total: int = Field(..., validation_alias="totalCount")
    items: list[Institution]


class InstitutionDetails(Institution):
    type: BaseEntity = Field(None, validation_alias="institutionType")
    parent_organisation_name: str = Field(None, validation_alias=AliasPath("parentInstitution", "name"))
