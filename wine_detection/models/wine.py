from dataclasses import dataclass, field
from typing import Optional


@dataclass
class WineRecognition:
    """
    Результат распознавания фотографии моделью.
    """

    name: Optional[str] = None
    grape_variety: Optional[str] = None


@dataclass
class WineRecommendation:
    """
    Вино из каталога.
    """

    title: str
    page_url: str
    rating: float
    grape_variety: Optional[str] = None
    manufacturer: Optional[str] = None
    category: Optional[str] = None
    strength: Optional[str] = None
    region: Optional[str] = None
    year: Optional[int] = None
    color: Optional[str] = None
    temperature: Optional[str] = None
    character: Optional[str] = None
    similar_titles: list[str] = field(default_factory=list)

    def to_public_dict(self) -> dict:
        return {
            "название": self.title,
            "производитель": self.manufacturer,
            "категория": self.category,
            "виноград": self.grape_variety,
            "крепость": self.strength,
            "регион": self.region,
            "год": self.year,
            "цвет": self.color,
            "температура": self.temperature,
            "характер": self.character,
        }


@dataclass
class WineResult:
    """
    Финальный результат работы приложения.
    """

    recognition: WineRecognition
    recommendations: list[WineRecommendation]
    match_type: str