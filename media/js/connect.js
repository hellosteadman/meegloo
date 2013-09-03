$(document).ready(
	function() {
		$.ajax(
			{
				url: CONNECT_URL,
				dataType: 'json',
				context: $('article.page form'),
				success: function(data) {
					$(this).animate(
						{
							opacity: 0
						},
						function() {
							$(this).html('<table class="friends"><thead><th class="follow">Follow</th><th colspan="2">Friend</th></thead><tbody></tbody></table>');
							for(var i = 0; i < data.length; i ++) {
								var klass = data[i].following ? 'following' : 'not-following';
								var input = '<input type="checkbox" name="' + data[i].username + '"';
								var img = '<img src="' + data[i].image + '" width="48" height="48" />';
								var html = '<tr class="' + klass + '"';
								
								if(data[i].username) {
									html += ' data-username="' + data[i].username + '"';
								}
														
								if(data[i].following) {
									input += ' disabled="disabled" checked="checked"';
								}
								
								input += ' />';
								html += '><td class="follow">' + input + '</td>' + '<td class="avatar">' + img + '</td>';
								html += '<td class="name"><span>';
								
								if(data[i].show_username) {
									html += '<strong>' + data[i].username + '</strong><br />';
								}
								
								html += data[i].full_name
								html += '</span></td></tr>';
								
								$(this).find('table tbody').append(html);
							}
							
							$(this).find('.friends tr.not-following input').bind('change',
								function(e) {
									var username = $(this).closest('tr').attr('data-username')
									
									$.ajax(
										{
											url: CONNECT_URL,
											dataType: 'text',
											type: 'POST',
											data: 'username=' + escape(username),
											context: $(this),
											success: function(data) {
												$(this).closest('tr').removeClass('not-following').addClass('following');
												$(this).animate(
													{
														opacity: 0
													}
												);
											}
										}
									);
								}
							);
							
							$(this).animate(
								{
									opacity: 1
								}
							);
						}
					);
				}
			}
		);
	}
);