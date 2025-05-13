from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import User
from typing import List, Optional
from sqlalchemy import or_, func


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
        for skill in skills:
            filters.append(
                func.array_to_string(User.key_skills, ',').ilike(f"%{skill.lower()}%")
            )

    if location:
        filters.append(func.lower(User.location).ilike(f"%{location.lower()}%"))
            
    if min_experience is not None:
        filters.append(User.years_of_experience >= min_experience)

    stmt = select(User).where(and_(*filters)) if filters else select(User)

    result = await db.execute(stmt)
    return result.scalars().all()
