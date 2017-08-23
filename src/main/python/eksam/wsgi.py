from itsdangerous import JSONWebSignatureSerializer


def configure(app, db, config):
    if config['<db-location>'] == ':memory:':
        db.bind(provider='sqlite', filename=':memory:')
    else:
        db.bind(provider='sqlite',
                filename=config['<db-location>'],
                create_db=True)

    db.generate_mapping(create_tables=True)

    app.signer = JSONWebSignatureSerializer(config['--secret'])
    app.test_time_seconds = int(config['--test-time'])

    return app
