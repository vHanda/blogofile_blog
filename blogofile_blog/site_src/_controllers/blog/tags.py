import os
import shutil
import operator
from blogofile.cache import bf

from . import blog, tools
from . import feed

def run():
    write_tags()

tagged_posts = {}

def sort_into_tags() :
    tags = set()
    for post in blog.iter_posts_published():
        tags = tags.union( post.tags )

    global tagged_posts
    for tag in tags:
        tag_posts = [ post for post in blog.iter_posts_published()
                       if tag in post.tags ]
        tagged_posts[tag] = tag_posts

def write_tags():
    """Write all the blog posts in tags"""
    blog.tag_dir = "tag"
    root = bf.util.path_join(blog.path, blog.tag_dir)

    sort_into_tags()

    for tag, posts in tagged_posts.items():
        #Write tag RSS feed
        rss_path = bf.util.fs_site_path_helper( blog.path, blog.tag_dir,
                                                tag, "feed" )
        feed.write_feed(posts,rss_path, "rss.mako")
        atom_path = bf.util.fs_site_path_helper( blog.path, blog.tag_dir,
                                                 tag, "feed", "atom" )
        feed.write_feed(posts, atom_path, "atom.mako")
        page_num = 1
        while True:
            path = bf.util.path_join(root, tag, #Maybe use tag.urlname?
                                     str(page_num), "index.html")
            # Splice the lists accordingly
            page_posts = posts[:blog.posts_per_page]
            posts = posts[blog.posts_per_page:]

            #Forward and back links
            if page_num > 1:
                prev_link = bf.util.site_path_helper(
                    blog.path, blog.tag_dir, tag,
                                           str(page_num - 1))
            else:
                prev_link = None
            if len(posts) > 0:
                next_link = bf.util.site_path_helper(
                    blog.path, blog.tag_dir, tag,
                                           str(page_num + 1))
            else:
                next_link = None

            env = {
                "tag": tag,
                "posts": page_posts,
                "prev_link": prev_link,
                "next_link": next_link
            }
            tools.materialize_template("chronological.mako", path, env)

            #Copy tags/1 to tags/index.html
            if page_num == 1:
                shutil.copyfile(
                        bf.util.path_join(bf.writer.output_dir, path),
                        bf.util.path_join(
                                bf.writer.output_dir, root, tag,
                                "index.html"))
            #Prepare next iteration
            page_num += 1
            if len(posts) == 0:
                break
