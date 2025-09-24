from podcast_generator.server.get_github_repo_id import get_github_repo_id


def get_github_doc_ref(db, owner, name):
    repo_id = get_github_repo_id(owner, name)
    return db.document(f"repos/{repo_id}")
