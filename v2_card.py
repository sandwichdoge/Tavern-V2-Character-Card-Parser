"""
Tavern Cards, as defined by Character Card Spec V2:
    https://github.com/malfoyslastname/character-card-spec-v2
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Union
import dacite
from dataclasses_json import dataclass_json, Undefined
from PIL import Image
import base64
import json

@dataclass_json
@dataclass
class TavernCardV1: # Used for legacy format
    name: str = ""
    description: str = ""
    personality: str = ""
    scenario: str = ""
    first_mes: str = ""
    mes_example: str = ""
    fav: Optional[bool] = None
    chat: Optional[str] = None  
    creatorcomment: Optional[str] = None
    avatar: Optional[str] = None
    create_date: Optional[str] = None
    talkativeness: Optional[float] = None


PositionType = Optional[Literal["before_char", "after_char"]]

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
    position: PositionType = None


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
    
    fav: Optional[bool] = None
    chat: Optional[str] = None  
    creatorcomment: Optional[str] = None
    avatar: Optional[str] = None
    create_date: Optional[str] = None
    talkativeness: Optional[float] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TavernCardV2:
    spec: Literal["chara_card_v2"] = "chara_card_v2"
    spec_version: Literal["2.0"] = "2.0"
    data: TavernCardV2Data = field(
        default_factory=lambda: TavernCardV2Data(),
    )


def extract_exif_data(image_path: str) -> Dict[str, Any]:
    """Extracts metadata from an image file."""
    img = Image.open(image_path)
    img.load()
    return img.info


# Type hook function to convert '0' to None for the PositionType
def position_converter(data: Any) -> Any:
    """
    Converts integer 0 to None for the CharacterBookEntry.position field.
    Passes through other values for dacite's default processing and validation.
    """
    if data == 0:
        return None
    return data


def parse(image_path: str) -> Union[TavernCardV2, TavernCardV1]:
    """
    Parses Tavern Card data from an image file's metadata.
    Attempts to parse as V2 first, falls back to V1 if needed.
    """
    metadata = extract_exif_data(image_path)
    if "chara" not in metadata:
        raise ValueError("Invalid Tavern card format - missing 'chara' field in image metadata")
    
    try:
        raw_json_bytes = base64.b64decode(metadata["chara"])
        raw_json_string = raw_json_bytes.decode('utf-8') # Ensure decoding to string
    except (TypeError, base64.binascii.Error) as e:
        raise ValueError(f"Invalid Tavern card format - 'chara' field is not valid base64: {e}")
    except UnicodeDecodeError as e:
        raise ValueError(f"Invalid Tavern card format - 'chara' field does not decode to UTF-8: {e}")

    try:
        jobj = json.loads(raw_json_string)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid Tavern card format - 'chara' field does not contain valid JSON: {e}")

    is_v2 = 'spec' in jobj and jobj['spec'] == 'chara_card_v2'
    
    if is_v2:
        # V2 format parsing
        config = dacite.Config(
            type_hooks={PositionType: position_converter},
            strict=False,  # Changed to False to be more lenient with unexpected fields
        )

        try:
            return dacite.from_dict(data_class=TavernCardV2, data=jobj, config=config)
        except dacite.DaciteError as error:
            print(f"Error parsing as TavernCardV2, attempting V1 format: {error}")
            # Fall through to V1 parsing as a fallback
    
    # V1 format parsing (or fallback)
    try:
        # For V1 format, we need to parse the entire JSON object directly
        config = dacite.Config(
            strict=False,  # Be lenient with unexpected fields
        )
        return dacite.from_dict(data_class=TavernCardV1, data=jobj, config=config)
    except dacite.DaciteError as error:
        print(f"Error parsing TavernCardV1 data from '{image_path}': {error}")
        raise
    except Exception as error:
        print(f"An unexpected error occurred while parsing '{image_path}': {error}")
        raise
