{% extends 'posts/question.inc.js' %}

{% block onclick %}
	$('article[data-id="{{ post.pk }}"] form input[type="radio"]').bind('click',
		function(e) {
			$(this).closest('form').submit();
		}
	);
{% endblock onclick %}