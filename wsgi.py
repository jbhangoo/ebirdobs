import sys
path = '/home/jbhangoo/mysite'
if path not in sys.path:
   sys.path.insert(0, path)

from app import app

if __name__ == "__main__":
    app.run(debug=False)
