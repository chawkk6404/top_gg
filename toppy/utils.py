from __future__ import annotations

from typing import Any, Type, TypeVar, Awaitable, Generic

from aiohttp import web


__all__ = (
    'AsyncContextManager',
    'MISSING',
    'run_webhook_server'
)


T = TypeVar('T')


class _MissingSentinel:
    def __eq__(self, other):
        return False

    def __bool__(self):
        return False

    def __hash__(self):
        return 0

    def __repr__(self):
        return '...'

    def __getattr__(self, item):
        pass


MISSING: Any = _MissingSentinel()
    
    
class AsyncContextManager(Generic[T]):
    def __init__(self, awaitable: Awaitable[T]):
        self.awaitable = awaitable
        self.ret: T = MISSING

    def __await__(self):
        self.awaitable.__await__()

    async def __aenter__(self):
        self.ret = await self.awaitable
        try:
            return self.ret.__aenter__()
        except AttributeError:
            return self.ret

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            return await self.ret.__aexit__(exc_typ, exc_val, exc_tb)
        except AttributeError:
            return False


async def run_webhook_server(application: web.Application, site_class: Type[web.BaseSite] = web.TCPSite,
                             **kwargs) -> web.BaseSite:
    """
    Run the webhook server created in `create_webhook_server`

    Parameters
    -----------
    application: :class:`aiohttp.web.Application`
        The application to run.
    site_class: :class:`aiohttp.web.BaseSite`
        The site for the application. Must have all methods from :class:`aiohttp.web.BaseSite`.
        Defaults to :class:`web.TCPSite`
    **kwargs:
        The kwargs to pass into ``site_class``.

    Returns
    --------
    The instance of the site class passed into `site_class`.
    """
    runner = web.AppRunner(application)
    await runner.setup()

    site = site_class(runner, **kwargs)
    await site.start()

    return site
