from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import User
from typing import List, Optional


async def filter_candidates(
    skills: Optional[List[str]],
    location: Optional[str],
    min_experience: Optional[int],
    db: AsyncSession
):
    return await search_candidates(skills, location, min_experience, db)

async def search_candidates(
    skills: Optional[List[str]],
    location: Optional[str],
    min_experience: Optional[int],
    db: AsyncSession
):
    filters = []

    if skills:
        filters.append(User.key_skills.op("&&")(array(skills)))  

    if location:
        filters.append(User.location == location)

    if min_experience is not None:
        filters.append(User.years_of_experience >= min_experience)

    stmt = select(User).where(and_(*filters)) if filters else select(User)

    result = await db.execute(stmt)
    return result.scalars().all()