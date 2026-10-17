import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mangum import Mangum
from video_server import app

handler = Mangum(app)
