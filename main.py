from sanic import Sanic
from views.chatglm_p import chatglm_p
from views.chatglm_l import chatglm_l
from views.sd import stable_diffusion_bp
from views.moss import moss_bp

app = Sanic(__name__)
app.blueprint(chatglm_p)
app.blueprint(chatglm_l)
app.blueprint(stable_diffusion_bp)
app.blueprint(moss_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
