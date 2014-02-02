from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('series', '/series')
    config.add_route('series_view', '/series/view/{id}')
    config.add_route('series_delete', '/series/delete/{id}')
    config.add_route('series_edit', '/series/edit/{id}')
    
    config.scan()
    return config.make_wsgi_app()
