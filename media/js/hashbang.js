$.fn.bang = function(fn) {
	return fn ? this.bind('bang', fn) : this.trigger('bang');
}

function hashbang(method, form, hash) {
	if(form) {
		data = form.serialize();
	} else {
		data = {}
	}
	
	hash = hash ? hash : window.location.hash;
	if(hash.substr(0, 2) == '#!') {
		url = hash.substr(2);
	} else {
		alert('Invalid hashbang URL: ' + url);
		return
	}
	
	if(url.indexOf('?') > -1) {
		url += '&hashbang=1';
	} else {
		url += '?hashbang=1';
	}
	
	$.ajax(
		{
			url: url,
			type: method,
			dataType: 'html',
			data: data,
			success: function(data) {
				try {
					console.log(method + ' ' + url);
				} catch (err) {
					
				}
				
				if(method == 'POST') {
					window.location = '#!' + url.replace(
						'&hashbang=1', ''
					).replace(
						'?hashbang=1', ''
					);
				}
				
				$('#bang').html(data);
				$(document).bang();
			},
			error: function() {
				alert(
					'Sorry, it was not psosible to complete your request.' +
					'Please try again.'
				);
			}
		}
	);
}

$(document).bang(
	function(e) {
		$('a[href^="/"]').not('.fancybox, .delete-confirm').each(
			function() {
				$(this).attr('href', '#!' + $(this).attr('href'));
			}
		);
		
		$('form[action^="/"]').not('.chat').bind('submit',
			function(e) {
				e.preventDefault();
				hashbang('POST', $(this), '#!' + $(this).attr('action'));
			}
		);
		
		$('form[action=""]').not('.chat').bind('submit',
			function(e) {
				url = window.location.toString();
				if(url.indexOf('#!') > -1) {
					e.preventDefault();
					url = url.substr(url.indexOf('#!') + 2);
					hashbang('POST', $(this), '#!' + url);
				} else {
					alert(url);
				}
			}
		);
	}
);

$(document).ready(
	function() {
		$(window).hashchange(
			function(e) {
				if(window.location.hash.substr(0, 2) == '#!') {
					hashbang('GET');
				}
			}
		);
	}
);