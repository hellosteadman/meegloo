{% if handler and url and div_id %}
$('#{{ div_id }}').load(
	'http://{{ request.network.domain }}{% url oembed_html handler %}?url={{ url|urlencode }}&amp;width=' + $('#{{ div_id }}').width()
);
{% endif %}