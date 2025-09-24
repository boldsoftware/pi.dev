from typing import Any

from google.cloud.firestore import Client, FieldFilter

from podcast_generator.server.server_config import MAX_TRY_COUNT


def stuck_repos_core(db: Client) -> list[dict[str, Any]]:
    snapshots = list(
        db.collection("repos")
        .where(
            filter=FieldFilter(
                "tryCount",
                ">=",
                MAX_TRY_COUNT,
            )
        )
        .stream()
    )

    return list(
        filter(None, [snapshot.to_dict() for snapshot in snapshots if snapshot.exists])
    )
