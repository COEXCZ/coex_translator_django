import dataclasses
import typing


@dataclasses.dataclass(kw_only=True)
class BaseClientDataSchema:
    def dict(self, exclude_none: bool = True) -> dict[str, typing.Any]:
        data = dataclasses.asdict(self)
        if exclude_none:
            data = {k: v for k, v in dataclasses.asdict(self).items() if v is not None}
        return data


@dataclasses.dataclass(kw_only=True)
class ClientRequestDataSchema(BaseClientDataSchema):
    pass


@dataclasses.dataclass(kw_only=True)
class ClientResponseDataSchema(BaseClientDataSchema):
    pass
