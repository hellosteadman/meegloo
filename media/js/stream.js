timeoutInterval = 3000;
checkTimeout = null;

$(document).ready(
	function() {
		$('#mainstage .next-page').not('.no-ajax').html('Load more items').bind('click', nextPageLink);
	}
);

function organiseItems(data) {
	var objects = $('<div id="latest-' + latest_id + '">' + data + '</div>');
	var sets = objects.find('section.set[data-id]');
	var articles = objects.find('article.post[data-set]');
	var paginator = objects.find('a.next-page');
	
	if(articles.size() > 0) {
		$('.wait').fadeOut();
		timeoutInterval = 3000;
	} else {
		timeoutInterval += 3000;
		
		try {
			console.log('No new items. Waiting for ' + (timeoutInterval / 1000) + ' seconds');
		} catch (err) { }
	}
	
	articles.each(
		function() {
			var setID = $(this).attr('data-set');
			var setElement = $('#mainstage .posts .set[data-id=' + setID + ']');
			var common = $('#mainstage .posts .post[data-set=' + setID + ']');
			var firstMeta = null;
			var kind = null;
			
			$(this).hide().css('opacity', 0);
			
			if(setElement.size() > 0) {
				try {
					console.log('Found set ' + setID + ' to put articles in');
				} catch (err) { }
				
				setElement.prepend($(this));
				firstMeta = setElement.find('.post-meta').first().html();
				setElement.find('.post-meta').remove();
				setElement.append('<div class="post-meta">' + firstMeta + '</div>');
				setElement.append('<div class="clear"></div>');
			} else if(common.size() > 0) {
				kind = common.first().attr('data-kind');
				try {
					console.log('Found common article(s) in set ' + setID);
				} catch (err) { }
				
				setElement = $('<section class="set ' + kind + '-set" id="set-' + setID + '" data-id="' + setID + '"></section>');
				setElement.append(common);
				setElement.prepend($(this));
				
				firstMeta = setElement.find('.post-meta').first().html();
				setElement.find('.post-meta').remove();
				setElement.append('<div class="post-meta">' + firstMeta + '</div>');
				setElement.append('<div class="clear"></div>');
				
				if(setElement.hasClass('photo-set')) {
					setElement.find('p').remove();
				}
				
				$('#mainstage .posts').prepend(setElement);
			} else {
				try {
					console.log('No object for set ' + setID);
				} catch (err) { }
				$('#mainstage .posts').prepend($(this));
			}
			
			$(this).slideDown().animate(
				{
					opacity: 1
				}
			);
		}
	);
	
	$('#mainstage .posts').append(paginator);
	$('#mainstage span.date').each(
		function() {
			var date = $(this).attr('data-date');
			
			if(date) {
				date = parseDate(date);
				if(date) {
					date = timeSince(date);
					$(this).html(date);
				}
			}
		}
	);
}

function nextPageLink(e) {
	e.preventDefault();
	
	$.ajax(
		{
			url: $(this).attr('href'),
			context: $(this),
			dataType: 'html',
			success: function(data) {
				$(this).remove();
				$('#mainstage .posts').append(data);
				$('#mainstage .next-page').html('Load more items').bind('click', nextPageLink);
				
				$.ajax(
					{
						url: $(this).attr('href'),
						dataType: 'script'
					}
				);
			}
		}
	);
}

function checkLatest() {
	$.ajax(
		{
			url: '?since=' + latest_id,
			dataType: 'html',
			success: function(data) {
				organiseItems(data);
				
				$.ajax(
					{
						url: '?since=' + latest_id,
						dataType: 'script'
					}
				);
				
				clearTimeout(checkTimeout);
				checkTimeout = setTimeout(checkLatest, timeoutInterval);
			}
		}
	);
}