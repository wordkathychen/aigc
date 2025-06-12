"""
错误处理模块
定义全局错误处理函数
"""

from flask import render_template, jsonify, request

def register_error_handlers(app):
    """注册全局错误处理函数"""
    
    @app.errorhandler(400)
    def bad_request(error):
        """处理400错误"""
        if request.is_json or request.path.startswith('/api/'):
            return jsonify(error=str(error), message="请求参数错误"), 400
        return render_template('errors/400.html', error=error), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """处理401错误"""
        if request.is_json or request.path.startswith('/api/'):
            return jsonify(error="unauthorized", message="未授权访问"), 401
        return render_template('errors/401.html', error=error), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """处理403错误"""
        if request.is_json or request.path.startswith('/api/'):
            return jsonify(error="forbidden", message="禁止访问"), 403
        return render_template('errors/403.html', error=error), 403
    
    @app.errorhandler(404)
    def page_not_found(error):
        """处理404错误"""
        if request.is_json or request.path.startswith('/api/'):
            return jsonify(error="not_found", message="资源不存在"), 404
        return render_template('errors/404.html', error=error), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """处理405错误"""
        if request.is_json or request.path.startswith('/api/'):
            return jsonify(error="method_not_allowed", message="不允许的请求方法"), 405
        return render_template('errors/405.html', error=error), 405
    
    @app.errorhandler(429)
    def too_many_requests(error):
        """处理429错误"""
        if request.is_json or request.path.startswith('/api/'):
            return jsonify(error="too_many_requests", message="请求过于频繁"), 429
        return render_template('errors/429.html', error=error), 429
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """处理500错误"""
        if request.is_json or request.path.startswith('/api/'):
            return jsonify(error="internal_server_error", message="服务器内部错误"), 500
        return render_template('errors/500.html', error=error), 500 