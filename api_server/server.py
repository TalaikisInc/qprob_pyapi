from functools import lru_cache
from os import getpid
from subprocess import call
import datetime

import asyncio
import uvloop
from sanic import Sanic
from sanic_compress import Compress
from sanic.response import (json, html)
from sanic.exceptions import NotFound
from aoiklivereload import LiveReloader
from aiomysql import create_pool, DictCursor
from django.utils.html import strip_tags

import settings


today = datetime.datetime.now()
period = datetime.datetime(today.year, today.month, today.day) - datetime.timedelta(days=2)
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()
app = Sanic(__name__)
Compress(app)
app.config.KEEP_ALIVE = False
app.pids = []
reloader = LiveReloader()
reloader.start_watcher_thread()


@app.listener("before_server_start")
async def get_pool(app, loop):
    app.pool = {"aiomysql": await create_pool(host=settings.DATABASE_HOST, port=settings.DATABASE_PORT,
        user=settings.DATABASE_USER, password=settings.DATABASE_PASSWORD,
        db=settings.DATABASE_NAME, maxsize=5)}


@lru_cache(maxsize=None)
@app.route("/", methods=["GET"])
async def home(request):
    return html(settings.REDIRECT_HTML)


@lru_cache(maxsize=None)
@app.route("/posts/", methods=["GET"])
async def posts(request):
    results = []
    async with app.pool['aiomysql'].acquire() as conn:
        async with conn.cursor(DictCursor) as cur:
            await cur.execute("SELECT title, slug, url, summary, date, \
                sentiment, image, category_id FROM aggregator_post \
                ORDER BY date DESC  LIMIT 100;")
            async for row in cur:
                results.append({"title": row["title"],
                    "slug": row["slug"],
                    "url": row["url"],
                    "summary": strip_tags(row["summary"] or ""),
                    "date": row["date"],
                    "sentiment": row["sentiment"] or "N/A",
                    "image": row["image"],
                    "category_id": row["category_id"] })
            return json({'data': results })


@lru_cache(maxsize=None)
@app.route("/cats/", methods=["GET"])
async def cats(request):
    async with app.pool['aiomysql'].acquire() as conn:
        async with conn.cursor(DictCursor) as cur:
            await cur.execute("SELECT title, slug FROM aggregator_category;")
            value = await cur.fetchall()
            return json({'data': value })


@lru_cache(maxsize=None)
@app.route("/posts/<cat_slug>/", methods=["GET"])
async def posts_by_cat(request, cat_slug):
    results = []
    async with app.pool['aiomysql'].acquire() as conn:
        async with conn.cursor(DictCursor) as cur:
            await cur.execute("SELECT posts.title, posts.slug, posts.url, \
                posts.summary, posts.date AS dt, posts.category_id, posts.sentiment, posts.image, \
                cats.slug AS cat FROM aggregator_post AS posts INNER JOIN \
                aggregator_category AS cats ON posts.category_id = cats.title \
                WHERE cats.slug=%s ORDER BY dt DESC LIMIT 100;", (cat_slug,))
            async for row in cur:
                results.append({"title": row["title"],
                    "slug": row["slug"],
                    "url": row["url"],
                    "summary": strip_tags(row["summary"] or ""),
                    "date": row["dt"],
                    "sentiment": row["sentiment"] or "N/A",
                    "image": row["image"],
                    "category_id": row["category_id"],
                    "category_slug": row["cat"] })
            return json({'data': results })


@lru_cache(maxsize=None)
@app.route("/post/<slug>/", methods=["GET"])
async def post_by_id(request, slug):
    results = []
    async with app.pool['aiomysql'].acquire() as conn:
        async with conn.cursor(DictCursor) as cur:
            await cur.execute("SELECT title, slug, url, summary, date, \
                sentiment, image, category_id FROM aggregator_post \
                WHERE slug=%s;", (slug,))
            async for row in cur:
                results.append({"title": row["title"],
                    "slug": row["slug"],
                    "url": row["url"],
                    "summary": strip_tags(row["summary"] or ""),
                    "date": row["date"],
                    "sentiment": row["sentiment"] or "N/A",
                    "image": row["image"],
                    "category_id": row["category_id"] })
            return json({'data': results })


@lru_cache(maxsize=None)
@app.route("/today/", methods=["GET"])
async def post_by_id(request):
    results = []
    async with app.pool['aiomysql'].acquire() as conn:
        async with conn.cursor(DictCursor) as cur:
            await cur.execute("SELECT title, slug, url, summary, date, \
                sentiment, image, category_id FROM aggregator_post \
                WHERE date > %s ORDER BY date DESC;", (period),)
            async for row in cur:
                results.append({"title": row["title"],
                    "slug": row["slug"],
                    "url": row["url"],
                    "summary": strip_tags(row["summary"] or ""),
                    "date": row["date"],
                    "sentiment": row["sentiment"] or "N/A",
                    "image": row["image"],
                    "category_id": row["category_id"] })
            return json({'data': results })


# EXPERIMENTAL
@app.route("/admin/<api_key>/<name>/kill_server")
async def pids(request, api_key, name):
    request.app.pids.append(getpid())
    if api_key == settings.API_KEY:
        if not settings.DEV_ENV:
            call(["/sbin/stop", "a{}".format(name)])
        for pid in request.app.pids:
            call(["/bin/kill", "-9", "{}".format(pid)])


loop.close()
