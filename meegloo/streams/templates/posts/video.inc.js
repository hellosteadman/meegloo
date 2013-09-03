{% if not nojq and not api %}
	{% load thumbnail %}
	var parent_{{ post.pk }} = $('#post-{{ post.pk }}').parent();
	var width_{{ post.pk }} = $('#post-{{ post.pk }}').width();
	var height_{{ post.pk }} = width_{{ post.pk }} / 640 * 360;
	jwplayer('post-{{ post.pk }}').setup(
		{
			'file': '{{ post.media.mp4.content|escapejs }}',
			{% thumbnail post.media.image.content '640x360' crop='center' as thumb %}
			'image': '{{ thumb.url|escapejs }}',
			{% endthumbnail %}
			'width': $('#post-{{ post.pk }}').width(),
			'height': $('#post-{{ post.pk }}').width() / 640 * 360,
			'skin': '{{ MEDIA_URL }}js/jwplayer/skins/modieus.zip',
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
						'file': '{{ post.media.mp4.content.url }}',
						'provider': 'video'
					}
				}
			]
		}
	);
	
	$(window).resize(
		function() {
			jwplayer('post-{{ post.pk }}').resize(
				parent_{{ post.pk }}.width() - 10 - 42,
				(parent_{{ post.pk }}.width() - 10 - 42) / width_{{ post.pk }} * height_{{ post.pk }}
			);
		}
	);
{% endif %}