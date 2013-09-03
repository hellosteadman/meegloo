var LATIN_MAP = {
	'À': 'A', 'Á': 'A', 'Â': 'A', 'Ã': 'A', 'Ä': 'A', 'Å': 'A', 'Æ': 'AE', 'Ç':
	'C', 'È': 'E', 'É': 'E', 'Ê': 'E', 'Ë': 'E', 'Ì': 'I', 'Í': 'I', 'Î': 'I',
	'Ï': 'I', 'Ð': 'D', 'Ñ': 'N', 'Ò': 'O', 'Ó': 'O', 'Ô': 'O', 'Õ': 'O', 'Ö':
	'O', 'Ő': 'O', 'Ø': 'O', 'Ù': 'U', 'Ú': 'U', 'Û': 'U', 'Ü': 'U', 'Ű': 'U',
	'Ý': 'Y', 'Þ': 'TH', 'ß': 'ss', 'à':'a', 'á':'a', 'â': 'a', 'ã': 'a', 'ä':
	'a', 'å': 'a', 'æ': 'ae', 'ç': 'c', 'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e',
	'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i', 'ð': 'd', 'ñ': 'n', 'ò': 'o', 'ó':
	'o', 'ô': 'o', 'õ': 'o', 'ö': 'o', 'ő': 'o', 'ø': 'o', 'ù': 'u', 'ú': 'u',
	'û': 'u', 'ü': 'u', 'ű': 'u', 'ý': 'y', 'þ': 'th', 'ÿ': 'y'
}

var LATIN_SYMBOLS_MAP = {
	'©': '(c)'
}

var GREEK_MAP = {
	'α':'a', 'β':'b', 'γ':'g', 'δ':'d', 'ε':'e', 'ζ':'z', 'η':'h', 'θ':'8',
	'ι':'i', 'κ':'k', 'λ':'l', 'μ':'m', 'ν':'n', 'ξ':'3', 'ο':'o', 'π':'p',
	'ρ':'r', 'σ':'s', 'τ':'t', 'υ':'y', 'φ':'f', 'χ':'x', 'ψ':'ps', 'ω':'w',
	'ά':'a', 'έ':'e', 'ί':'i', 'ό':'o', 'ύ':'y', 'ή':'h', 'ώ':'w', 'ς':'s',
	'ϊ':'i', 'ΰ':'y', 'ϋ':'y', 'ΐ':'i',
	'Α':'A', 'Β':'B', 'Γ':'G', 'Δ':'D', 'Ε':'E', 'Ζ':'Z', 'Η':'H', 'Θ':'8',
	'Ι':'I', 'Κ':'K', 'Λ':'L', 'Μ':'M', 'Ν':'N', 'Ξ':'3', 'Ο':'O', 'Π':'P',
	'Ρ':'R', 'Σ':'S', 'Τ':'T', 'Υ':'Y', 'Φ':'F', 'Χ':'X', 'Ψ':'PS', 'Ω':'W',
	'Ά':'A', 'Έ':'E', 'Ί':'I', 'Ό':'O', 'Ύ':'Y', 'Ή':'H', 'Ώ':'W', 'Ϊ':'I',
	'Ϋ':'Y'
}

var TURKISH_MAP = {
	'ş':'s', 'Ş':'S', 'ı':'i', 'İ':'I', 'ç':'c', 'Ç':'C', 'ü':'u', 'Ü':'U',
	'ö':'o', 'Ö':'O', 'ğ':'g', 'Ğ':'G'
}

var RUSSIAN_MAP = {
	'а':'a', 'б':'b', 'в':'v', 'г':'g', 'д':'d', 'е':'e', 'ё':'yo', 'ж':'zh',
	'з':'z', 'и':'i', 'й':'j', 'к':'k', 'л':'l', 'м':'m', 'н':'n', 'о':'o',
	'п':'p', 'р':'r', 'с':'s', 'т':'t', 'у':'u', 'ф':'f', 'х':'h', 'ц':'c',
	'ч':'ch', 'ш':'sh', 'щ':'sh', 'ъ':'', 'ы':'y', 'ь':'', 'э':'e', 'ю':'yu',
	'я':'ya',
	'А':'A', 'Б':'B', 'В':'V', 'Г':'G', 'Д':'D', 'Е':'E', 'Ё':'Yo', 'Ж':'Zh',
	'З':'Z', 'И':'I', 'Й':'J', 'К':'K', 'Л':'L', 'М':'M', 'Н':'N', 'О':'O',
	'П':'P', 'Р':'R', 'С':'S', 'Т':'T', 'У':'U', 'Ф':'F', 'Х':'H', 'Ц':'C',
	'Ч':'Ch', 'Ш':'Sh', 'Щ':'Sh', 'Ъ':'', 'Ы':'Y', 'Ь':'', 'Э':'E', 'Ю':'Yu',
	'Я':'Ya'
}

