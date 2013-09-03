$.fn.passwordMeter = function(value, minLength, label) {
	var expressions = [
		{
			regex: /[a-z]+/,
			uniqueChars: 26,
			difficulty: 1
		},
		{
			regex: /[A-Z]+/,
			uniqueChars: 26,
			difficulty: 2
		},
		{
			regex: /[0-9]+/,
			uniqueChars: 10,
			difficulty: 3
		},
		{
			regex: /[!.@$£#*()%~<>{}\[\]]+/,
			uniqueChars: 17,
			difficulty: 4
		}
	];
	
	var quality = 0;
	var bestQuality = (26 + 52 + 30) * 30;
	
	for (var i = 0; i < expressions.length; i ++) {
		var expression = expressions[i];

		if (expression.regex.exec(value)) {
			quality += (expression.uniqueChars * expression.difficulty);
		}
	}
	
	quality = Math.floor(quality, bestQuality);
	var percentage = (quality * 30) / bestQuality * 100;
	
	$(this).removeClass('strong medium weak useless').stop().animate(
		{
			width: percentage + '%'
		}
	);
	
	if (percentage > 75 && value.length >= minLength) {
		label.html('Big and strong');
		$(this).addClass('strong');
	} else if (percentage > 50 && value.length >= minLength) {
		label.html('Looking good');
		$(this).addClass('medium')
	} else if (percentage > 25 && value.length >= minLength) {
		label.html('Needs beefing up');
		$(this).addClass('weak');
	} else if (value.length >= minLength) {
		label.html('Weak sauce');
		$(this).addClass('useless');
	} else {
		label.html('Not long enough');
		$(this).addClass('useless');
	}
};

$.fn.checkUsername = function(div) {
	if(!$(this).val()) {
		div.addClass('fail').removeClass('ok').find('.label').html(
			'Not valid'
		);
		
		return;
	}
	
	$.ajax(
		{
			url: '/api/check-username/?username=' + $(this).val(),
			dataType: 'json',
			context: div,
			success: function(data) {
				if(data) {
					$(this).addClass('ok').removeClass('fail').find('.label').html(
						'Valid username'
					);
				} else {
					$(this).addClass('fail').removeClass('ok').find('.label').html(
						'Already taken'
					);
				}
			}
		}
	);
};

$(document).ready(
	function() {
		$('#id_signup-username').bind('change',
			function(e) {
				$(this).checkUsername(
					$('#username-check')
				);
			}
		);
		
		if($('#id_signup-username').val()) {
			$('#id_signup-username').checkUsername(
				$('#username-check')
			);
		}
		
		$('#id_signup-password').bind('keypress',
			function(e) {
				$('#password-meter .progress').passwordMeter(
					$(this).val(), 7, $('#password-meter .label')
				);
			}
		);
		
		if($('#id_signup-password').val()) {
			$('#password-meter .progress').passwordMeter(
				$('#id_signup-password').val(), 7, $('#password-meter .label')
			);
		}
	}
);