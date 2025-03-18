from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
        use_reloader=True,
        extra_files=[
            'app/templates/base.html',
            'app/modules/file_manager/templates/index.html',
            'app/modules/time_calculator/templates/time_calculator.html',
            'app/static/css/style.css',
        ],
    )
