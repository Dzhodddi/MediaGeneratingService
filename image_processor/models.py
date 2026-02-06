from pydantic import BaseModel, ConfigDict


class AppBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
        populate_by_name=True,
    )
