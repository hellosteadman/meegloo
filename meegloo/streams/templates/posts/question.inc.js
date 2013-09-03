{% block onclick %}
	$('article[data-id="{{ post.pk }}"] form textarea').bind('keypress',
		function(e) {
			var code = e.charCode || e.keyCode;
			if(code == 13) {
				e.preventDefault();
				
				if($(this).val().trim() == '') {
					alert('Please enter an answer.');
					return;
				}
				
				$(this).closest('form').submit();
			}
		}
	);
{% endblock %}

{% block submit %}
	$('article[data-id="{{ post.pk }}"] form').bind('submit',
		function(e) {
			e.preventDefault();
			
			{% if not api %}
			$.ajax(
				{
					url: $(this).attr('action'),
					dataType: 'html',
					type: 'post',
					data: $(this).serialize(),
					context: $(this).closest('article').find('#answers-{{ post.pk }}'),
					success: function(data) {
						$(this).replaceWith(data);
						$('article[data-id="{{ post.pk }}"] form textarea').val('');
						$('article[data-id="{{ post.pk }}"] form input[type=radio]').attr('disabled', 'disabled');
					},
					error: function() {
						alert('Error');
					}
				}
			);
			{% else %}
			Titanium.App.fireEvent('questionAnswered',
				{
					answer: $(this).find(':input[name="answer"]').val()
				}
			);
			{% endif %}
		}
	);
{% endblock submit %}