from sanic import Sanic
from views.origin import origin_bp
from views.sd import stable_diffusion_bp
from views.moss import moss_bp

app = Sanic(__name__)
app.blueprint(origin_bp)
app.blueprint(stable_diffusion_bp)
app.blueprint(moss_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
