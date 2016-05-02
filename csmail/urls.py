from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.contrib import admin
from csmail.settings import MEDIA_URL, MEDIA_ROOT

admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^$', 'csmail.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'cs.views.homepage', name="homepage"),
    url(r'^register$', 'cs.views.register', name="register"),
    url(r'^user/(?P<uuid>.+)$', 'cs.views.loguser', name="loguser"),
    url(r'^logout$', 'cs.views.logout', name="logout"),
    url(r'^panel$', 'cs.views.panel', name="panel"),
    url(r'^lambda/$', 'cs.views.aws_lambda', name="lambda"),
    url(r'^webhook/$', 'cs.views.webhook', name="webhook"),
    url(r'^playnow$', 'cs.views.playnow', name="playnow"),
    url(r'^submission/(?P<matchid>.+)$', 'cs.views.submission', name="submission"),
    url(r'^play/(?P<matchid>.+)/(?P<uuid>.+)$', 'cs.views.play', name="play"),
    url(r'^expire$', 'cs.views.expire', name="expire"),
    url(r'^tests$', 'cs.views.tests', name="tests"),
    url(r'^finalize$', 'cs.views.finalize', name="finalize"),
    url(r'^leaderboard$', 'cs.views.leaderboard', name="leaderboard"),
]


urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)