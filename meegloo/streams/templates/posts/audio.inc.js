{% if not nojq %}
jwplayer('post-{{ post.pk }}').setup(
	{
		'file': '{{ post.media.mp3.content|escapejs }}',
		{% if not nojq %}'width': $('#post-{{ post.pk }}').width(),{% endif %}
		'height': 30,
		'playButton': '',
		'skin': '{{ MEDIA_URL }}js/jwplayer/skins/modieus.zip',
		// icons: false,
		'provider': 'http',
		'http.startparam': 'start',
		'modes': [
			{
				'type': 'flash',
				'src': '{{ MEDIA_URL }}js/jwplayer/player.swf',
			},
			{
				'type': 'html5',
				'config': {
					file: '{{ post.media.mp3.content.url }}',
					provider: 'sound'
				}
			}
		],
	}
);
{% endif %}