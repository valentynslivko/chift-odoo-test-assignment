import uuid
from datetime import datetime, timezone
from typing import Annotated, Any, Dict, List, Optional

from sqlalchemy import ARRAY, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSON, JSONB, UUID
from sqlalchemy.orm import mapped_column

uuid_pk = Annotated[
    str,
    mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    ),
]
int_pk = Annotated[int, mapped_column(autoincrement=True, index=True, primary_key=True)]
nullable_json_column = Annotated[Dict[str, Any], mapped_column(JSON, nullable=True)]
nullable_json_array_column = Annotated[
    List[Dict[str, str]], mapped_column(JSONB, nullable=True)
]
created_at = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    ),
]
updated_at = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    ),
]

nullable_string_256 = Annotated[
    Optional[str], mapped_column(String(256), nullable=True)
]
nullable_int = Annotated[Optional[int], mapped_column(Integer, nullable=True)]
nullable_datetime = Annotated[
    Optional[datetime], mapped_column(DateTime(timezone=True), nullable=True)
]

nullable_int_array = Annotated[
    Optional[list[int]], mapped_column(ARRAY(Integer), nullable=True)
]
nullable_str_array = Annotated[
    Optional[list[str]], mapped_column(ARRAY(String), nullable=True)
]
