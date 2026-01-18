import datetime
import os

from feedgen.feed import FeedGenerator
from markdown_it import MarkdownIt
from staticpipes.checks.html_tags import CheckHtmlTags
from staticpipes.checks.internal_links import CheckInternalLinks
from staticpipes.config import Config
from staticpipes.current_info import CurrentInfo
from staticpipes.jinja2_environment import Jinja2Environment
from staticpipes.pipe_base import BasePipe
from staticpipes.pipes.collection_records_process import PipeCollectionRecordsProcess
from staticpipes.pipes.copy import PipeCopy
from staticpipes.pipes.copy_with_versioning import PipeCopyWithVersioning
from staticpipes.pipes.exclude_underscore_directories import (
    PipeExcludeUnderscoreDirectories,
)
from staticpipes.pipes.jinja2 import PipeJinja2
from staticpipes.process_base import BaseProcessor
from staticpipes.processes.jinja2 import ProcessJinja2
from staticpipesdatatig.pipes.datatig_write_staticsite_output import (
    PipeDatatigStaticSite,
)
from staticpipesdatatig.pipes.load_datatig import PipeLoadDatatig


def render_markdown(content):
    md = MarkdownIt()
    return md.render(content) if content else ""


def date_format(content, format):
    d = datetime.datetime.fromisoformat(content)
    return d.strftime(format)


jinja2_environment = Jinja2Environment(
    filters={"date_format": date_format, "render_markdown": render_markdown}
)


class PipeBuildContext(BasePipe):

    def start_build(self, current_info: CurrentInfo) -> None:

        # URLs
        blog_urls = {}
        blog_dirs_files = {}
        for blog in current_info.get_context("collection")["blog"].get_records():
            date_bits = (
                blog.get_data()["published_at"]["value_iso"].split("T")[0].split("-")
            )
            blog_urls[blog.get_id()] = (
                "/"
                + date_bits[0]
                + "/"
                + date_bits[1]
                + "/"
                + date_bits[2]
                + "/"
                + blog.get_id()[11:]
                + ".html"
            )
            blog_dirs_files[blog.get_id()] = (
                "/" + date_bits[0] + "/" + date_bits[1] + "/" + date_bits[2],
                blog.get_id()[11:] + ".html",
            )

        current_info.set_context("blog_urls", blog_urls)
        current_info.set_context("blog_dirs_files", blog_dirs_files)

        # blogs posts
        blogs = current_info.get_context("collection").get("blog").get_records()
        blogs = sorted(
            list(blogs),
            key=lambda x: x.get_data().get("published_at").get("value_timestamp"),
            reverse=True,
        )
        current_info.set_context("blogs_sorted", blogs)


class ChangeBlogPostURLProcess(BaseProcessor):

    def process_source_file(
        self,
        source_dir,
        source_filename,
        process_current_info,
        current_info,
    ):

        process_current_info.dir, process_current_info.filename = (
            current_info.get_context("blog_dirs_files")[
                process_current_info.context["blog_id"]
            ]
        )


class PipeRSSAndAtomFeed(BasePipe):

    def start_build(self, current_info: CurrentInfo) -> None:

        fg = FeedGenerator()
        fg.title("DataTig")
        fg.id("https://www.datatig.com/")
        fg.link(href="https://www.datatig.com/blogs.xml", rel="self")
        fg.generator(generator="StaticPipes")
        fg.description(
            "DataTig helps when a community of people want to crowd source a data set and they use a git repository to store the data."  # noqa
        )

        for blogs in current_info.get_context("collection").get("blog").get_records():
            fe = fg.add_entry()
            fe.id(
                "https://staticpipes.teacaketech.scot/blogs/{}/".format(blogs.get_id())
            )
            fe.title(blogs.get_data().get("title").get("value"))
            fe.summary(blogs.get_data().get("description").get("value"))
            fe.pubDate(pubDate=blogs.get_data().get("published_at").get("value_iso"))
            fe.updated(updated=blogs.get_data().get("updated_at").get("value_iso"))
            fe.link(
                href="https://www.datatig.com{}".format(
                    current_info.get_context("blog_urls")[blogs.get_id()]
                ),
                rel="alternate",
            )

        self.build_directory.write("/", "blogs.xml", fg.rss_str(pretty=True))


config = Config(
    pipes=[
        PipeExcludeUnderscoreDirectories(),
        PipeCopyWithVersioning(extensions=["css"], directories=["css"]),
        PipeCopyWithVersioning(directories=["images"], extensions=["png"]),
        PipeCopy(directories=["fontawesome-free-6.7.2-web"]),
        PipeLoadDatatig(),
        PipeBuildContext(),
        PipeJinja2(jinja2_environment=jinja2_environment),
        PipeCollectionRecordsProcess(
            collection_name="blog",
            processors=[
                ProcessJinja2(
                    template="_layouts/blog.html",
                    jinja2_environment=jinja2_environment,
                ),
                ChangeBlogPostURLProcess(),
            ],
            output_dir="blogs",
            output_mode="dir",
            context_key_record_id="blog_id",
            context_key_record_data="blog",
        ),
        PipeRSSAndAtomFeed(),
        PipeDatatigStaticSite(output_dir="datatig_for_this_website"),
    ],
    checks=[CheckInternalLinks(), CheckHtmlTags()],
    context={},
)

if __name__ == "__main__":
    from staticpipes.cli import cli

    cli(
        config,
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "src"),
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "_site"),
    )
