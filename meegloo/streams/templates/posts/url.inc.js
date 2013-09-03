{% if not nojq %}
	{% load oembed %}

	{% for embeddable in post.embeddables.all %}
		{% oembed embeddable.url embeddable.tag %}
	{% endfor %}
{% endif %}