var UKRAINIAN_MAP = {
	'Є':'Ye', 'І':'I', 'Ї':'Yi', 'Ґ':'G', 'є':'ye', 'і':'i', 'ї':'yi', 'ґ':'g'
}

var CZECH_MAP = {
	'č':'c', 'ď':'d', 'ě':'e', 'ň': 'n', 'ř':'r', 'š':'s', 'ť':'t', 'ů':'u',
	'ž':'z', 'Č':'C', 'Ď':'D', 'Ě':'E', 'Ň': 'N', 'Ř':'R', 'Š':'S', 'Ť':'T',
	'Ů':'U', 'Ž':'Z'
}

var POLISH_MAP = {
	'ą':'a', 'ć':'c', 'ę':'e', 'ł':'l', 'ń':'n', 'ó':'o', 'ś':'s', 'ź':'z',
	'ż':'z', 'Ą':'A', 'Ć':'C', 'Ę':'e', 'Ł':'L', 'Ń':'N', 'Ó':'o', 'Ś':'S',
	'Ź':'Z', 'Ż':'Z'
}

var LATVIAN_MAP = {
	'ā':'a', 'č':'c', 'ē':'e', 'ģ':'g', 'ī':'i', 'ķ':'k', 'ļ':'l', 'ņ':'n',
	'š':'s', 'ū':'u', 'ž':'z', 'Ā':'A', 'Č':'C', 'Ē':'E', 'Ģ':'G', 'Ī':'i',
	'Ķ':'k', 'Ļ':'L', 'Ņ':'N', 'Š':'S', 'Ū':'u', 'Ž':'Z'
}

var ALL_DOWNCODE_MAPS = new Array();
var streamsHoverTimeout = 0;
var networksHoverTimeout = 0;

ALL_DOWNCODE_MAPS[0] = LATIN_MAP
ALL_DOWNCODE_MAPS[1] = LATIN_SYMBOLS_MAP
ALL_DOWNCODE_MAPS[2] = GREEK_MAP
ALL_DOWNCODE_MAPS[3] = TURKISH_MAP
ALL_DOWNCODE_MAPS[4] = RUSSIAN_MAP
ALL_DOWNCODE_MAPS[5] = UKRAINIAN_MAP
ALL_DOWNCODE_MAPS[6] = CZECH_MAP
ALL_DOWNCODE_MAPS[7] = POLISH_MAP
ALL_DOWNCODE_MAPS[8] = LATVIAN_MAP

var Downcoder = new Object();
Downcoder.Initialize = function() {
	if (Downcoder.map) {
		return;
	}
	
	Downcoder.map ={}
	Downcoder.chars = '';
	
	for(var i in ALL_DOWNCODE_MAPS) {
		var lookup = ALL_DOWNCODE_MAPS[i]
		for (var c in lookup) {
			Downcoder.map[c] = lookup[c];
			Downcoder.chars += c;
		}
	}
	
	Downcoder.regex = new RegExp(
		'[' + Downcoder.chars + ']|[^' + Downcoder.chars + ']+','g'
	);
}

downcode = function(slug) {
	Downcoder.Initialize();
	var downcoded =""
	var pieces = slug.match(Downcoder.regex);
	if(pieces) {
		for (var i = 0; i < pieces.length; i++) {
			if (pieces[i].length == 1) {
				var mapped = Downcoder.map[pieces[i]];
				if (mapped != null) {
					downcoded+=mapped;
					continue;
				}
			}
			downcoded+=pieces[i];
		}
	} else {
		downcoded = slug;
	}
	return downcoded;
}

function URLify(s, num_chars) {
	s = downcode(s);
	removelist = ['a', 'an', 'as', 'at', 'before', 'but', 'by', 'for', 'from',
		'is', 'in', 'into', 'like', 'of', 'off', 'on', 'onto', 'per',
		'since', 'than', 'the', 'this', 'that', 'to', 'up', 'via', 'with'
	];
	r = new RegExp('\\b(' + removelist.join('|') + ')\\b', 'gi');
	s = s.replace(r, '');
	s = s.replace(/[^-\w\s]/g, '');
	s = s.replace(/^\s+|\s+$/g, '');
	s = s.replace(/[-\s]+/g, '');
	s = s.toLowerCase();
	return s.substring(0, num_chars);
}

