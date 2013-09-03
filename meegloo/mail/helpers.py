from datetime import datetime
from uuid import uuid4
from os import path

def upload_section_image(instance, filename):
	return 'mail/%s/%s%s' % (
		datetime.now().strftime('%Y/%m'),
		str(uuid4()),
		path.splitext(filename)[-1]
	)