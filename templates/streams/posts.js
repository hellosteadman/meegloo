{% if not request.is_ajax and not request.GET.callback %}
	meegloo_checkInterval_{{ container_id }} = 3000;
	meegloo_checkTimer_{{ container_id }} = null;
	{% if latest_id %}meegloo_latestID_{{ container_id }} = {{ latest_id }};{% endif %}
	
	function meegloo_recheck_{{ container_id }}() {
		var script = document.createElement('script');
		script.src = 'http://{{ request.profile.username }}.{{ request.network.domain }}{% if stream.part_of %}{% url embed_stream stream.part_of.slug %}{% else %}{% url embed_stream stream.slug %}{% endif %}?since=' + meegloo_latestID_{{ container_id }} + '&callback=meegloo_organise_{{ container_id }}&container={{ container_id }}&nocache=' + new Date().getTime();
		document.getElementsByTagName('head')[0].appendChild(script);
		
		try {
			console.log(script.src);
		} catch (err) { }
	}
	
	document.write('<div id="{{ container_id }}"></div><p style="text-align: right;">Powered by <a href="http://meegloo.com/" target="_blank">Meegloo</a></p>');
	var meegloo_container_{{ container_id }} = document.getElementById('{{ container_id }}');
	
	{% for post in posts.object_list %}
		var meegloo_article = document.createElement('div');
		meegloo_article.innerHTML = '{% filter escapejs %}{% include post.html_template_name with nojq='True' %}{% endfilter %}<hr />';
		meegloo_container_{{ container_id }}.appendChild(meegloo_article);
	{% endfor %}
	
	function meegloo_organise_{{ container_id }}(e) {
		if(e.elements.length > 0) {
			var meegloo_container_{{ container_id }} = document.getElementById('{{ container_id }}');
			var before = e.elements.join('<hr />');
			
			alert(before);
			alert(meegloo_container_{{ container_id }});
			meegloo_container_{{ container_id }}.innerHTML = before + meegloo_container_{{ container_id }}.innerHTML;
			
			meegloo_checkInterval_{{ container_id }} = 3000;
			if('latestID' in e) {
				meegloo_latestID_{{ container_id }} = e.latestID;
			}
		} else {
			meegloo_checkInterval_{{ container_id }} += 3000;
			
			try {
				console.log('No new itmes. Waiting for ' + (meegloo_checkInterval_{{ container_id }} / 1000) + ' seconds');
			} catch (err) { }
		}
		
		clearTimeout(meegloo_checkTimer_{{ container_id }});
		meegloo_checkTimer_{{ container_id }} = setTimeout(meegloo_recheck_{{ container_id }}, meegloo_checkInterval_{{ container_id }});
	}
	
	meegloo_checkTimer_{{ container_id }} = setTimeout(meegloo_recheck_{{ container_id }}, meegloo_checkInterval_{{ container_id }});
{% else %}
	{{ request.GET.callback }}(
		{
			elements: [{% for post in posts.object_list %}
				'{% filter escapejs %}{% include post.html_template_name with nojq='True' %}{% endfilter %}'
			{% if not forloop.last %},{% endif %}{% endfor %}]{% if latest_id %},
			latestID: {{ latest_id }}{% endif %}
		}
	);
{% endif %}