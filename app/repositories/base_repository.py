from app import db
from typing import List, Optional, Type, TypeVar

T = TypeVar('T')

class BaseRepository:
    def __init__(self, model: Type[T]):
        self.model = model
    
    def get_by_id(self, id: str) -> Optional[T]:
        return self.model.query.get(id)
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[T]:
        query = self.model.query
        if limit:
            query = query.limit(limit).offset(offset)
        return query.all()
    
    def create(self, entity: T) -> T:
        db.session.add(entity)
        db.session.commit()
        return entity
    
    def update(self, entity: T) -> T:
        db.session.commit()
        return entity
    
    def delete(self, entity: T) -> bool:
        db.session.delete(entity)
        db.session.commit()
        return True
    
    def count(self) -> int:
        return self.model.query.count()

