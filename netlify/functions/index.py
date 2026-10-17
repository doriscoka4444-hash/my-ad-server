import sys
import os

func_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, func_dir)
root_dir = os.path.dirname(os.path.dirname(func_dir))
sys.path.insert(0, root_dir)

from mangum import Mangum
from video_server import app

handler = Mangum(app, api_gateway_base_path="/.netlify/functions/index")
