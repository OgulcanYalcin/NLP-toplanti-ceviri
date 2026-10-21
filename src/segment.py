"""Aşamalar arası veri: bir konuşma parçası (bkz. docs/decisions.md, D-003)."""

from dataclasses import dataclass


@dataclass
class Segment:
    """Yazıya dökülmüş (veya çevrilmiş) tek bir konuşma parçası."""

    start: float          # saniye, toplantı başından itibaren
    end: float
    text: str
    language: str         # "tr", "en", ...
    speaker: str = "ben"  # "ben" | "karsi_taraf" (ses kaynağına göre)
    is_final: bool = True  # False: geçici sonuç, değişebilir
    source_id: int = 0    # çeviri ve ses çıktısını kaynak parçaya bağlamak için
