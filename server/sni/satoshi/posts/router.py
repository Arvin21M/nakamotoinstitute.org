from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from sni.database import get_db

from . import service
from .schemas import (
    ForumPostBaseModel,
    ForumPostDetailModel,
    ForumPostModel,
    ForumThreadBaseModel,
    ForumThreadModel,
)

router = APIRouter()


@router.get("", response_model=List[ForumPostBaseModel])
async def get_forum_posts(db: AsyncSession = Depends(get_db)):
    return await service.get_all_posts(db_session=db)


@router.get("/threads", response_model=List[ForumThreadBaseModel])
async def get_forum_threads(db: AsyncSession = Depends(get_db)):
    return await service.get_threads(db_session=db)


@router.get("/{source}", response_model=List[ForumPostModel])
async def get_forum_posts_by_source(source: str, db: AsyncSession = Depends(get_db)):
    return await service.get_posts_by_source(source, db_session=db)


@router.get("/{source}/threads", response_model=List[ForumThreadBaseModel])
async def get_forum_threads_by_source(source: str, db: AsyncSession = Depends(get_db)):
    return await service.get_threads_by_source(source, db_session=db)


@router.get("/{source}/threads/{thread_id}", response_model=ForumThreadModel)
async def get_forum_thread_by_source(
    source: str,
    thread_id: int,
    satoshi: bool = False,
    db: AsyncSession = Depends(get_db),
):
    thread = await service.get_thread(thread_id, db_session=db)
    if not thread or thread.source != source:
        raise HTTPException(status_code=404, detail="Forum thread not found")

    previous_thread = await service.get_thread(thread_id - 1, db_session=db)
    next_thread = await service.get_thread(thread_id + 1, db_session=db)

    return {
        "posts": thread.posts,
        "thread": thread,
        "previous": previous_thread,
        "next": next_thread,
    }


@router.get("/{source}/{satoshi_id}", response_model=ForumPostDetailModel)
async def get_forum_post_by_source(
    source: str, satoshi_id: int, db: AsyncSession = Depends(get_db)
):
    post = await service.get_post_by_source(source, satoshi_id, db_session=db)
    if not post:
        raise HTTPException(status_code=404, detail="Forum post not found")

    previous_post = await service.get_post(satoshi_id - 1, db_session=db)
    next_post = await service.get_post(satoshi_id + 1, db_session=db)

    return {"post": post, "previous": previous_post, "next": next_post}
