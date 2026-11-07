# Check local geographic aggregates and logo transparency without mutating application data.
import json
from PIL import Image
from decimal import Decimal
data = json.load(open('/app/frontend/src/assets/world-activity.json'))
countries = data['countries']
views = sum(c['views'] for c in countries)
weighted = sum(Decimal(str(c['cpvv'])) * c['views'] for c in countries)
print('Regions:', len(countries), 'Pixels:', len(data['points']))
print('Total views:', views, 'Weighted spend:', weighted, 'Rendered all-region spend:', Decimal('.024') * views)
print('Pixel sums:', sum(p[3] for p in data['points']), sum(p[4] for p in data['points']))
print('Country sums:', views, sum(c['clicks'] for c in countries))
image = Image.open('/app/frontend/public/brand/meantime-mark.png').convert('RGBA')
print('Logo corners:', [image.getpixel(p) for p in [(0, 0), (image.width-1, 0), (0, image.height-1), (image.width-1, image.height-1)]])