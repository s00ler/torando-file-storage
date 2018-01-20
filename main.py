from server import Application

if __name__ == '__main__':
    app = Application()
    try:
        print('Server started')
        app.run()
    except KeyboardInterrupt:
        app.stop()
        print('Server stopped')
