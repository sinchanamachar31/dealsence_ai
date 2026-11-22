import random

from backend.database.sim_db import SessionLocal
from backend.models.sim_models import SimActivityLog, SimComment, SimContent, SimCreator
from backend.scripts.demo_data import DEMO_CREATORS


BACKGROUND_NICHES = {
    "Healthy Food & Nutrition": (
        "food",
        "simple recipes and thoughtful pantry finds",
    ),
    "Clean Skincare & Beauty": (
        "beauty",
        "gentle skincare routines and ingredient notes",
    ),
    "Home Fitness & Strength": (
        "fitness",
        "mobility, home workouts, and recovery gear",
    ),
    "Tech & Student Productivity": (
        "tech",
        "budget desk setups and practical study tools",
    ),
    "Sustainable Home & Decor": (
        "home",
        "secondhand finds and lower-waste home styling",
    ),
}

FIRST_NAMES = [
    "Aarav", "Aditi", "Aisha", "Arjun", "Dev", "Diya", "Ira", "Ishaan",
    "Kabir", "Kavya", "Kiran", "Maya", "Neel", "Nisha", "Priya", "Rhea",
    "Samar", "Sana", "Tara", "Vihaan",
]

LAST_NAMES = [
    "Bhat", "Chandra", "Das", "Desai", "Ghosh", "Iyer", "Jain", "Kapoor",
    "Khanna", "Menon", "Nair", "Patel", "Rao", "Reddy", "Saxena", "Shah",
    "Singh", "Suri", "Verma", "Wadhwa",
]


def seed_database():
    db = SessionLocal()
    try:
        if db.query(SimCreator).count() > 0:
            print("Database already seeded")
            return

        for creator_data in DEMO_CREATORS:
            creator = SimCreator(
                handle=creator_data["handle"],
                display_name=creator_data["display_name"],
                login_email=creator_data["login_email"],
                niche=creator_data["niche"],
                platform=creator_data["platform"],
                bio=creator_data["bio"],
                avatar_url=creator_data["avatar_url"],
                follower_count=creator_data["follower_count"],
                engagement_rate=creator_data["engagement_rate"],
                is_demo_creator=True,
            )
            db.add(creator)
            db.flush()

            for item in creator_data["contents"]:
                comments = item["comments"]
                content = SimContent(
                    creator_id=creator.id,
                    content_slug=item["content_slug"],
                    media_type=item["media_type"],
                    category=item["category"],
                    thumbnail_path=item["thumbnail_path"],
                    video_path=item["video_path"],
                    caption=item["caption"],
                    views=item["views"],
                    likes=item["likes"],
                    comments_count=len(comments),
                )
                db.add(content)
                db.flush()

                for comment_data in comments:
                    db.add(
                        SimComment(
                            content_id=content.id,
                            author_handle=comment_data["author_handle"],
                            text=comment_data["text"],
                            intent_label=comment_data["intent_label"],
                        )
                    )

        content_pools = {
            niche: [
                item
                for creator_data in DEMO_CREATORS
                if creator_data["niche"] == niche
                for item in creator_data["contents"]
            ]
            for niche in BACKGROUND_NICHES
        }
        rng = random.Random(2026)
        creator_number = 0

        for niche, (handle_prefix, bio_topic) in BACKGROUND_NICHES.items():
            for niche_creator_number in range(1, 20):
                creator_number += 1
                name_index = creator_number - 1
                display_name = (
                    f"{FIRST_NAMES[name_index % len(FIRST_NAMES)]} "
                    f"{LAST_NAMES[(name_index // len(FIRST_NAMES)) % len(LAST_NAMES)]}"
                )
                handle = f"@community.{handle_prefix}{niche_creator_number:02d}"
                creator = SimCreator(
                    handle=handle,
                    display_name=display_name,
                    login_email=f"community.{handle_prefix}{niche_creator_number:02d}@example.com",
                    niche=niche,
                    platform="instagram",
                    bio=f"Sharing {bio_topic} for everyday inspiration.",
                    avatar_url=None,
                    follower_count=rng.randint(1200, 48000),
                    engagement_rate=round(rng.uniform(0.025, 0.085), 4),
                    is_demo_creator=False,
                )
                db.add(creator)
                db.flush()

                pool = content_pools[niche]
                for content_number, source_item in enumerate(
                    rng.sample(pool, rng.randint(2, 3)),
                    start=1,
                ):
                    content_slug = (
                        f"background_{creator_number:03d}_{content_number:02d}_"
                        f"{source_item['content_slug']}"
                    )
                    views = max(
                        300,
                        int(source_item["views"] * rng.uniform(0.08, 0.55)),
                    )
                    comment_data_list = rng.sample(
                        source_item["comments"],
                        rng.randint(2, 3),
                    )
                    content = SimContent(
                        creator_id=creator.id,
                        content_slug=content_slug,
                        media_type=source_item["media_type"],
                        category=source_item["category"],
                        thumbnail_path=source_item["thumbnail_path"],
                        video_path=source_item["video_path"],
                        caption=source_item["caption"],
                        views=views,
                        likes=max(1, int(views * rng.uniform(0.035, 0.11))),
                        comments_count=len(comment_data_list),
                    )
                    db.add(content)
                    db.flush()

                    for comment_data in comment_data_list:
                        db.add(
                            SimComment(
                                content_id=content.id,
                                author_handle=comment_data["author_handle"],
                                text=comment_data["text"],
                                intent_label=comment_data["intent_label"],
                            )
                        )

        db.add(
            SimActivityLog(
                event_type="seed_completed",
                description=(
                    "Seeded 5 demo creators and 95 background creators with "
                    "content and comments."
                ),
            )
        )
        db.commit()

        demo_creator_count = (
            db.query(SimCreator).filter_by(is_demo_creator=True).count()
        )
        total_creator_count = db.query(SimCreator).count()
        total_content_count = db.query(SimContent).count()
        total_comment_count = db.query(SimComment).count()
        print(f"Demo creators: {demo_creator_count}")
        print(f"Total creators: {total_creator_count}")
        print(f"Total contents: {total_content_count}")
        print(f"Total comments: {total_comment_count}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
