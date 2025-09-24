from datetime import datetime
from urllib.parse import urlencode

from google.cloud.firestore import Client, Query
from google.cloud.storage.bucket import Bucket
from markdown import markdown

from podcast_generator.server.episode import Episode
from podcast_generator.server.gcs_utils import upload_blob_from_string
from podcast_generator.server.generate_placeholder_episode import (
    generate_placeholder_episode,
)
from podcast_generator.server.generate_podcast_image import generate_podcast_image
from podcast_generator.server.get_github_doc_ref import get_github_doc_ref
from podcast_generator.server.get_shows_gcs_path import (
    get_feed_gcs_path,
    get_show_logo_public_url,
)


def update_rss_feed(
    public_bucket: Bucket,
    db: Client,
    owner: str,
    name: str,
    *,
    regenerate_logo: bool = False,
):
    doc_ref = get_github_doc_ref(db, owner, name)
    episodes = [
        Episode.from_doc(episode_doc.to_dict())
        for episode_doc in doc_ref.collection("episodes")
        .order_by("createdAt", direction=Query.DESCENDING)
        .stream()
    ]

    is_initial = not episodes

    if is_initial:
        episodes = [generate_placeholder_episode(public_bucket, db, owner, name)]

    if is_initial or regenerate_logo:
        generate_podcast_image(public_bucket, owner, name)

    update_rss_feed_internal(
        public_bucket,
        owner,
        name,
        episodes,
        is_initial=is_initial,
    )


def update_rss_feed_internal(
    public_bucket: Bucket,
    owner: str,
    name: str,
    episodes: list[Episode],
    *,
    is_initial: bool,
):
    repo = f"{owner}/{name}"
    # Initialize the Podcast
    podcast_xml = get_podcast_xml(
        title=f"{owner}/{name} by pi.dev",
        link=f"https://pi.dev/github.com/{owner}/{name}/readme",
        language="en-us",
        author="The pi.dev AI",
        description=f"An AI-generated podcast keeping you up-to-date on the latest changes in the {owner}/{name} repository.",
        image_url=get_show_logo_public_url(public_bucket, owner, name),
        copyright_year=datetime.now().year,
        copyright_owner="Bold, Inc.",
        episodes_xml="\n".join(
            get_episode_xml(repo, index, episode)
            for index, episode in enumerate(episodes)
        ),
        repo=repo,
    )

    # Upload to Google Cloud Storage
    path = get_feed_gcs_path(owner, name)
    upload_blob_from_string(
        public_bucket, path, podcast_xml, content_type="application/rss+xml"
    )

    # Set cache control to 1 minute if this is the initial feed
    blob = public_bucket.blob(str(path))
    blob.cache_control = (
        "public, max-age=60, must-revalidate" if is_initial else "public, max-age=3600"
    )
    blob.patch()


def get_podcast_xml(
    *,
    title,
    link,
    language,
    author,
    description,
    image_url,
    copyright_year,
    copyright_owner,
    episodes_xml,
    repo,
):
    return f"""\
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>{title}</title>
    <link>{link}</link>
    <language>{language}</language>
    <copyright>&#169; {copyright_year} {copyright_owner}</copyright>
    <itunes:author>{author}</itunes:author>
    <description>
      {description} We would love your feedback! {get_feedback_url(repo, None)}
    </description>
    <itunes:type>episodic</itunes:type>
    <itunes:image
      href="{image_url}"
    />
    <itunes:category text="Technology">
    </itunes:category>
    <itunes:explicit>false</itunes:explicit>
    {episodes_xml}
  </channel>
</rss>
"""


def get_episode_xml(repo: str, index: int, episode: Episode) -> str:
    return f"""\
    <item>
      <itunes:episodeType>full</itunes:episodeType>
      <itunes:episode>{index}</itunes:episode>
      <title>{episode.name}</title>
      <description>
        <![CDATA[
        <p>
        {markdown(episode.description)}
        </p>

        <p>
        We love <a href="{get_feedback_url(repo, episode.name)}">feedback</a>!
        </p>
        ]]>
      </description>
      <enclosure
        url="{episode.url}"
        length="{episode.length}"
        type="audio/mpeg"
      />
      <guid>{episode.guid}</guid>
      <pubDate>{episode.publication_date.strftime('%a, %d %b %Y %H:%M:%S GMT')}</pubDate>
      <itunes:duration>{episode.duration}</itunes:duration>
      <itunes:explicit>false</itunes:explicit>
    </item>
    """


def get_feedback_url(repo: str, name: str | None) -> str:
    query_params = {"repo": repo}
    if name:
        query_params["episode"] = name
    return f"https://pi.dev/feedback?{urlencode(query_params)}"
