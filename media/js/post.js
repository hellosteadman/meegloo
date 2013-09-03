var postType = 'text';

$(document).ready(
	function() {
		$('#postbox textarea').bind('focus',
			function(e) {
				$(this).closest('form').find('.uploadify, .buttons, .chars-remaining').show();
				
				$(this).animate(
					{
						height: '3em'
					}
				);
			}
		);
		
		$('#postbox textarea').bind('keyup',
			function(e) {
				if($(this).val().length > 200) {
					$(this).val($(this).val().substr(0, 200));
				}
				
				var remaining = 200 - $(this).val().length;
				$(this).parent().find('.chars-remaining').html(
					remaining + ' character' + (remaining != 1 ? 's' : '') + ' left'
				);
			}
		);
		
		$('#postbox textarea').bind('keypress',
			function(e) {
				var code = e.charCode || e.keyCode;
				if(code == 13) {
					var val = $(this).val().trim();
					var q = val.substr(val.length - 1);
					
					if(q != '?' && postType == 'text') {
						e.preventDefault();
						$(this).closest('form').submit();
						$('.question-hint').fadeOut();
						postType = 'text';
					} else {
						val = $(this).val();
						if(val.substr(val.length - '\n'.length) == '\n') {
							e.preventDefault();
							$(this).closest('form').submit();
							$('.question-hint').fadeOut();
						} else if(val.substr(val.length - '\r'.length) == '\r') {
							e.preventDefault();
							$(this).closest('form').submit();
							$('.question-hint').fadeOut();
						} else if(val.substr(val.length - '\r\n'.length) == '\r\n') {
							e.preventDefault();
							$(this).closest('form').submit();
							$('.question-hint').fadeOut();
						} else {
							$('.question-hint').fadeIn();
							postType = 'question';
						}
					}
				}
			}
		);
		
		$('#postbox input[type="file"]').uploadify(
			{
				uploader: '/media/js/uploadify/uploadify.swf',
				script: '/uploadify/upload/',
				scriptData: {
					user: user_id,
					guid: guid
				},
				buttonImg: '/media/img/uploadify.png',
				cancelImg: '/media/js/uploadify/cancel.png',
				width: 68,
				height: 10,
				scriptAccess: 'always',
				fileExt: extensions,
				fileDesc: 'Choose a file to upload',
				onSelect: function(e) {
					$('#postbox form').attr('data-uploadify', 'true');
				},
				onCancel: function(e) {
					$('#postbox form').removeAttr('data-uploadify');
				},
				onAllComplete: function(e, data) {
					if(data.errors && data.errors > 0) {
						return;
					} else {
						$('#postbox form').removeAttr('data-uploadify');
						$('#postbox form').submit();
						$('#postbox input[type="file"]').uploadifyClearQueue();
					}
				}
			}
		);
		
		$('#postbox form #id_geotag').bind('click',
			function(e) {
				if($(this).attr('checked')) {
					$.geolocation.find(
						function(v) {
							$('#id_latitude').val(v.latitude);
							$('#id_longitude').val(v.longitude);
						}
					);
				} else {
					$('#id_latitude').val('');
					$('#id_longitude').val('');
				}
			}
		);
		
		$('#postbox form #id_tweet').button();
		$('#postbox form #id_geotag').button(
			{
				disabled: !$.support.geolocation()
			}
		);
		
		$('#postbox form').bind('submit',
			function(e) {
				e.preventDefault();
				
				if($(this).attr('data-uploadify')) {
					$(this).find('input[type="file"]').uploadifyUpload();
					return;
				}
				
				$.ajax(
					{
						url: $(this).attr('action'),
						data: $(this).serialize(),
						type: $(this).attr('method'),
						context: $(this),
						dataType: 'json',
						success: function(data) {
							if('errors' in data) {
								$(this).find('input[name="guid"]').val(
									data.guid
								);
								
								$(this).find('input[type="file"]').uploadifySettings(
									'scriptData', 
									{
										user: user_id,
										guid: data.guid
									}
								);
								
								if('__all__' in data.errors) {
									alert(data.errors.__all__);
								} else {
									var errors = [];
									for(var key in data.errors) {
										errors.push(key + ': ' + data.errors[key]);
									}
									
									alert(errors.join('\n'));
								}
							} else {
								$(this).find('textarea').val('');
								$(this).find('input[name="guid"]').val(
									data.guid
								);
								
								$(this).find('input[name="kind"]').val('text');
								
								$(this).find('input[type="file"]').uploadifySettings(
									'scriptData', 
									{
										user: user_id,
										guid: data.guid
									}
								);
								
								clearTimeout(checkTimeout);
								checkLatest();
								
								postType = 'text';
							}
						}
					}
				);
			}
		);
		
		$('#embed-stream input').bind('click',
			function(e) {
				$(this).select();
			}
		);
	}
);