$.fn.bindExternal = function() {
	$(this).attr('data-bound', 'true');
	
	$(this).find('.tweets[data-tag]').each(
		function() {
			var twitter = $(this);
			var tag = $(this).attr('data-tag');
			var sample = $(this).find('.post.sample');
			var tweet = null;
			var post = null;
			
			tag = '%23' + tag.split(',').join('%20OR%20%23')
			$.getJSON('http://search.twitter.com/search.json?q=' + tag +
				'&rpp=5&result_type=recent&callback=?',
				function(data) {
					for(var i = 0; i < data.results.length; i ++) {
						tweet = data.results[i];
						post = sample.clone().removeClass('sample');
						
						post.attr('id', 'tweet-' + tweet.id_str);
						post.find('.avatar').attr(
							'href', 'http://twitter.com/' + tweet.from_user
						).find('img').attr('src', tweet.profile_image_url);
						
						post.find('.username').attr(
							'href', 'http://twitter.com/' + tweet.from_user
						).attr('target', '_blank').html(tweet.from_user);
						
						var text = tweet.text.replace(
							/(ftp|http|https|file):\/\/[\S]+(\b|$)/gim, '<a href="$&" target="_blank">$&</a>'
						).replace(
							/@(\w+)/g, '@<a href="http://www.twitter.com/$1" target="_blank">$1</a>'
						).replace(
							/#(\w+)/g, '<a href="http://twitter.com/search/%23$1" target="_blank">#$1</a>'
						);
						
						post.find('.body').html(text);
						post.find('.date').attr(
							'href', 'http://twitter.com/' + tweet.from_user + '/statuses/' + tweet.id_str
						).attr('target', '_blank').html(
							timeSince(
								new Date(tweet.created_at)
							)
						);
						
						sample.before(post);
					}
					
					sample.remove();
					twitter.show();
				}
			);
		}
	);
	
	$(this).find('.flickr[data-tag]').each(
		function() {
			var flickr = $(this);
			var tag = $(this).attr('data-tag');
			var key = '9c7f7691c6af611084c6af4e9e2fd059';
			
			$.getJSON('http://api.flickr.com/services/rest/?' +
				'method=flickr.photos.search&format=json&extras=url_sq&per_page=12&' +
				'api_key=' + key + '&tags=' + tag + '&callback=?'
			);
		}
	);
}

$.fn.formDefaults = function() {
	$(this).closest('form').bind('submit',
		function(e) {
			$(this).find('input.initial').val('');
		}
	);
	
	var container = $(this);
	
	$(this).find('label').each(
		function() {
			var lbl = $(this);
			var labelText = lbl.text();
			
			if(lbl.find('input').size() == 0) {
				var input = container.find('input#' + lbl.attr('for'));
			} else {
				var input = lbl.find('input');
			}
			
			input.val(
				$(this).text()
			).addClass('initial').bind('focus',
				function(e) {
					if($(this).hasClass('initial')) {
						$(this).val('');
					}
				}
			).bind('blur',
				function(e) {
					if($(this).val() == '') {
						$(this).val(labelText);
						$(this).addClass('initial');
					}
				}
			).bind('keypress',
				function(e) {
					$(this).removeClass('initial');
				}
			);
			
			if(lbl.find('input').size() == 0) {
				lbl.text('');
			} else {
				lbl.replaceWith(input);
			}
		}
	);
};

function parseDate(date) {
	var split = date.split(' ');
	var datePart = split[0].split('-');
	var timePart = split[1].split(':');
	var year = datePart[0];
	var month = datePart[1];
	var day = datePart[2];
	var hour = timePart[0];
	var minute = timePart[1];
	var second = timePart[2];
	
	return new Date(
		year, month - 1, day,
		hour, minute, second
	);
}

function timeSince(date) {
	var diff = (((new Date()).getTime() - date.getTime()) / 1000);
	var day_diff = Math.floor(diff / 86400);
	
	if (isNaN(day_diff) || day_diff < 0 || day_diff >= 31) {
		return;
	}
	
	return day_diff == 0 && (
		diff < 60 && 'just now' ||
		diff < 120 && '1 minute ago' ||
		diff < 3600 && Math.floor(diff / 60) + ' minutes ago' ||
		diff < 7200 && 'an hour ago' ||
		diff < 86400 && Math.floor(diff / 3600) + ' hours ago'
	) || (
		day_diff == 1 && '1 day ago' ||
		day_diff < 7 && day_diff + ' days ago' ||
		day_diff < 31 && Math.ceil(day_diff / 7) + ' weeks ago'
	);
}

