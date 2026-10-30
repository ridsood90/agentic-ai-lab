from pydantic import BaseModel

class TravelState(BaseModel):
    destination: str | None = None
    budget: int | None = None
    hotel_preference: str | None = None

    def apply_update(self, update: BaseModel):
        changes = update.model_dump(exclude_none=True)

        for field, value in changes.items():
            setattr(self, field, value)