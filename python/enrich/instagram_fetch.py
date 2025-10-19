import random, time, re
try:
    import instaloader
except Exception:
    instaloader = None

from ..settings import INSTA_USERNAME, INSTA_PASSWORD, INSTA_MAX_POSTS

def fetch_profile(username_or_url):
    if not instaloader or not INSTA_USERNAME: return {}
    try:
        m = re.search(r"instagram\.com/([^/?#]+)", username_or_url or "", re.I)
        uname = (m.group(1) if m else (username_or_url or "")).strip("@/")
        L = instaloader.Instaloader(download_pictures=False, download_videos=False,
                                    save_metadata=False, post_metadata_txt_pattern="")
        L.login(INSTA_USERNAME, INSTA_PASSWORD)
        time.sleep(random.uniform(1.0,2.0))
        p = instaloader.Profile.from_username(L.context, uname)
        photos=[]
        for i, post in enumerate(p.get_posts(), start=1):
            photos.append(post.url)
            if i>=INSTA_MAX_POSTS: break
        return {"instagram_followers": p.followers, "photos_instagram": photos}
    except Exception as e:
        print(f"[Instagram] {username_or_url}: {e}")
        return {}