function jsonFlickrApi(rsp) {
	if (rsp.stat != 'ok') {
		return;
	}
	
	var photo = null;
	for(var i = 0; i < rsp.photos.photo.length; i ++) {
		photo = rsp.photos.photo[i];
		
		$('.flickr[data-tag]').append(
			'<a href="http://www.flickr.com/photos/' + photo.owner + '/' + photo.id + '" ' +
			'title="' + photo.title + '" target="_blank">' +
			'<img src="' + photo.url_sq + '" alt="' + photo.title + '" /></a>'
		);
	}
	
	$('.flickr[data-tag]').show();
}

$(document).ready(
	function() {
		$('.swap[data-swap-parent]').hide();
		$('a[data-swap]').bind('click',
			function(e) {
				e.preventDefault();
				
				var swap = $(this).attr('data-swap');
				$(this).closest('.module').fadeOut(
					function() {
						swap = $('.swap[data-swap="' + swap + '"]').not($(this));
						swap.fadeIn();
						swap.find('input:first').focus();
					}
				);
			}
		);
		
		$('header nav a.streams').bind('click',
			function(e) {
				var nav = $(this).closest('nav').find('nav.streams');
				
				nav.show();
				$.ajax(
					{
						url: '/streams.js',
						dataType: 'json',
						context: nav,
						success: function(data) {
							$(this).find('img').animate(
								{
									opacity: 0
								},
								function() {
									var nav = $(this).closest('nav');
									for(var i = 0; i < data.length; i ++) {
										nav.append(
											'<a href="' + data[i].url + '">' + data[i].name + '</a>'
										);
									}
									
									$(this).remove();
									nav.append(
										'<a class="create" href="/create/">Create a stream</a>'
									);
								}
							);
						},
						error: function() {
							alert('Error');
						}
					}
				);
			}
		);
		
		$('header nav a.streams, header nav nav.streams').hover(
			function(e) {
				if(streamsHoverTimeout > 0) {
					clearTimeout(streamsHoverTimeout);
				}
			},
			function(e) {
				streamsHoverTimeout = setTimeout(
					function() {
						$('nav nav.streams').hide();
					},
					300
				);
			}
		);
		
		$('header nav a.networks').bind('click',
			function(e) {
				var nav = $(this).closest('nav').find('nav.networks');
				
				nav.show();
				$.ajax(
					{
						url: '/networks.js',
						dataType: 'json',
						context: nav,
						success: function(data) {
							$(this).find('img').animate(
								{
									opacity: 0
								},
								function() {
									var nav = $(this).closest('nav');
									for(var i = 0; i < data.length; i ++) {
										nav.append(
											'<a href="http://' + data[i].domain + '">' + data[i].name + '</a>'
										);
									}
									
									$(this).remove();
									nav.append(
										'<a class="explore" href="/networks/">Explore networks</a>'
									);
								}
							);
						},
						error: function() {
							alert('Error');
						}
					}
				);
			}
		);
		
		$('header nav a.networks, header nav nav.networks').hover(
			function(e) {
				if(networksHoverTimeout > 0) {
					clearTimeout(networksHoverTimeout);
				}
			},
			function(e) {
				networksHoverTimeout = setTimeout(
					function() {
						$('nav nav.networks').hide();
					},
					300
				);
			}
		);
		
		$(window).resize(
			function() {
				if($('#sidebar').attr('data-bound') == undefined && $('#sidebar').is(':visible')) {
					$('#sidebar').bindExternal();
				}
			}
		);
		
		$('#sidebar:visible').bindExternal();
		
		function slideUpMessage() {
			setTimeout(
				function() {
					$('#messages .message:visible').not('.static').first().slideUp(
						slideUpMessage
					)	
				},
				3000
			);
		}
		
		slideUpMessage();
		
		$('.st_wordpress_button').attr('displayText', 'WordPress');
		$('.st_tumblr_button').attr('displayText', 'Tumblr');
		$('.st_blogger_button').attr('displayText', 'Blogger');
		$('.st_evernote_button').attr('displayText', 'Evernote');
		$('.st_email_button').attr('displayText', 'Email');
	}
);