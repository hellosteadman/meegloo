{% if latest_id %}
latest_id = {{ latest_id }};
try { console.log(latest_id); } catch(err) { }
{% endif %}

{% for post in posts.object_list %}
	{% include post.js_template_name %}
{% endfor %}