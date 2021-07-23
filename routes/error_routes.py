
def bind(flask_app):
    
    @flask_app.errorhandler(403)
    def forbidden(error):
        return error, 403