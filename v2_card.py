"""
Tavern Cards, as defined by Character Card Spec V2:
    https://github.com/malfoyslastname/character-card-spec-v2
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Union
from dataclasses_json import dataclass_json, Undefined

from PIL import Image
import base64
import json
import dacite


@dataclass_json
@dataclass
class TavernCardV1:
    name: str = ""
    description: str = ""
    personality: str = ""
    scenario: str = ""
    first_mes: str = ""
    mes_example: str = ""


@dataclass_json
@dataclass
class CharacterBookEntry:
    keys: List[str] = field(default_factory=lambda: [])
    content: str = ""
    extensions: Dict[str, Any] = field(default_factory=lambda: dict())
    enabled: bool = True
    insertion_order: Union[int, float] = 0
    case_sensitive: Optional[bool] = None

    name: Optional[str] = None
    priority: Optional[Union[int, float]] = None

    id: Optional[Union[int, float]] = None
    comment: Optional[str] = None
    selective: Optional[bool] = None
    secondary_keys: Optional[List[str]] = None
    constant: Optional[bool] = None
    position: Optional[Literal["before_char", "after_char"]] = None


@dataclass_json
@dataclass
class CharacterBook:
    name: Optional[str] = None
    description: Optional[str] = None
    scan_depth: Optional[int] = None
    token_budget: Optional[Union[int, float]] = None
    recursive_scanning: Optional[bool] = None
    extensions: Dict[str, Any] = field(default_factory=lambda: dict())
    entries: List[CharacterBookEntry] = field(default_factory=lambda: [])


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TavernCardV2Data:
    name: str = ""
    description: str = ""
    personality: str = ""
    scenario: str = ""
    first_mes: str = ""
    mes_example: str = ""

    # New Fields Start Here
    creator_notes: str = ""
    system_prompt: str = ""
    post_history_instructions: str = ""
    alternate_greetings: List[str] = field(default_factory=lambda: [])
    character_book: Optional[CharacterBook] = None

    # May 8th additions
    tags: List[str] = field(default_factory=lambda: [])
    creator: str = ""
    character_version: str = ""


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TavernCardV2:
    spec: Literal["chara_card_v2"] = "chara_card_v2"
    spec_version: Literal["2.0"] = "2.0"
    data: TavernCardV2Data = field(
        default_factory=lambda: TavernCardV2Data(),
    )


def extract_exif_data(image_path):
    img = Image.open(image_path)
    img.load()
    return img.info


def parse(image_path: str) -> TavernCardV2:
    data = extract_exif_data(image_path)
    if not data.get('chara'): raise Exception("Invalid Tavern card format - missing 'chara' field")
    raw = base64.b64decode(data['chara'])

    jobj = json.loads(raw)
    if not jobj.get('data'): raise Exception("Invalid Tavern card format - missing 'data' field")

    # Use dacite to convert the dictionary to a TavernCardV2 instance
    return dacite.from_dict(data_class=TavernCardV2, data=jobj)
