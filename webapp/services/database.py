from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, create_engine, desc, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker
from sqlalchemy.sql import func

from webapp.app_paths import DEFAULT_DB_PATH
from webapp.core.types import EvaluationResult
from webapp.services.storage import ensure_runtime_directories


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    evaluations: Mapped[list["Evaluation"]] = relationship(back_populates="user")


class Song(Base):
    __tablename__ = "songs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    reference_filename: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    evaluations: Mapped[list["Evaluation"]] = relationship(back_populates="song")


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    song_id: Mapped[int] = mapped_column(ForeignKey("songs.id"))
    cover_filename: Mapped[str] = mapped_column(String(255))
    cover_path: Mapped[str] = mapped_column(String(500))
    original_path: Mapped[str] = mapped_column(String(500))
    final_score: Mapped[float] = mapped_column(Float)
    grade: Mapped[str] = mapped_column(String(4))
    mfcc_error: Mapped[float] = mapped_column(Float)
    energy_error: Mapped[float] = mapped_column(Float)
    rop_error: Mapped[float] = mapped_column(Float)
    singing_power_ratio: Mapped[float] = mapped_column(Float)
    delta_pitch_error: Mapped[float] = mapped_column(Float)
    median_pitch_error: Mapped[float] = mapped_column(Float)
    alignment_path_length: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship(back_populates="evaluations")
    song: Mapped[Song] = relationship(back_populates="evaluations")


class Database:
    def __init__(self, db_path: Path | None = None) -> None:
        ensure_runtime_directories()
        active_db_path = db_path or DEFAULT_DB_PATH
        self.engine = create_engine(f"sqlite:///{active_db_path}", future=True)
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False, future=True)

    def initialize(self) -> None:
        Base.metadata.create_all(self.engine)

    @contextmanager
    def session(self) -> Iterator[Session]:
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_or_create_user(self, name: str) -> User:
        with self.session() as session:
            user = session.scalar(select(User).where(User.name == name))
            if user is None:
                user = User(name=name)
                session.add(user)
                session.flush()
            return user

    def upsert_song(self, title: str, reference_filename: str) -> Song:
        with self.session() as session:
            song = session.scalar(
                select(Song).where(Song.title == title, Song.reference_filename == reference_filename)
            )
            if song is None:
                song = Song(title=title, reference_filename=reference_filename)
                session.add(song)
                session.flush()
            return song

    def save_evaluation(
        self,
        *,
        user_name: str,
        song_title: str,
        reference_filename: str,
        cover_filename: str,
        cover_path: str,
        original_path: str,
        result: EvaluationResult,
    ) -> Evaluation:
        user = self.get_or_create_user(user_name)
        song = self.upsert_song(song_title, reference_filename)

        with self.session() as session:
            evaluation = Evaluation(
                user_id=user.id,
                song_id=song.id,
                cover_filename=cover_filename,
                cover_path=cover_path,
                original_path=original_path,
                final_score=result.final_score,
                grade=result.grade,
                mfcc_error=result.metrics.mfcc_error,
                energy_error=result.metrics.energy_error,
                rop_error=result.metrics.rop_error,
                singing_power_ratio=result.metrics.singing_power_ratio,
                delta_pitch_error=result.metrics.delta_pitch_error,
                median_pitch_error=result.metrics.median_pitch_error,
                alignment_path_length=int(result.alignment_metadata["mfcc"]["path_length"]),
            )
            session.add(evaluation)
            session.flush()
            return evaluation

    def fetch_recent_evaluations(self, user_name: str, limit: int = 10) -> list[dict[str, object]]:
        with self.session() as session:
            stmt = (
                select(Evaluation, Song)
                .join(User, Evaluation.user_id == User.id)
                .join(Song, Evaluation.song_id == Song.id)
                .where(User.name == user_name)
                .order_by(desc(Evaluation.created_at))
                .limit(limit)
            )
            rows = session.execute(stmt).all()

        records = []
        for evaluation, song in rows:
            records.append(
                {
                    "id": evaluation.id,
                    "song_title": song.title,
                    "cover_filename": evaluation.cover_filename,
                    "final_score": evaluation.final_score,
                    "grade": evaluation.grade,
                    "mfcc_error": evaluation.mfcc_error,
                    "energy_error": evaluation.energy_error,
                    "rop_error": evaluation.rop_error,
                    "singing_power_ratio": evaluation.singing_power_ratio,
                    "delta_pitch_error": evaluation.delta_pitch_error,
                    "median_pitch_error": evaluation.median_pitch_error,
                    "alignment_path_length": evaluation.alignment_path_length,
                    "created_at": evaluation.created_at,
                }
            )
        return records

    def list_user_names(self) -> list[str]:
        with self.session() as session:
            return list(session.scalars(select(User.name).order_by(User.name)).all())
